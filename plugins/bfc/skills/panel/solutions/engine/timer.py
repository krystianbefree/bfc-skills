"""
Timer pracy — stoper albo pomodoro, z logiem czasu na zadanie i klienta.

Stan biegnącej sesji trzyma serwer, nie przeglądarka. Dzięki temu odświeżenie
karty ani przejście na telefon nie gubi licznika: front pyta o `started_at`
i sam sobie tyka.

Zamknięta sesja dopisuje się do `time_log.json`. To jest telemetria, nie
notatka, więc świadomie nie ląduje w sejfie Obsidiana — w panelu widać z niej
podsumowania, a te trafiają potem do wyceny („ten klient zjadł 22 godziny przy
stawce liczonej na 8"). Pliki stanu i logu leżą w DATA_DIR silnika, poza sejfem.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.config import DATA_DIR, Config

MODE_POMODORO = "pomodoro"
MODE_STOPER = "stoper"
MODES = (MODE_POMODORO, MODE_STOPER)

# Sesje krótsze niż to nie trafiają do logu — to zwykle pomyłkowe kliknięcie.
_MIN_SECONDS = 20


def _state_path(cfg: Config) -> Path:
    return DATA_DIR / "timer_state.json"


def _log_path(cfg: Config) -> Path:
    return DATA_DIR / "time_log.json"


def _read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def running(cfg: Config) -> Optional[Dict[str, Any]]:
    """Sesja w biegu albo None."""
    state = _read_json(_state_path(cfg), None)
    return state if isinstance(state, dict) and state.get("started_at") else None


def start(cfg: Config, mode: str = "", task_key: str = "", task_text: str = "",
          projekt: str = "", minutes: Optional[int] = None) -> Dict[str, Any]:
    """Odpala sesję. Jeśli inna trwa, zamyka ją najpierw — dwa liczniki naraz
    zawsze kończą się nieprawdziwym logiem."""
    previous = running(cfg)
    if previous:
        stop(cfg)

    mode = mode if mode in MODES else str(cfg.get("timer.default_mode", MODE_POMODORO))
    if mode not in MODES:
        mode = MODE_POMODORO

    planned = minutes if minutes else int(cfg.get("timer.pomodoro_minutes", 25))

    session = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "task_key": task_key or None,
        "task_text": task_text or None,
        "projekt": projekt or None,
        # Stoper leci bez końca, pomodoro ma zaplanowaną długość.
        "planned_minutes": planned if mode == MODE_POMODORO else None,
    }
    _write_json(_state_path(cfg), session)
    return session


def stop(cfg: Config) -> Optional[Dict[str, Any]]:
    """Zamyka sesję i dopisuje ją do logu. Zwraca zapisany wpis albo None."""
    session = running(cfg)
    _write_json(_state_path(cfg), {})
    if not session:
        return None

    try:
        started = datetime.fromisoformat(session["started_at"])
    except (ValueError, KeyError):
        return None

    seconds = int((datetime.now() - started).total_seconds())
    if seconds < _MIN_SECONDS:
        return None

    entry = {
        "start": session["started_at"],
        "end": datetime.now().isoformat(timespec="seconds"),
        "seconds": seconds,
        "mode": session.get("mode"),
        "task_key": session.get("task_key"),
        "task_text": session.get("task_text"),
        "projekt": session.get("projekt"),
    }

    log: List[Dict[str, Any]] = _read_json(_log_path(cfg), [])
    if not isinstance(log, list):
        log = []
    log.append(entry)
    _write_json(_log_path(cfg), log)
    return entry


def entries(cfg: Config) -> List[Dict[str, Any]]:
    log = _read_json(_log_path(cfg), [])
    return log if isinstance(log, list) else []


def summary(cfg: Config) -> Dict[str, Any]:
    """Podsumowania, z których realnie się korzysta: dziś, ten tydzień
    i rozbicie na projekty — czyli materiał do wyceny."""
    log = entries(cfg)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    today_seconds = 0
    week_seconds = 0
    per_project: Dict[str, int] = {}
    per_task: Dict[str, Dict[str, Any]] = {}

    for item in log:
        try:
            started = datetime.fromisoformat(item["start"]).date()
        except (ValueError, KeyError, TypeError):
            continue
        seconds = int(item.get("seconds") or 0)

        if started == today:
            today_seconds += seconds
        if started >= week_start:
            week_seconds += seconds
            key = item.get("projekt") or "bez projektu"
            per_project[key] = per_project.get(key, 0) + seconds

        task_key = item.get("task_key")
        if task_key:
            bucket = per_task.setdefault(task_key, {"seconds": 0, "text": item.get("task_text")})
            bucket["seconds"] += seconds

    projects = [{"projekt": k, "seconds": v} for k, v in per_project.items()]
    projects.sort(key=lambda p: -p["seconds"])

    # Dziennik dzisiejszych sesji — widać, na co poszedł dzień, a nie tylko ile.
    today_entries = [i for i in log if str(i.get("start", ""))[:10] == today.isoformat()]
    today_entries.reverse()

    tasks = [
        {"key": key, "text": value.get("text") or "bez zadania", "seconds": value["seconds"]}
        for key, value in per_task.items()
    ]
    tasks.sort(key=lambda t: -t["seconds"])

    return {
        "today_seconds": today_seconds,
        "week_seconds": week_seconds,
        "sessions_today": len(today_entries),
        "today_entries": today_entries[:20],
        "per_project_week": projects,
        "per_task": per_task,
        "top_tasks": tasks[:12],
        "total_entries": len(log),
    }
