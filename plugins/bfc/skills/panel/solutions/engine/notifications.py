"""
Powiadomienia push (macOS) o nowych sygnałach `alarm`.

Zadanie w tle co `notifications.interval_minutes` przelicza sygnały panelu i dla
KAŻDEGO nowego sygnału `severity=alarm` (którego wcześniej nie widziało) odpala
natywne powiadomienie macOS przez `osascript`. Dedup po id sygnału - widziane
id leżą w `DATA_DIR/notifications_seen.json`.

Zasady twardości:
  * nie-macOS -> no-op + log (żadnych powiadomień),
  * błąd powiadomienia albo przeliczenia NIGDY nie kładzie serwera,
  * klucze API nie dotykają tego modułu - działa wyłącznie na gotowych sygnałach.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Set

from loguru import logger

from engine.config import DATA_DIR

PLATFORM_IS_MAC = sys.platform == "darwin"
_SEEN_PATH = DATA_DIR / "notifications_seen.json"
_APP_TITLE = "Panel"


# ── trwały stan widzianych sygnałów ───────────────────────────────────────
def _load_seen() -> Set[str]:
    try:
        if _SEEN_PATH.exists():
            raw = json.loads(_SEEN_PATH.read_text(encoding="utf-8"))
            return set(raw.get("seen", []))
    except Exception as exc:  # noqa: BLE001 - brudny plik nie może nas zatrzymać
        logger.warning(f"Powiadomienia: nie odczytałem widzianych id ({exc}), startuję od zera.")
    return set()


def _save_seen(seen: Set[str]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _SEEN_PATH.with_suffix(".tmp")
        payload = {"seen": sorted(seen), "updated_at": datetime.now().isoformat(timespec="seconds")}
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_SEEN_PATH)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Powiadomienia: nie zapisałem widzianych id: {exc}")


# ── natywne powiadomienie macOS ───────────────────────────────────────────
def _osa_escape(text: str) -> str:
    """Escapuje tekst do wnętrza podwójnych cudzysłowów w AppleScript."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def send_macos_notification(title: str, text: str) -> bool:
    """Odpala jedno natywne powiadomienie. Błąd -> False, nigdy wyjątek."""
    if not PLATFORM_IS_MAC:
        logger.info(f"Powiadomienia: nie-macOS, pomijam ({title}: {text}).")
        return False
    script = f'display notification "{_osa_escape(text)}" with title "{_osa_escape(title)}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True,
                       capture_output=True, timeout=10)
        return True
    except Exception as exc:  # noqa: BLE001 - powiadomienie nie może położyć serwera
        logger.warning(f"Powiadomienia: osascript padł: {exc}")
        return False


# ── jeden przebieg: policz sygnały, powiadom o nowych alarmach ────────────
def check_and_notify() -> Dict[str, Any]:
    """
    Jeden tick. Buduje sygnały, znajduje nowe alarmy, odpala powiadomienia i
    dopisuje ich id do widzianych. Nigdy nie rzuca wyjątkiem - zwraca podsumowanie.
    """
    from engine.build import build  # import leniwy - unikamy cyklu na starcie

    result: Dict[str, Any] = {"platform_mac": PLATFORM_IS_MAC, "new": [], "notified": 0}
    try:
        payload = build(force=False)
        alarms: List[Dict[str, Any]] = [
            s for s in payload.get("signals", []) if s.get("severity") == "alarm"
        ]
    except Exception as exc:  # noqa: BLE001 - błąd przeliczenia nie kładzie pętli
        logger.warning(f"Powiadomienia: nie policzyłem sygnałów: {exc}")
        result["error"] = str(exc)
        return result

    seen = _load_seen()
    current_ids = {s["id"] for s in alarms}
    new_alarms = [s for s in alarms if s["id"] not in seen]

    for sig in new_alarms:
        title = _APP_TITLE
        text = sig.get("title") or "Nowy alarm"
        if send_macos_notification(title, text):
            result["notified"] += 1
        result["new"].append(sig["id"])
        seen.add(sig["id"])

    # Sprzątanie: nie trzymamy w nieskończoność id, których już nie ma w sygnałach,
    # ale zostawiamy te wciąż aktywne, żeby nie powiadamiać o nich ponownie.
    seen = {sid for sid in seen if sid in current_ids}
    _save_seen(seen)

    if new_alarms:
        logger.info(f"Powiadomienia: {result['notified']}/{len(new_alarms)} nowych alarmów.")
    return result


# ── pętla w tle ────────────────────────────────────────────────────────────
async def run_loop(interval_minutes: int) -> None:
    """Pętla w tle. Odporna na wyjątki, kończy się dopiero przy cancel()."""
    interval = max(1, int(interval_minutes or 30))
    if not PLATFORM_IS_MAC:
        logger.info("Powiadomienia: platforma nie-macOS - pętla działa jako no-op.")
    logger.info(f"Powiadomienia: pętla wystartowała (co {interval} min).")
    try:
        while True:
            try:
                await asyncio.to_thread(check_and_notify)
            except Exception as exc:  # noqa: BLE001 - żaden tick nie kładzie serwera
                logger.warning(f"Powiadomienia: tick padł: {exc}")
            await asyncio.sleep(interval * 60)
    except asyncio.CancelledError:  # pragma: no cover - normalne zamknięcie serwera
        logger.info("Powiadomienia: pętla zatrzymana.")
        raise
