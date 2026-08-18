"""
Składanie kontraktu danych - jeden JSON, z którego żyje cały interfejs.

To jest warstwa, którą podmieniasz budując panel pod swój biznes: własne
adaptery w `ADAPTERS`, własne etapy w configu, ten sam UI.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from engine.adapters import biznes, connectors, kasa, klienci, outputy, pozyskiwanie, statystyki, timer_block, toolkit, tresci
from engine.cache import cached_block
from engine.config import Config, load_config
from engine.schema import Block
from engine.signals import build_health, build_signals, build_today

# Nazwa źródła -> funkcja pobierająca. Kolejność ma znaczenie tylko dla logów.
ADAPTERS: Dict[str, Callable[[Config], Block]] = {
    "pozyskiwanie": pozyskiwanie.fetch,
    "klienci": klienci.fetch,
    "biznes": biznes.fetch,
    "kasa": kasa.fetch,
    "connectors": connectors.fetch,
    "timer": timer_block.fetch,
    "tresci": tresci.fetch,
    "statystyki": statystyki.fetch,
    "outputy": outputy.fetch,
    "toolkit": toolkit.fetch,
}


def collect_blocks(cfg: Config, force: bool = False,
                   only: Optional[List[str]] = None) -> Dict[str, Block]:
    """Odpala adaptery włączone w configu. Padnięte źródło nie kładzie reszty."""
    blocks: Dict[str, Block] = {}

    for name, producer in ADAPTERS.items():
        if only and name not in only:
            continue
        if not cfg.source_enabled(name):
            continue

        block = cached_block(
            name=name,
            ttl_minutes=cfg.source_ttl(name),
            producer=lambda p=producer: p(cfg),
            force=force,
        )
        block.name = name
        if not block.fetched_at:
            block.fetched_at = datetime.now().isoformat(timespec="seconds")
        blocks[name] = block

        if not block.ok:
            logger.warning(f"Źródło '{name}' nie odpowiada: {block.error}")

    return blocks


def build(cfg: Optional[Config] = None, force: bool = False) -> Dict[str, Any]:
    """Pełny kontrakt danych dla `/api/data`."""
    cfg = cfg or load_config()
    blocks = collect_blocks(cfg, force=force)

    signals = build_signals(cfg, blocks)
    today = build_today(cfg, blocks, signals)
    health = build_health(cfg, blocks)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "owner": cfg.owner,
        "pipeline": {
            "unit": cfg.get("pipeline.unit"),
            "unit_plural": cfg.get("pipeline.unit_plural"),
            "stages": cfg.stages,
            "archived_stages": cfg.get("pipeline.archived_stages", []),
        },
        "blocks": {name: block.to_dict() for name, block in blocks.items()},
        "signals": [s.to_dict() for s in signals],
        "today": [a.to_dict() for a in today],
        "health": [h.to_dict() for h in health],
    }


def main() -> None:
    """Podgląd kontraktu z linii poleceń: `python -m engine.build`."""
    payload = build(force=True)
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
