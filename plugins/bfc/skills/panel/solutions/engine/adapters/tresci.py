"""
Adapter treści do nagrania — pomysły i materiały, żeby nic nie zginęło.

Czyta `<sejf>/Do nagrania.md`: każdy `## Tytuł` to jedna pozycja, linia
`Status:` opisuje etap, a cała reszta pod nagłówkiem to treść pozycji (np. szkic
albo pełny skrypt rolki), pokazywana w podglądzie po kliknięciu. Pipeline:
pomysł -> szkic -> nagrane -> opublikowane. Kartę można przeciągnąć między
etapami — panel wtedy punktowo podmienia linię `Status:` w pliku (kopia przed
zapisem), tak jak przy lejku i to-do.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from datetime import datetime

from engine.config import DATA_DIR, Config
from engine.schema import Block
from engine.util import plain_text, to_iso

_H2 = re.compile(r"^##\s+(.+?)\s*$")
_STATUS = re.compile(r"^status:\s*(.+)$", re.IGNORECASE)

STAGES = ["pomysł", "szkic", "nagrane", "opublikowane"]
_ALIAS = {"pomysl": "pomysł", "idea": "pomysł", "draft": "szkic",
          "nagrany": "nagrane", "gotowe": "nagrane",
          "opublikowany": "opublikowane", "publikacja": "opublikowane"}

_BACKUP_DIR = DATA_DIR / "sejf_backups"


def _key(title: str) -> str:
    norm = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return hashlib.sha1(norm.strip().lower().encode("utf-8")).hexdigest()[:10]


def _read(path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def _norm_status(raw: str) -> str:
    raw = raw.strip().lower()
    return raw if raw in STAGES else _ALIAS.get(raw, "pomysł")


def _parse(path):
    if not path.exists():
        return []
    out = []
    cur = None
    body = []

    def flush():
        if cur is None:
            return
        text = "\n".join(body).strip()
        cur["body"] = text
        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        cur["note"] = re.sub(r"[*#>`_]", "", first).lstrip("- ").strip()

    for line in _read(path).splitlines():
        h = _H2.match(line)
        if h:
            flush()
            cur = {"title": plain_text(h.group(1)), "status": "pomysł", "body": "", "note": ""}
            cur["key"] = _key(cur["title"])
            out.append(cur)
            body = []
            continue
        if cur is None:
            continue
        s = _STATUS.match(line.strip())
        if s:
            cur["status"] = _norm_status(s.group(1))
            continue
        body.append(line)
    flush()
    return out


def fetch(cfg: Config) -> Block:
    path = cfg.sejf_path(cfg.get("sources.tresci.file", "Do nagrania.md"))
    items = _parse(path)
    by_status = {s: [] for s in STAGES}
    for it in items:
        by_status[it["status"] if it["status"] in by_status else "pomysł"].append(it)

    data_as_of = to_iso(datetime.fromtimestamp(path.stat().st_mtime)) if path.exists() else None
    return Block(
        name="tresci",
        data={"items": items, "by_status": by_status, "stages": STAGES, "total": len(items)},
        data_as_of=data_as_of,
    )


def set_status(path, key: str, new_status: str):
    """Podmienia linię `Status:` pod nagłówkiem pozycji o danym kluczu."""
    new_status = _norm_status(new_status)
    if new_status not in STAGES:
        raise ValueError(f"Nieznany etap: {new_status}")
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku: {path}")

    lines = _read(path).splitlines()
    target = None
    for i, line in enumerate(lines):
        h = _H2.match(line)
        if h and _key(plain_text(h.group(1))) == key:
            target = i
            break
    if target is None:
        raise KeyError(f"Nie ma pozycji o kluczu '{key}' w {path.name}. Odśwież panel.")

    end = len(lines)
    for j in range(target + 1, len(lines)):
        if _H2.match(lines[j]):
            end = j
            break

    status_idx = None
    for j in range(target + 1, end):
        if _STATUS.match(lines[j].strip()):
            status_idx = j
            break

    new_line = f"Status: {new_status}"
    if status_idx is not None:
        lines[status_idx] = new_line
    else:
        lines.insert(target + 1, new_line)

    _backup(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "key": key, "status": new_status}


def _backup(path) -> None:
    _BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, _BACKUP_DIR / f"{path.stem}.{stamp}.md")
    for old in sorted(_BACKUP_DIR.glob(f"{path.stem}.*.md"))[:-30]:
        old.unlink(missing_ok=True)
