"""Drobne narzędzia wspólne dla adapterów."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional


def to_iso(value: Any) -> Optional[str]:
    """Normalizuje datę do ISO 8601, żeby wszystko wychodziło z backendu w jednym formacie."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).isoformat(timespec="seconds")
    except ValueError:
        return text


def to_datetime(value: Any) -> Optional[datetime]:
    """Odwrotność `to_iso` - do liczenia różnic czasu."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).strip())
    except ValueError:
        return None


def plain_text(text: str) -> str:
    """
    Zdejmuje składnię Obsidiana na potrzeby interfejsu.

    `[[Firma]]` -> `Firma`, `` `Klienci/` `` -> `Klienci/`.
    Panel pokazuje treść, nie zapis - a w plikach markdown zostaje bez zmian.
    """
    if not text:
        return ""
    without_links = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    return without_links.replace("`", "").strip()


def plural(n: int, one: str, few: str, many: str) -> str:
    """
    Polska odmiana liczebnika: 1 klient, 2 klientów, 5 klientów.

    Panel mówi po polsku, więc „1 klientów" nie przechodzi.
    """
    n = abs(int(n))
    if n == 1:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def days_since(value: Any, now: Optional[datetime] = None) -> Optional[float]:
    """Ile dni minęło od podanej daty. `None` gdy daty nie da się odczytać."""
    parsed = to_datetime(value)
    if parsed is None:
        return None
    reference = now or datetime.utcnow()
    return round((reference - parsed).total_seconds() / 86400, 1)


def parse_amount(text: Any) -> Optional[float]:
    """
    Wyciąga liczbę z zapisu kwoty jak „~6000 zł", „4 000 zł", „4000zł/mc".

    Brak liczby to brak danych (None), nie zero - tak jak w blueprintach.
    """
    if text is None:
        return None
    raw = str(text)
    # Zdejmujemy separatory tysięcy (spacje, kropki) tylko między cyframi.
    cleaned = re.sub(r"(?<=\d)[ . ](?=\d{3}\b)", "", raw)
    m = re.search(r"-?\d+(?:[.,]\d+)?", cleaned)
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", "."))
    except ValueError:
        return None
