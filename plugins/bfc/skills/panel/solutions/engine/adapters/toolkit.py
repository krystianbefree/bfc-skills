"""
Adapter toolkitu - czym Claude Code dysponuje pod ręką.

Zakładka Toolkit odpowiada na pytanie „jaka była ta komenda do…", zamiast
zmuszać do grzebania w `.claude/`. Skanujemy komendy i skille - projektowe
(katalog projektu) i globalne (`~/.claude`). Na stałe dorzucamy skróty do
kluczowych skilli klubu (`/bfc:research`, `/bfc:oferta`, `/bfc:cold-mail`).
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

from engine.config import PROJECT_ROOT, Config
from engine.schema import Block

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Skróty do skilli klubu - zawsze widoczne, niezależnie od tego, co jest w .claude.
_BFC_SHORTCUTS: List[Dict[str, Any]] = [
    {"invoke": "/bfc:research", "scope": "bfc", "description": "Znajdź i zaudytuj prospektów B2B pod outreach."},
    {"invoke": "/bfc:oferta", "scope": "bfc", "description": "Zbuduj ofertę dla klienta na bazie jego problemu."},
    {"invoke": "/bfc:cold-mail", "scope": "bfc", "description": "Napisz spersonalizowany cold mail do prospekta."},
]


def _meta(path: Path) -> Dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _first_line(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    body = _FRONTMATTER_RE.sub("", text)
    for line in body.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return clean[:160]
    return ""


def _collect(directory: Path, kind: str, scope: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not directory.exists():
        return items

    candidates = sorted(directory.glob("*.md")) if kind == "command" \
        else sorted(directory.glob("*/SKILL.md"))

    for path in candidates:
        meta = _meta(path)
        name = meta.get("name") or (path.stem if kind == "command" else path.parent.name)
        description = (meta.get("description") or _first_line(path)).strip()
        items.append({
            "name": name,
            "invoke": f"/{name}",
            "kind": kind,
            "scope": scope,
            "description": description[:200],
            "file": str(path),
        })
    return items


def fetch(cfg: Config) -> Block:
    home_claude = Path.home() / ".claude"

    collected: List[Dict[str, Any]] = []
    collected += _collect(PROJECT_ROOT / ".claude" / "commands", "command", "projekt")
    collected += _collect(PROJECT_ROOT / ".claude" / "skills", "skill", "projekt")
    collected += _collect(home_claude / "commands", "command", "globalny")
    collected += _collect(home_claude / "skills", "skill", "globalny")

    seen = set()
    tools: List[Dict[str, Any]] = []
    for item in _BFC_SHORTCUTS:
        tools.append(item)
        seen.add(item["invoke"])
    for item in collected:
        if item["invoke"] in seen:
            continue
        seen.add(item["invoke"])
        tools.append(item)

    # bfc na górze, potem projektowe, potem globalne.
    scope_order = {"bfc": 0, "projekt": 1, "globalny": 2}
    tools.sort(key=lambda t: (scope_order.get(t["scope"], 9), t.get("name", t["invoke"])))

    return Block(
        name="toolkit",
        data={
            "tools": tools,
            "commands_count": len([t for t in tools if t.get("kind") == "command"]),
            "skills_count": len([t for t in tools if t.get("kind") == "skill"]),
        },
        data_as_of=datetime.now().isoformat(timespec="seconds"),
    )
