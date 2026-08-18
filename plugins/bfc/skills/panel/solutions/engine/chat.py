"""
Czat z Claude Code wewnątrz panelu.

Każda wiadomość odpala `claude -p` ze strumieniowym wyjściem JSON, a odpowiedź
leci do przeglądarki token po tokenie. Ciągłość rozmowy trzyma `--session-id`
przy pierwszej wiadomości i `--resume` przy kolejnych.

Uprawnienia: w trybie nieinteraktywnym nie ma gdzie wyświetlić pytania „czy
mogę", więc zakres jest ustalany z góry w `dashboard.config.yaml` i pokazywany
w interfejsie.
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

from loguru import logger

from engine.config import Config
from engine.terminal import child_env, default_cwd, resolve_command

_ARG_PREVIEW = 90


def build_args(cfg: Config, prompt: str, session_id: Optional[str]) -> List[str]:
    """Składa wywołanie CLI. Nic z przeglądarki nie trafia poza `prompt`."""
    args = list(resolve_command(cfg))
    args += [
        "-p",
        prompt,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
    ]

    if session_id:
        args += ["--resume", session_id]
    else:
        args += ["--session-id", str(uuid.uuid4())]

    mode = cfg.get("chat.permission_mode", "acceptEdits")
    if mode:
        args += ["--permission-mode", str(mode)]

    allowed = cfg.get("chat.allowed_tools") or []
    if allowed:
        args += ["--allowedTools", *[str(t) for t in allowed]]

    disallowed = cfg.get("chat.disallowed_tools") or []
    if disallowed:
        args += ["--disallowedTools", *[str(t) for t in disallowed]]

    model = cfg.get("chat.model")
    if model:
        args += ["--model", str(model)]

    system = cfg.get("chat.system_prompt")
    if system:
        args += ["--append-system-prompt", str(system)]

    return args


def _preview(tool: str, payload: Dict[str, Any]) -> str:
    """Jedna czytelna linijka opisująca użycie narzędzia."""
    for key in ("file_path", "path", "pattern", "command", "query", "url", "prompt"):
        value = payload.get(key)
        if value:
            text = str(value).replace("\n", " ").strip()
            return text[:_ARG_PREVIEW] + ("…" if len(text) > _ARG_PREVIEW else "")
    return ""


async def run_turn(cfg: Config, prompt: str, session_id: Optional[str]) -> AsyncIterator[Dict[str, Any]]:
    """Odpala jedną turę rozmowy i zwraca zdarzenia gotowe do wysłania na WebSocket."""
    args = build_args(cfg, prompt, session_id)
    cwd: Path = default_cwd(cfg)

    env = child_env(cfg)
    env["TERM"] = "dumb"

    logger.info(f"Czat: {'wznawiam' if session_id else 'nowa sesja'}, prompt {len(prompt)} zn.")

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd),
        env=env,
    )

    saw_output = False
    try:
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            raw = line.decode("utf-8", errors="replace").strip()
            if not raw:
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue

            for out in _translate(event):
                saw_output = True
                yield out
    finally:
        stderr = b""
        if proc.stderr is not None:
            try:
                stderr = await asyncio.wait_for(proc.stderr.read(), timeout=2)
            except asyncio.TimeoutError:
                stderr = b""
        code = await proc.wait()
        if code != 0 and not saw_output:
            message = stderr.decode("utf-8", errors="replace").strip() or f"CLI zakończyło się kodem {code}"
            yield {"type": "error", "text": message[:600]}


def _translate(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Zamienia zdarzenie ze stream-json na coś, co interfejs umie narysować."""
    kind = event.get("type")

    if kind == "rate_limit_event":
        info = event.get("rate_limit_info") or {}
        return [{
            "type": "limit",
            "status": info.get("status"),
            "window": info.get("rateLimitType"),
            "resets_at": info.get("resetsAt"),
            "using_overage": bool(info.get("isUsingOverage")),
        }]

    if kind == "system" and event.get("subtype") == "init":
        return [{
            "type": "session",
            "session_id": event.get("session_id"),
            "model": event.get("model"),
            "tools": len(event.get("tools") or []),
        }]

    if kind == "stream_event":
        inner = event.get("event") or {}
        if inner.get("type") == "content_block_delta":
            delta = inner.get("delta") or {}
            if delta.get("type") == "text_delta" and delta.get("text"):
                return [{"type": "delta", "text": delta["text"]}]
        return []

    if kind == "assistant":
        out: List[Dict[str, Any]] = []
        for block in (event.get("message") or {}).get("content") or []:
            if block.get("type") == "tool_use":
                out.append({
                    "type": "tool",
                    "name": block.get("name", "narzędzie"),
                    "detail": _preview(block.get("name", ""), block.get("input") or {}),
                })
        return out

    if kind == "result":
        return [{
            "type": "done",
            "session_id": event.get("session_id"),
            "text": event.get("result") or "",
            "is_error": bool(event.get("is_error")),
            "cost_usd": event.get("total_cost_usd"),
            "duration_ms": event.get("duration_ms"),
        }]

    return []


def describe(cfg: Config) -> Dict[str, Any]:
    """Opis konfiguracji czatu dla interfejsu - żeby zakres uprawnień był widoczny."""
    try:
        command = resolve_command(cfg)
    except RuntimeError as exc:
        return {"enabled": False, "reason": str(exc)}

    if not cfg.get("chat.enabled", True):
        return {"enabled": False, "reason": "Czat wyłączony w dashboard.config.yaml"}

    return {
        "enabled": True,
        "command": Path(command[0]).name,
        "cwd": str(default_cwd(cfg)),
        "permission_mode": cfg.get("chat.permission_mode", "acceptEdits"),
        "allowed_tools": cfg.get("chat.allowed_tools") or [],
        "disallowed_tools": cfg.get("chat.disallowed_tools") or [],
    }
