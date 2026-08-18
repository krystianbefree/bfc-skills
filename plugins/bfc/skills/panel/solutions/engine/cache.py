"""
Cache na dysku dla wolnych źródeł (np. Stripe live).

Lokalne czytanie plików MD jest darmowe i leci zawsze na świeżo (ttl_minutes: 0).
Zewnętrzne API mają TTL z configu, żeby odświeżenie strony nie kosztowało
kilkunastu requestów.

Katalog cache jest env-overridable (DASHBOARD_DATA), bo silnik żyje w projekcie
użytkownika, nie w repo pluginu.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

from loguru import logger

from engine.config import DATA_DIR
from engine.schema import Block

CACHE_PATH = DATA_DIR / "dashboard_cache.json"
_LOCK = threading.Lock()


def _read_store() -> Dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(f"Cache panelu nieczytelny, startuję od zera: {exc}")
        return {}


def _write_store(store: Dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(store, fh, ensure_ascii=False)
    tmp.replace(CACHE_PATH)


def cached_block(
    name: str,
    ttl_minutes: int,
    producer: Callable[[], Block],
    force: bool = False,
) -> Block:
    """
    Zwraca blok z cache jeśli świeży, inaczej odpala `producer`.

    Gdy producer wywali się, a w cache leży stara odpowiedź - oddajemy starą
    z oznaczeniem `from_cache`. Lepiej pokazać wczorajszą liczbę niż pustą kartę.
    """
    if ttl_minutes <= 0 and not force:
        return _run(name, producer, fallback=None)

    with _LOCK:
        store = _read_store()
        entry = store.get(name)

    if entry and not force:
        try:
            saved_at = datetime.fromisoformat(entry["fetched_at"])
            if datetime.now() - saved_at < timedelta(minutes=ttl_minutes):
                block = Block(**entry["block"])
                block.from_cache = True
                return block
        except (KeyError, ValueError, TypeError):
            pass

    fallback = Block(**entry["block"]) if entry and "block" in entry else None
    block = _run(name, producer, fallback=fallback)

    if block.ok:
        with _LOCK:
            store = _read_store()
            store[name] = {
                "fetched_at": datetime.now().isoformat(timespec="seconds"),
                "block": block.to_dict(),
            }
            _write_store(store)

    return block


def _run(name: str, producer: Callable[[], Block], fallback: Optional[Block]) -> Block:
    """Odpala adapter, łapiąc każdy wyjątek - jedno źródło nie może położyć całego ekranu."""
    try:
        return producer()
    except Exception as exc:  # noqa: BLE001 - celowo szeroko
        logger.error(f"Adapter '{name}' padł: {exc}")
        if fallback is not None:
            fallback.from_cache = True
            fallback.error = f"Świeże pobranie nie wyszło ({exc}). Dane z cache."
            return fallback
        return Block.failed(name, str(exc))


def clear_cache() -> None:
    with _LOCK:
        if CACHE_PATH.exists():
            CACHE_PATH.unlink()
