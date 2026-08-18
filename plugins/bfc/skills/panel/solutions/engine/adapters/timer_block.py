"""
Adapter timera — stan biegnącej sesji plus podsumowania czasu.

Sam licznik tyka we froncie, tutaj oddajemy tylko punkt startu i zsumowany
czas. Dzięki temu odświeżenie strony nie gubi sesji, a panel na telefonie
pokazuje ten sam licznik, co panel na kompie.
"""
from __future__ import annotations

from datetime import datetime

from engine import timer
from engine.config import Config
from engine.schema import Block


def fetch(cfg: Config) -> Block:
    session = timer.running(cfg)
    data = {
        "enabled": True,
        "default_mode": str(cfg.get("timer.default_mode", timer.MODE_POMODORO)),
        "pomodoro_minutes": int(cfg.get("timer.pomodoro_minutes", 25)),
        "break_minutes": int(cfg.get("timer.break_minutes", 5)),
        "long_break_minutes": int(cfg.get("timer.long_break_minutes", 15)),
        "sessions_before_long_break": int(cfg.get("timer.sessions_before_long_break", 4)),
        "running": session,
        **timer.summary(cfg),
    }
    return Block(
        name="timer",
        data=data,
        data_as_of=datetime.now().isoformat(timespec="seconds"),
    )
