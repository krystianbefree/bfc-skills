"""
Adapter archiwum outputów - gotowe efekty skończonych zadań.

Czyta folder `<sejf>/Outputy/` (nazwa z configu). Każdy podfolder to typ
efektu (Wyceny, Oferty, Treści, Scenariusze...), każdy plik `.md` w środku to
jeden gotowy output: cennik, oferta, artykuł, scenariusz automatyzacji. Panel
tylko go pokazuje - zapisuje go Claude z rozmowy, gdy zamykacie zadanie
(reguły: blueprints/zadania-lifecycle.md). Dzięki temu efekt pracy nie ginie w
czacie: leży jako notatka, można go kliknąć, skopiować i podać ponownie.

Read-only. Zero zapisu z tego adaptera - archiwum tworzy Claude przez Write,
trzymając się konwencji folderów i frontmatteru.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime

import yaml

from engine.config import Config
from engine.schema import Block
from engine.util import plain_text, to_iso

_FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")

# Kolejność wyświetlania typów w zakładce. Typy spoza listy lecą na koniec
# alfabetycznie - folder decyduje, nie ten spis.
_TYP_ORDER = ["Wyceny", "Oferty", "Treści", "Scenariusze", "Maile",
              "Strategie", "Artykuły", "Inne"]


def _key(rel_path: str) -> str:
    return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:10]


def _read(path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def _split_frontmatter(text: str):
    """Zwraca (meta dict, body). Brak frontmatteru -> ({}, cały tekst)."""
    m = _FM.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
        if not isinstance(meta, dict):
            meta = {}
    except yaml.YAMLError:
        meta = {}
    return meta, m.group(2)


def _title(meta: dict, body: str, stem: str) -> str:
    """Tytuł: nagłówek `# ...` z treści -> frontmatter -> nazwa pliku bez daty."""
    for line in body.splitlines():
        h = line.strip()
        if h.startswith("# "):
            return plain_text(h[2:])
    if meta.get("tytul") or meta.get("title"):
        return plain_text(str(meta.get("tytul") or meta.get("title")))
    return _DATE_PREFIX.sub("", stem).strip(" -") or stem


def _date(meta: dict, path, stem: str):
    for k in ("data", "date"):
        if meta.get(k):
            return to_iso(str(meta[k]))
    m = _DATE_PREFIX.match(stem)
    if m:
        return to_iso(m.group(1))
    try:
        return to_iso(datetime.fromtimestamp(path.stat().st_mtime))
    except OSError:
        return None


def _note(body: str) -> str:
    """Pierwsza sensowna linia treści (bez nagłówka) - podgląd na karcie."""
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        return re.sub(r"[*#>`_]", "", s).lstrip("- ").strip()[:160]
    return ""


def fetch(cfg: Config) -> Block:
    base_rel = cfg.get("sources.outputy.dir", "Outputy")
    base = cfg.sejf_path(base_rel)
    if not base.exists():
        return Block(name="outputy",
                     data={"items": [], "by_typ": {}, "typy": [], "total": 0})

    items = []
    latest = None
    for path in sorted(base.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(base)
        # Typ = pierwszy podfolder pod Outputy/; plik w korzeniu -> „Inne".
        typ = rel.parts[0] if len(rel.parts) > 1 else "Inne"
        text = _read(path)
        meta, body = _split_frontmatter(text)
        body = body.strip()
        stem = path.stem
        rel_full = f"{base_rel}/{rel.as_posix()}"
        data_iso = _date(meta, path, stem)
        if data_iso and (latest is None or data_iso > latest):
            latest = data_iso
        items.append({
            "title": _title(meta, body, stem),
            "typ": typ,
            "klient": plain_text(str(meta.get("klient", "") or meta.get("projekt", ""))),
            "zadanie": plain_text(str(meta.get("zadanie", ""))),
            "zrodlo": str(meta.get("zrodlo", "") or ""),
            "data": data_iso,
            "path": rel_full,
            "body": body,
            "note": _note(body),
            "key": _key(rel_full),
        })

    # Najnowsze u góry w obrębie typu.
    items.sort(key=lambda it: (it["data"] or ""), reverse=True)

    typy_present = {it["typ"] for it in items}
    typy = [t for t in _TYP_ORDER if t in typy_present]
    typy += sorted(t for t in typy_present if t not in _TYP_ORDER)

    by_typ = {t: [it for it in items if it["typ"] == t] for t in typy}

    return Block(
        name="outputy",
        data={"items": items, "by_typ": by_typ, "typy": typy, "total": len(items)},
        data_as_of=latest,
    )
