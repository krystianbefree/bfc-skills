"""
Serwer panelu - FastAPI.

Serwuje interfejs i kontrakt danych, przyjmuje akcje zapisujące. Wszystko chodzi
lokalnie na 127.0.0.1: klucze API zostają po stronie serwera i nigdy nie trafiają
do przeglądarki ani do sejfu Obsidiana.

Uruchomienie:
    bash panel.sh
    # albo
    .venv/bin/uvicorn engine.app:app --host 127.0.0.1 --port 8765
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import asyncio
import json
import os

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel

from engine import chat as chat_mod
from engine import notifications as notif
from engine import terminal as term
from engine import timer as timer_mod
from engine.adapters import klienci, pozyskiwanie, tresci
from engine.build import build
from engine.cache import clear_cache
from engine.config import load_config, reload_config

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Panel dowodzenia", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_TERMINALS: "set" = set()
_NOTIF_TASK: Optional["asyncio.Task"] = None


@app.on_event("startup")
async def _start_notifications() -> None:
    """Odpala pętlę powiadomień push, jeśli włączona w configu."""
    global _NOTIF_TASK
    try:
        cfg = load_config()
        if not cfg.get("notifications.enabled", False):
            return
        interval = int(cfg.get("notifications.interval_minutes", 30) or 30)
        if not notif.PLATFORM_IS_MAC:
            logger.info("Powiadomienia włączone, ale platforma nie-macOS - no-op.")
        _NOTIF_TASK = asyncio.create_task(notif.run_loop(interval))
        logger.info(f"Powiadomienia push aktywne (co {interval} min).")
    except Exception as exc:  # noqa: BLE001 - powiadomienia nie mogą zablokować startu
        logger.warning(f"Powiadomienia: nie wystartowały: {exc}")


@app.on_event("shutdown")
async def _stop_notifications() -> None:
    if _NOTIF_TASK is not None:
        _NOTIF_TASK.cancel()


@app.on_event("shutdown")
def _close_terminals() -> None:
    for session in list(_TERMINALS):
        session.stop()
    _TERMINALS.clear()


# ── modele wejścia ────────────────────────────────────────────────────────
class TaskStatusIn(BaseModel):
    file: str        # ścieżka pliku klienta/biznesu względem sejfu
    key: str
    done: bool = True


class TaskAddIn(BaseModel):
    file: str
    text: str


class QueueStatusIn(BaseModel):
    key: str
    stage: str
    note: str = ""


class QueueAddIn(BaseModel):
    title: str
    stage: str = ""
    note: str = ""
    value: str = ""


class TimerStartIn(BaseModel):
    mode: str = ""
    task_key: str = ""
    task_text: str = ""
    projekt: str = ""
    minutes: Optional[int] = None


class ContentStatusIn(BaseModel):
    key: str
    status: str


def _sejf_file(cfg, relative: str) -> Path:
    """Rozwiązuje ścieżkę pliku w sejfie i pilnuje, by nie wyszła poza sejf."""
    sejf = cfg.sejf.resolve()
    target = (sejf / relative).resolve()
    if sejf not in target.parents and target != sejf:
        raise HTTPException(status_code=400, detail="Ścieżka poza sejfem.")
    return target


# ── interfejs ─────────────────────────────────────────────────────────────
@app.get("/")
def index() -> FileResponse:
    # no-store: HTML zawsze świeży, żeby po aktualizacji panelu nie wisiała
    # stara wersja z cache przeglądarki (statyki wersjonowane przez ?v=).
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/data")
def api_data(force: bool = False) -> JSONResponse:
    """Kontrakt danych. `?force=1` omija cache zewnętrznych źródeł."""
    return JSONResponse(build(force=force))


@app.post("/api/reload")
def api_reload() -> Dict[str, Any]:
    """Przeładowuje config i czyści cache - po ręcznej zmianie configu."""
    clear_cache()
    reload_config()
    return {"ok": True}


# ── akcje zapisujące ──────────────────────────────────────────────────────
@app.post("/api/task/status")
def api_task_status(payload: TaskStatusIn) -> Dict[str, Any]:
    """Odhacza to-do w pliku klienta albo własnego biznesu (jedna linia)."""
    cfg = load_config()
    path = _sejf_file(cfg, payload.file)
    try:
        result = klienci.set_task_status(path, payload.key, payload.done)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(f"To-do '{result['text'][:60]}' -> done={payload.done} ({payload.file})")
    return {"ok": True, "task": result}


@app.post("/api/task/add")
def api_task_add(payload: TaskAddIn) -> Dict[str, Any]:
    """Dopisuje to-do do pliku klienta/biznesu."""
    cfg = load_config()
    path = _sejf_file(cfg, payload.file)
    try:
        result = klienci.add_task(path, payload.text)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(f"Nowe to-do: {result['text'][:60]} ({payload.file})")
    return {"ok": True, "task": result}


@app.post("/api/queue/status")
def api_queue_status(payload: QueueStatusIn) -> Dict[str, Any]:
    """Przenosi firmę między etapami lejka."""
    cfg = load_config()
    path = cfg.sejf_path(cfg.get("sources.pozyskiwanie.file", "Pozyskiwanie.md"))
    try:
        item = pozyskiwanie.set_status(path, payload.key, payload.stage, payload.note)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(f"Lejek: '{item['title'][:60]}' -> {payload.stage}")
    return {"ok": True, "item": item}


@app.post("/api/queue/add")
def api_queue_add(payload: QueueAddIn) -> Dict[str, Any]:
    """Dopisuje firmę do lejka."""
    cfg = load_config()
    path = cfg.sejf_path(cfg.get("sources.pozyskiwanie.file", "Pozyskiwanie.md"))
    try:
        item = pozyskiwanie.add_item(
            path, title=payload.title, stage=payload.stage,
            note=payload.note, value=payload.value,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(f"Nowa firma w lejku: {item['title'][:60]}")
    return {"ok": True, "item": item}


@app.post("/api/timer/start")
def api_timer_start(payload: TimerStartIn) -> Dict[str, Any]:
    """Odpala sesję timera (pomodoro/stoper). Stan trzyma serwer."""
    cfg = load_config()
    session = timer_mod.start(
        cfg, mode=payload.mode, task_key=payload.task_key,
        task_text=payload.task_text, projekt=payload.projekt, minutes=payload.minutes,
    )
    logger.info(f"Timer start: {session.get('mode')} · {session.get('task_text') or '-'}")
    return {"ok": True, "running": session}


@app.post("/api/timer/stop")
def api_timer_stop() -> Dict[str, Any]:
    """Zamyka bieżącą sesję i dopisuje ją do logu czasu."""
    cfg = load_config()
    entry = timer_mod.stop(cfg)
    return {"ok": True, "entry": entry}


@app.post("/api/content/status")
def api_content_status(payload: ContentStatusIn) -> Dict[str, Any]:
    """Przenosi pomysł/treść między etapami (podmienia linię Status: w pliku)."""
    cfg = load_config()
    path = cfg.sejf_path(cfg.get("sources.tresci.file", "Do nagrania.md"))
    try:
        result = tresci.set_status(path, payload.key, payload.status)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(f"Content: {payload.key} -> {result['status']}")
    return {"ok": True, "item": result}


@app.get("/api/health")
def api_health() -> Dict[str, Any]:
    """Lekki endpoint do sprawdzenia, czy serwer żyje."""
    return {"ok": True}


# ── czat ──────────────────────────────────────────────────────────────────
@app.get("/api/chat/info")
def api_chat_info() -> Dict[str, Any]:
    return chat_mod.describe(load_config())


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket) -> None:
    cfg = load_config()
    port = int(os.getenv("DASHBOARD_PORT", "8765"))

    info = chat_mod.describe(cfg)
    if not info.get("enabled"):
        await ws.close(code=1008, reason=info.get("reason", "Czat wyłączony"))
        return

    if not term.origin_allowed(ws.headers.get("origin"), cfg, port):
        logger.warning(f"Czat: odrzucone połączenie z origin={ws.headers.get('origin')!r}")
        await ws.close(code=1008, reason="Niedozwolone źródło połączenia")
        return

    await ws.accept()
    session_id: Optional[str] = None
    busy = False

    try:
        while True:
            raw = await ws.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if message.get("type") == "reset":
                session_id = None
                await ws.send_json({"type": "reset_ok"})
                continue

            if message.get("type") != "message":
                continue

            prompt = (message.get("text") or "").strip()
            if not prompt:
                continue
            if busy:
                await ws.send_json({"type": "error", "text": "Poprzednia odpowiedź jeszcze leci."})
                continue

            busy = True
            await ws.send_json({"type": "start"})
            try:
                async for event in chat_mod.run_turn(cfg, prompt, session_id):
                    if event.get("session_id"):
                        session_id = event["session_id"]
                    await ws.send_json(event)
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Czat: tura padła: {exc}")
                await ws.send_json({"type": "error", "text": str(exc)[:400]})
            finally:
                busy = False
                await ws.send_json({"type": "idle"})
    except WebSocketDisconnect:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Czat: połączenie przerwane: {exc}")


# ── terminal ──────────────────────────────────────────────────────────────
@app.get("/api/terminal/info")
def api_terminal_info() -> Dict[str, Any]:
    cfg = load_config()
    if not cfg.get("terminal.enabled", False):
        return {"enabled": False, "reason": "Terminal wyłączony w dashboard.config.yaml"}
    try:
        command = term.resolve_command(cfg)
    except RuntimeError as exc:
        return {"enabled": False, "reason": str(exc)}
    return {
        "enabled": True,
        "command": " ".join(command),
        "cwd": str(term.default_cwd(cfg)),
    }


@app.websocket("/ws/terminal")
async def ws_terminal(ws: WebSocket) -> None:
    cfg = load_config()
    port = int(os.getenv("DASHBOARD_PORT", "8765"))

    if not cfg.get("terminal.enabled", False):
        await ws.close(code=1008, reason="Terminal wyłączony w configu")
        return

    origin = ws.headers.get("origin")
    if not term.origin_allowed(origin, cfg, port):
        logger.warning(f"Terminal: odrzucone połączenie z origin={origin!r}")
        await ws.close(code=1008, reason="Niedozwolone źródło połączenia")
        return

    try:
        command = term.resolve_command(cfg)
    except RuntimeError as exc:
        await ws.accept()
        await ws.send_text(f"\r\n\x1b[31m{exc}\x1b[0m\r\n")
        await ws.close()
        return

    await ws.accept()
    session = term.TerminalSession(command, term.default_cwd(cfg), env=term.child_env(cfg))
    session.start()
    _TERMINALS.add(session)

    async def send(text: str) -> None:
        await ws.send_text(text)

    pump = asyncio.create_task(term.pump_output(session, send))

    try:
        while True:
            raw = await ws.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if message.get("type") == "input":
                session.write(message.get("data", ""))
            elif message.get("type") == "resize":
                session.resize(int(message.get("rows", 30)), int(message.get("cols", 100)))
    except WebSocketDisconnect:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Terminal: połączenie przerwane: {exc}")
    finally:
        pump.cancel()
        session.stop()
        _TERMINALS.discard(session)
