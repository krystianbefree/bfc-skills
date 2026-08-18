"""
Silnik sygnałów - zamienia surowe bloki w alerty i akcje na dziś.

Zasada: panel wykłada fakty na stół, ale nie decyduje za człowieka. Sygnał
nazywa fakt i podaje link, a nie wmawia, co masz czuć. Poziom `alarm` jest
zarezerwowany na rzeczy, które kosztują pieniądze albo są nieodwracalne
(deadline po terminie). Jeśli wszystko jest alarmem, nic nim nie jest.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from engine.config import Config
from engine.schema import (
    SEVERITY_ALARM,
    SEVERITY_INFO,
    SEVERITY_OK,
    SEVERITY_WARN,
    Action,
    Signal,
    SourceHealth,
)
from engine.util import days_since, plural

# Ile dni bez świeżych danych zanim źródło uznamy za nieświeże.
_DEFAULT_STALE_DAYS: Dict[str, float] = {
    "pozyskiwanie": 30,
    "klienci": 30,
    "biznes": 60,
    "kasa": 2,
    "connectors": 999,
    "timer": 999,
    "tresci": 999,
    "statystyki": 999,
    "outputy": 999,
    "toolkit": 999,
}

_LABELS: Dict[str, str] = {
    "pozyskiwanie": "Lejek",
    "klienci": "Klienci",
    "biznes": "Biznes",
    "kasa": "Kasa",
    "connectors": "Połączenia",
    "timer": "Czas",
    "tresci": "Content",
    "statystyki": "Zasięgi",
    "outputy": "Archiwum",
    "toolkit": "Toolkit",
}


def _data(blocks: Dict[str, Any], name: str) -> Dict[str, Any]:
    block = blocks.get(name)
    if not block or not block.ok:
        return {}
    return block.data or {}


# ── ZDROWIE ŹRÓDEŁ ────────────────────────────────────────────────────────
def build_health(cfg: Config, blocks: Dict[str, Any]) -> List[SourceHealth]:
    health: List[SourceHealth] = []

    for name, block in blocks.items():
        label = _LABELS.get(name, name)

        if not block.ok:
            health.append(
                SourceHealth(
                    name=name,
                    label=label,
                    ok=False,
                    severity=SEVERITY_ALARM,
                    message=block.error or "źródło nie odpowiada",
                )
            )
            continue

        limit = float(cfg.get(f"sources.{name}.stale_after_days", _DEFAULT_STALE_DAYS.get(name, 3)))
        age = days_since(block.data_as_of)

        if age is None:
            severity, message = SEVERITY_INFO, "brak znacznika czasu"
        elif age > limit:
            severity = SEVERITY_WARN
            message = f"nieświeże od {age:.0f} dni"
        else:
            severity = SEVERITY_OK
            message = "świeże" if age < 1 else f"{age:.0f} dni temu"

        if block.from_cache:
            message += " (cache)"

        health.append(
            SourceHealth(
                name=name,
                label=label,
                ok=severity != SEVERITY_ALARM,
                severity=severity,
                message=message,
                data_as_of=block.data_as_of,
                age_days=age,
            )
        )

    order = {SEVERITY_ALARM: 0, SEVERITY_WARN: 1, SEVERITY_INFO: 2, SEVERITY_OK: 3}
    health.sort(key=lambda h: (order.get(h.severity, 9), h.label))
    return health


# ── SYGNAŁY ───────────────────────────────────────────────────────────────
def build_signals(cfg: Config, blocks: Dict[str, Any]) -> List[Signal]:
    signals: List[Signal] = []
    poz = _data(blocks, "pozyskiwanie")
    kli = _data(blocks, "klienci")
    biz = _data(blocks, "biznes")

    dni_ruch = int(cfg.get("signals.dni_bez_ruchu_lejek", 14))
    dni_kontakt = int(cfg.get("signals.dni_bez_kontaktu", 21))

    # 1. Zaległy follow-up w lejku.
    for item in (poz.get("overdue_followups") or [])[:5]:
        signals.append(
            Signal(
                id=f"followup-{item['key']}",
                severity=SEVERITY_WARN,
                title=f"Zaległy follow-up: {item['title']}",
                detail=f"Termin był {item['follow_up']} ({item['stage_label']}). Odezwij się albo przesuń.",
                link=item.get("link"),
                link_label="Otwórz" if item.get("link") else None,
                source="pozyskiwanie",
            )
        )

    # 2. Lead bez ruchu ponad próg.
    stale = [i for i in (poz.get("stale_leads") or []) if not i["follow_up_overdue"]]
    for item in stale[:4]:
        signals.append(
            Signal(
                id=f"lead-stoi-{item['key']}",
                severity=SEVERITY_INFO,
                title=f"{item['title']} stoi {item['age_days']} dni",
                detail=f"Lead w etapie {item['stage_label']} bez ruchu ponad {dni_ruch} dni.",
                source="pozyskiwanie",
            )
        )

    # 3. Klient bez kontaktu ponad próg.
    for client in (kli.get("all") or []):
        if client["status"] != "aktywny":
            continue
        days = client.get("days_since_contact")
        if days is not None and days > dni_kontakt:
            signals.append(
                Signal(
                    id=f"klient-cisza-{client['file']}",
                    severity=SEVERITY_WARN,
                    title=f"{client['name']} - {days} dni bez kontaktu",
                    detail=f"Ostatni kontakt {client['ostatni_kontakt']}. Próg to {dni_kontakt} dni.",
                    source="klienci",
                )
            )

    # 4. Deadline'y projektów klientów.
    for client in (kli.get("all") or []):
        for proj in client.get("projekty", []):
            _deadline_signal(signals, proj, client["name"], "klienci", client.get("file"))

    # 5. Deadline'y własnego biznesu.
    for item in (biz.get("all") or []):
        if item.get("deadline"):
            _deadline_signal(
                signals,
                {"name": item["name"], "deadline": item["deadline"],
                 "overdue": item["overdue"], "days_to_deadline": item["days_to_deadline"]},
                "Własny biznes", "biznes", item.get("file"),
            )

    order = {SEVERITY_ALARM: 0, SEVERITY_WARN: 1, SEVERITY_INFO: 2, SEVERITY_OK: 3}
    signals.sort(key=lambda s: order.get(s.severity, 9))
    return signals


def _deadline_signal(signals: List[Signal], proj: Dict[str, Any], owner: str,
                     source: str, file: Any) -> None:
    """Deadline po terminie -> alarm, dziś/jutro -> warn, dalej -> cisza."""
    days = proj.get("days_to_deadline")
    if proj.get("overdue"):
        signals.append(
            Signal(
                id=f"deadline-{source}-{proj['name']}",
                severity=SEVERITY_ALARM,
                title=f"Po terminie: {proj['name']} ({owner})",
                detail=f"Deadline był {proj['deadline']}.",
                source=source,
            )
        )
    elif days is not None and days <= 1:
        when = "dziś" if days == 0 else "jutro"
        signals.append(
            Signal(
                id=f"deadline-{source}-{proj['name']}",
                severity=SEVERITY_WARN,
                title=f"Deadline {when}: {proj['name']} ({owner})",
                detail=f"Termin {proj['deadline']}.",
                source=source,
            )
        )


# ── DZIŚ ──────────────────────────────────────────────────────────────────
def build_today(cfg: Config, blocks: Dict[str, Any], signals: List[Signal]) -> List[Action]:
    """
    Krótka lista tego, co ma sens zrobić teraz: terminy po czasie, zaległe
    to-do klientów i biznesu, zaległe follow-upy. Maksymalnie pięć pozycji.
    """
    actions: List[Action] = []
    poz = _data(blocks, "pozyskiwanie")
    kli = _data(blocks, "klienci")
    biz = _data(blocks, "biznes")

    # 1. Deadline'y po terminie (alarm).
    for client in (kli.get("all") or []):
        for proj in client.get("projekty", []):
            if proj.get("overdue"):
                actions.append(
                    Action(
                        id=f"proj-{client['file']}-{proj['name']}",
                        title=f"Po terminie: {proj['name']}",
                        detail=f"{client['name']} · deadline {proj['deadline']}",
                        severity=SEVERITY_ALARM,
                    )
                )

    # 2. Zaległe to-do klientów (klikalne - odhaczają w pliku klienta).
    for client in (kli.get("all") or []):
        for todo in client.get("todos", []):
            if todo["overdue"]:
                actions.append(
                    Action(
                        id=f"todo-{client['file']}-{todo['key']}",
                        title=todo["text"],
                        detail=f"{client['name']} · termin {todo['termin']} (po terminie)",
                        severity=SEVERITY_ALARM,
                        action_type="task_status",
                        action_payload={"file": client["file"], "key": todo["key"], "done": True},
                    )
                )

    # 3. Zaległe to-do własnego biznesu (klikalne).
    for item in (biz.get("all") or []):
        for todo in item.get("todos", []):
            if todo["overdue"]:
                actions.append(
                    Action(
                        id=f"biztodo-{item['file']}-{todo['key']}",
                        title=todo["text"],
                        detail=f"{item['name']} · termin {todo['termin']} (po terminie)",
                        severity=SEVERITY_WARN,
                        action_type="task_status",
                        action_payload={"file": item["file"], "key": todo["key"], "done": True},
                    )
                )

    # 4. Zaległe follow-upy w lejku.
    for lead in (poz.get("overdue_followups") or []):
        actions.append(
            Action(
                id=f"fu-{lead['key']}",
                title=f"Follow-up: {lead['title']}",
                detail=f"Termin był {lead['follow_up']} ({lead['stage_label']})",
                severity=SEVERITY_WARN,
                link=lead.get("link"),
                link_label="Otwórz" if lead.get("link") else None,
            )
        )

    if not actions:
        actions.append(
            Action(
                id="czysto",
                title="Nic pilnego na dziś",
                detail="Terminy, to-do klientów i follow-upy ogarnięte. Dobry moment na robotę bez terminu.",
                severity=SEVERITY_OK,
            )
        )

    return actions[:5]
