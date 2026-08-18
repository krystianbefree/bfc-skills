"""
Adapter własnego biznesu (`<sejf>/Biznes/*.md`, jeden plik = jedna inicjatywa).

Praca **nad** firmą, nie dla klienta: oferta, strona, systemy, marketing. Ten
sam szkielet co klient, ale bez pól klienckich - frontmatter `etap`/`deadline`
i sekcja `## Do zrobienia`. To-do odhaczają się przez `klienci.set_task_status`
(format jest identyczny).
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml
from loguru import logger

from engine.adapters.klienci import _parse_todos, _sections
from engine.config import Config
from engine.schema import Block
from engine.util import days_since, plain_text

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$")

# Kolejność etapów w UI.
_ETAP_ORDER = {"w toku": 0, "w-toku": 0, "pomysł": 1, "pomysl": 1, "wstrzymane": 2, "zrobione": 3}


def _read_item(path: Path, sejf: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    meta: Dict[str, Any] = {}
    body = text
    m = _FRONTMATTER_RE.match(text)
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        if not isinstance(meta, dict):
            meta = {}
        body = text[m.end():]

    lines = body.splitlines()
    name = path.stem
    for line in lines:
        h1 = _H1_RE.match(line)
        if h1:
            name = h1.group(1).strip()
            break

    today = date.today().isoformat()
    todos = _parse_todos(_sections(lines).get("do zrobienia", []), today)

    etap = str(meta.get("etap") or "").strip().lower() or "w toku"
    deadline = str(meta.get("deadline") or "").strip() or None
    overdue = bool(deadline and deadline < today and etap != "zrobione")
    days_to = None
    if deadline:
        ds = days_since(deadline)
        if ds is not None:
            days_to = round(-ds)

    try:
        rel = path.relative_to(sejf).as_posix()
    except ValueError:
        rel = path.name

    return {
        "name": plain_text(name),
        "etap": etap,
        "deadline": deadline,
        "overdue": overdue,
        "days_to_deadline": days_to,
        "todos": todos,
        "open_todos": len([t for t in todos if not t["done"]]),
        "overdue_todos": len([t for t in todos if t["overdue"]]),
        "file": rel,
    }


def fetch(cfg: Config) -> Block:
    directory = cfg.sejf_path(cfg.get("sources.biznes.dir", "Biznes"))
    if not directory.exists():
        raise FileNotFoundError(f"Brak katalogu biznesu: {directory}")

    sejf = cfg.sejf
    items: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for p in sorted(directory.glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:
            items.append(_read_item(p, sejf))
        except Exception as exc:  # noqa: BLE001 - jeden zły plik nie kładzie bloku
            skipped.append(p.name)
            logger.warning(f"Biznes: pomijam plik {p.name}: {exc}")
    items.sort(key=lambda i: (_ETAP_ORDER.get(i["etap"], 5), i["name"].lower()))

    return Block(
        name="biznes",
        data={
            "dir": cfg.get("sources.biznes.dir", "Biznes"),
            "all": items,
            "count": len(items),
            "overdue_count": len([i for i in items if i["overdue"]]),
            "skipped_files": skipped,
        },
        data_as_of=datetime.fromtimestamp(directory.stat().st_mtime).isoformat(timespec="seconds"),
    )
