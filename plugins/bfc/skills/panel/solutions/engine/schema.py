"""
Kontrakt danych panelu.

Każdy adapter zwraca `Block` o tym samym kształcie. UI nigdy nie dotyka bazy
ani API - czyta wyłącznie ten JSON. Dzięki temu podmieniasz adapter pod własne
dane i dostajesz ten sam interfejs bez linijki zmiany we froncie.

Kształt odpowiedzi `/api/data`:
{
  "generated_at": iso,
  "owner": {...},
  "pipeline": {...},               # etapy lejka z configu
  "blocks": { "<nazwa>": Block },  # dane z adapterów
  "signals": [Signal],             # alerty i rekomendacje
  "today": [Action],               # 3-5 konkretnych akcji na dziś
  "health": [SourceHealth]         # świeżość każdego źródła
}
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Poziomy ważności - sterują kolorem w UI.
SEVERITY_OK = "ok"
SEVERITY_INFO = "info"
SEVERITY_WARN = "warn"
SEVERITY_ALARM = "alarm"


@dataclass
class Block:
    """Wynik jednego adaptera."""

    name: str
    ok: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    fetched_at: Optional[str] = None
    from_cache: bool = False
    # Data najświeższego rekordu w źródle - do liczenia świeżości.
    data_as_of: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def failed(cls, name: str, error: str) -> "Block":
        return cls(name=name, ok=False, error=error, fetched_at=_now_iso())


@dataclass
class Signal:
    """Alert albo rekomendacja - blok SYGNAŁY."""

    id: str
    severity: str
    title: str
    detail: str = ""
    link: Optional[str] = None
    link_label: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Action:
    """Konkretna akcja na dziś - blok DZIŚ."""

    id: str
    title: str
    detail: str = ""
    severity: str = SEVERITY_INFO
    link: Optional[str] = None
    link_label: Optional[str] = None
    # Akcja może być klikalna: wywołuje POST z tym payloadem.
    action_type: Optional[str] = None
    action_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceHealth:
    """Stan jednego źródła - pasek na górze panelu."""

    name: str
    label: str
    ok: bool
    severity: str
    message: str
    data_as_of: Optional[str] = None
    age_days: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineItem:
    """Jedna jednostka pracy w pipeline (u freelancera: prospekt w lejku)."""

    key: str                       # stabilny identyfikator do zapisu statusu
    title: str
    stage: str
    stage_label: str = ""
    note: str = ""
    date: Optional[str] = None     # data ostatniej zmiany statusu
    source_ref: Optional[str] = None   # skąd wzięty (research, cold-mail)
    link: Optional[str] = None
    age_days: Optional[int] = None
    raw_status: str = ""
    # Pełna treść pozycji - zasila podgląd po kliknięciu w kartę.
    fields: Dict[str, str] = field(default_factory=dict)
    blocks: List[Dict[str, str]] = field(default_factory=list)
    body_md: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
