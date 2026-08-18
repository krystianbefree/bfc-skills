"""
Adapter kasy - liczby, na które freelancer patrzy raz dziennie.

Tryb `sources.kasa.zrodlo` decyduje o źródle przychodu:
  * "reczne"    - SZACUNEK ze stawek aktywnych klientów (frontmatter `stawka`),
                  wyraźnie oznaczony jako szacunek, nie realny przychód,
  * "faktury"   - REALNA gotówka: suma kwot ze statusem „oplacona" z pliku
                  `<sejf>/<sources.kasa.ledger_file>` (np. `Kasa.md`), z okna
                  `window_days`,
  * "stripe"    - REALNY przychód z żywego API Stripe; obsługuje wiele kont
                  (`sources.kasa.accounts: [{key_env, label}]`), paginację i
                  błędy API (brak klucza -> czytelny `note`, nigdy crash),
  * "nie_licze" - panel nie pokazuje kasy (Block bez danych).

Wartość lejka i liczba klientów pochodzą z bloków pozyskiwanie/klienci, liczone
niezależnie tym samym adapterem. Klucze API zostają po stronie serwera - w
payloadzie lądują tylko etykiety i nazwy zmiennych środowiskowych, nigdy klucz.
"""
from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from engine.adapters import klienci as klienci_adapter
from engine.adapters import pozyskiwanie as pozyskiwanie_adapter
from engine.config import Config
from engine.schema import Block
from engine.util import parse_amount

_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
# Statusy liczone jako realna, wpłacona gotówka (po zdjęciu ogonków i ascii).
_PAID_PREFIXES = ("oplac", "zaplac", "paid")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _funnel_snapshot(cfg: Config) -> Dict[str, Any]:
    """Wartość lejka i liczba prospektów - niezależnie od bloku pozyskiwanie."""
    try:
        data = pozyskiwanie_adapter.fetch(cfg).data
        return {"funnel_value": data.get("funnel_value", 0), "prospects": data.get("total", 0)}
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Kasa: nie policzyłem wartości lejka: {exc}")
        return {"funnel_value": 0, "prospects": 0}


def _clients_snapshot(cfg: Config) -> Dict[str, Any]:
    """Aktywni klienci i suma ich stawek - do trybu ręcznego (szacunek)."""
    try:
        data = klienci_adapter.fetch(cfg).data
        active = [c for c in data.get("all", []) if c["status"] == "aktywny"]
        stawki = round(sum(c.get("stawka_value") or 0 for c in active))
        return {"active_clients": len(active), "stawki_sum": stawki}
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Kasa: nie policzyłem klientów: {exc}")
        return {"active_clients": 0, "stawki_sum": 0}


# ── tryb faktury: realna gotówka z pliku ledgera ──────────────────────────
def _ascii_lower(text: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").strip().lower()


def _ledger_revenue(path, window: int) -> Tuple[Optional[int], int, Optional[str], str]:
    """
    Sumuje realną gotówkę z pliku ledgera. Linie:
        - 2026-08-10 | 4000 zł | Kowalski | oplacona
    Liczone tylko pozycje ze statusem „oplacona" z okna `window` dni. Zwraca
    (suma|None, liczba_wpłat, data_najświeższej, note). Odporne na brudne linie.
    """
    if not path.exists():
        return None, 0, None, f"Brak pliku ledgera ({path.name}) - dodaj go, by liczyć realną kasę."

    cutoff = date.today() - timedelta(days=window)
    total = 0.0
    paid = 0
    skipped = 0
    latest: Optional[str] = None
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")

    for line in raw.splitlines():
        m = _BULLET_RE.match(line)
        if not m:
            continue
        body = m.group(1)
        if "|" not in body:
            continue
        try:
            parts = [p.strip() for p in body.split("|")]
            dm = _DATE_RE.search(parts[0])
            if not dm:
                skipped += 1
                continue
            when = dm.group(1)
            try:
                when_date = datetime.strptime(when, "%Y-%m-%d").date()
            except ValueError:
                skipped += 1
                continue
            amount = parse_amount(parts[1]) if len(parts) > 1 else None
            status = _ascii_lower(parts[-1]) if len(parts) > 2 else ""
            is_paid = any(status.startswith(p) for p in _PAID_PREFIXES)
            if not is_paid or amount is None:
                continue
            if when_date < cutoff:
                continue
            total += amount
            paid += 1
            if latest is None or when > latest:
                latest = when
        except Exception as exc:  # noqa: BLE001 - zła linia nie kładzie kasy
            skipped += 1
            logger.warning(f"Kasa/faktury: pomijam linię {line!r}: {exc}")

    note = f"Realna gotówka: {paid} wpłat oplaconych z ostatnich {window} dni ({path.name})."
    if skipped:
        note += f" Pominięto {skipped} zepsutych linii."
    return round(total), paid, latest, note


def _parse_ledger(path) -> List[Dict[str, Any]]:
    """Wszystkie pozycje ledgera z polami date/amount/who/status/is_paid.

    Zasila bogaty widok Kasy: rozbicie per klient, lista wpłat i zaległe faktury.
    Odporne na brudną linię (pomija ją cicho).
    """
    out: List[Dict[str, Any]] = []
    if not path.exists():
        return out
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    for line in raw.splitlines():
        m = _BULLET_RE.match(line)
        if not m or "|" not in m.group(1):
            continue
        parts = [p.strip() for p in m.group(1).split("|")]
        dm = _DATE_RE.search(parts[0])
        if not dm or len(parts) < 3:
            continue
        amount = parse_amount(parts[1])
        if amount is None:
            continue
        status_raw = parts[-1]
        is_paid = any(_ascii_lower(status_raw).startswith(p) for p in _PAID_PREFIXES)
        out.append({
            "date": dm.group(1),
            "amount": round(amount),
            "who": parts[2],
            "status": status_raw,
            "is_paid": is_paid,
        })
    return out


# ── tryb stripe: realny przychód z API (wiele kont) ───────────────────────
def _stripe_account_revenue(key: str, window: int) -> float:
    """Suma udanych obciążeń z okna `window` dni dla jednego klucza (paginacja)."""
    import stripe  # import leniwy - pozostałe tryby nie potrzebują biblioteki

    client = stripe.StripeClient(api_key=key)
    since = int((datetime.utcnow() - timedelta(days=window)).timestamp())
    total = 0.0
    starting_after: Optional[str] = None
    while True:
        params: Dict[str, Any] = {"created": {"gte": since}, "limit": 100}
        if starting_after:
            params["starting_after"] = starting_after
        page = client.charges.list(params=params)
        data = page.data or []
        for ch in data:
            if ch.get("status") == "succeeded" and not ch.get("refunded"):
                amount = ch.get("amount_captured") or ch.get("amount") or 0
                total += amount / 100
        if not getattr(page, "has_more", False) or not data:
            break
        starting_after = data[-1].id
    return round(total)


def _stripe_accounts(cfg: Config) -> List[Dict[str, str]]:
    """Lista kont z configu; fallback do pojedynczego STRIPE_API_KEY."""
    accounts = cfg.get("sources.kasa.accounts") or []
    clean: List[Dict[str, str]] = []
    for acc in accounts:
        if not isinstance(acc, dict):
            continue
        key_env = str(acc.get("key_env") or "").strip()
        if not key_env:
            continue
        clean.append({"key_env": key_env, "label": str(acc.get("label") or key_env).strip()})
    if not clean:
        clean = [{"key_env": "STRIPE_API_KEY", "label": "Stripe"}]
    return clean


def _stripe_revenue(cfg: Config, window: int) -> Tuple[Optional[int], str]:
    """
    Sumuje przychód ze wszystkich skonfigurowanych kont Stripe. Brak klucza albo
    błąd API danego konta -> odnotowane w note, reszta liczy się dalej. Klucze
    nigdy nie trafiają do zwracanych danych - tylko etykiety i nazwy zmiennych.
    """
    accounts = _stripe_accounts(cfg)
    total = 0.0
    had_value = False
    notes: List[str] = []

    for acc in accounts:
        label, key_env = acc["label"], acc["key_env"]
        key = os.getenv(key_env, "")
        if not key:
            notes.append(f"{label}: brak klucza w .env ({key_env})")
            continue
        try:
            rev = _stripe_account_revenue(key, window)
            total += rev
            had_value = True
            notes.append(f"{label}: {round(rev)} zł")
        except Exception as exc:  # noqa: BLE001 - jedno konto nie kładzie kasy
            logger.warning(f"Kasa/stripe: konto {label} ({key_env}) padło: {exc}")
            notes.append(f"{label}: błąd API")

    summary = "; ".join(notes) if notes else "brak kont Stripe w configu"
    if not had_value:
        return None, f"Stripe niedostępny - {summary}."
    return round(total), f"Realny przychód z {window} dni (Stripe). {summary}."


# ── etykiety źródła dla frontu (realne vs szacunek) ───────────────────────
_SOURCE_LABELS = {
    "faktury": "faktury",
    "stripe": "Stripe",
    "reczne": "szacunek ze stawek",
    "nie_licze": "wyłączone",
}


def fetch(cfg: Config) -> Block:
    zrodlo = str(cfg.get("sources.kasa.zrodlo", "reczne")).strip().lower().replace(" ", "_")
    window = int(cfg.get("sources.kasa.window_days", 30) or 30)

    funnel = _funnel_snapshot(cfg)
    clients = _clients_snapshot(cfg)

    # Konwersja: udział klientów wśród wszystkich w zasięgu (klienci + lejek).
    denom = clients["active_clients"] + funnel["prospects"]
    conversion = round(clients["active_clients"] / denom * 100) if denom else None

    data: Dict[str, Any] = {
        "zrodlo": zrodlo,
        "window_days": window,
        "funnel_value": funnel["funnel_value"],
        "active_clients": clients["active_clients"],
        "conversion": conversion,
    }
    data_as_of = _now_iso()

    if zrodlo == "nie_licze":
        data.update({"revenue_window": None, "source": "nie_licze",
                     "source_label": _SOURCE_LABELS["nie_licze"], "is_real": False,
                     "note": "Kasa wyłączona (zrodlo = nie liczę)."})
        return Block(name="kasa", data=data, data_as_of=data_as_of)

    if zrodlo == "faktury":
        try:
            ledger_file = cfg.get("sources.kasa.ledger_file", "Kasa.md")
            path = cfg.sejf_path(ledger_file)
            entries = _parse_ledger(path)
        except Exception as exc:  # noqa: BLE001 - nigdy nie kładziemy bloku
            logger.warning(f"Kasa/faktury: {exc}")
            entries = []

        cutoff = (date.today() - timedelta(days=window)).isoformat()
        paid_win = [e for e in entries if e["is_paid"] and e["date"] >= cutoff]
        revenue = sum(e["amount"] for e in paid_win)
        pending = sorted([e for e in entries if not e["is_paid"]], key=lambda e: e["date"], reverse=True)
        pending_total = sum(e["amount"] for e in pending)

        per: Dict[str, int] = {}
        for e in paid_win:
            per[e["who"]] = per.get(e["who"], 0) + e["amount"]
        per_client = sorted(({"who": k, "amount": v} for k, v in per.items()), key=lambda x: -x["amount"])
        transactions = sorted(paid_win, key=lambda e: e["date"], reverse=True)
        latest = transactions[0]["date"] if transactions else None

        label = str(cfg.get("sources.kasa.label") or _SOURCE_LABELS["faktury"])
        note = f"{len(paid_win)} wpłat z ostatnich {window} dni"
        if pending:
            note += f" · {len(pending)} oczekujących na {round(pending_total)} zł"

        data.update({
            "revenue_window": revenue if entries else None,
            "source": "faktury", "source_label": label, "is_real": True,
            "paid_count": len(paid_win), "transactions": transactions,
            "pending": pending, "pending_total": round(pending_total),
            "per_client": per_client, "note": note,
        })
        return Block(name="kasa", data=data, data_as_of=latest or data_as_of)

    if zrodlo == "stripe":
        try:
            revenue, note = _stripe_revenue(cfg, window)
        except Exception as exc:  # noqa: BLE001 - nigdy nie kładziemy bloku
            logger.warning(f"Kasa/stripe: {exc}")
            revenue, note = None, f"Stripe niedostępny: {exc}"
        data.update({"revenue_window": revenue, "source": "stripe",
                     "source_label": _SOURCE_LABELS["stripe"], "is_real": True,
                     "note": note})
        return Block(name="kasa", data=data, data_as_of=data_as_of)

    # Tryb ręczny: przychód = suma stawek aktywnych klientów (SZACUNEK, nie przychód).
    data.update({
        "revenue_window": clients["stawki_sum"],
        "source": "reczne",
        "source_label": _SOURCE_LABELS["reczne"],
        "is_real": False,
        "note": "Szacunek ze stawek aktywnych klientów (nie realny przychód - włącz tryb faktury/stripe).",
    })
    return Block(name="kasa", data=data, data_as_of=data_as_of)
