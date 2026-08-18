"""
Adapter klientów (`<sejf>/Klienci/*.md`, jeden plik = jeden klient).

Metadane siedzą we frontmatterze (status, stawka, ostatni_kontakt), a treść
w sekcjach `## Projekty` (deliverables z etapem i deadline) i `## Do zrobienia`
(checkboxy klienta). Plik zostaje czytelną notatką w Obsidianie - panel odhacza
to-do punktowo, nigdy nie przepisuje listy.

`set_task_status` i parser to-do są wspólne z adapterem `biznes` - format jest
identyczny.
"""
from __future__ import annotations

import hashlib
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from loguru import logger

from engine.config import DATA_DIR, Config
from engine.schema import Block
from engine.util import days_since, parse_amount, plain_text

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
_H1_RE = re.compile(r"^#\s+(.+?)\s*$")
_TODO_RE = re.compile(r"^(\s*[-*]\s*\[)([ xX/\-~])(\]\s*)(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_TERMIN_RE = re.compile(r"\(\s*do\s+(\d{4}-\d{2}-\d{2})\s*\)", re.IGNORECASE)
_ETAP_RE = re.compile(r"etap:\s*([^-•\n]+?)(?:\s*-\s*deadline|$)", re.IGNORECASE)
_DEADLINE_RE = re.compile(r"deadline:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)

_BACKUP_DIR = DATA_DIR / "sejf_backups"
_DONE_STATES = {"x", "X"}


def _todo_key(text: str) -> str:
    """Stabilny identyfikator to-do - skrót z jego treści."""
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def _sections(lines: List[str]) -> Dict[str, List[str]]:
    """Zwraca {tytuł sekcji (lower) -> linie treści}."""
    out: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in lines:
        m = _SECTION_RE.match(line)
        if m:
            current = m.group(1).strip().lower()
            out[current] = []
            continue
        if current is not None:
            out[current].append(line)
    return out


def _parse_todos(lines: List[str], today: str) -> List[Dict[str, Any]]:
    """Parsuje checkboxy `- [ ]` z sekcji na listę to-do."""
    todos: List[Dict[str, Any]] = []
    for line in lines:
        m = _TODO_RE.match(line)
        if not m:
            continue
        raw_text = m.group(4).strip()
        done = m.group(2) in _DONE_STATES
        termin = None
        tm = _TERMIN_RE.search(raw_text)
        if tm:
            termin = tm.group(1)
        clean = _TERMIN_RE.sub("", raw_text).strip()
        overdue = bool(termin and termin < today and not done)
        todos.append({
            "key": _todo_key(raw_text),
            "text": plain_text(clean) or plain_text(raw_text),
            "done": done,
            "termin": termin,
            "overdue": overdue,
        })
    return todos


def _parse_projekty(lines: List[str], today: str) -> List[Dict[str, Any]]:
    """Parsuje deliverables z sekcji `## Projekty`."""
    projekty: List[Dict[str, Any]] = []
    for line in lines:
        if _TODO_RE.match(line):  # checkbox to nie projekt
            continue
        m = _BULLET_RE.match(line)
        if not m:
            continue
        body = m.group(1).strip()
        if not body:
            continue
        name = re.split(r"\s+-\s+", body, maxsplit=1)[0].strip()
        etap = None
        em = _ETAP_RE.search(body)
        if em:
            etap = em.group(1).strip().rstrip("-").strip()
        deadline = None
        dm = _DEADLINE_RE.search(body)
        if dm:
            deadline = dm.group(1)
        overdue = bool(deadline and deadline < today)
        days_to = None
        if deadline:
            ds = days_since(deadline)
            if ds is not None:
                days_to = round(-ds)
        projekty.append({
            "name": plain_text(name),
            "etap": etap,
            "deadline": deadline,
            "overdue": overdue,
            "days_to_deadline": days_to,
        })
    return projekty


def _read_client(path: Path, sejf: Path) -> Dict[str, Any]:
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
    sections = _sections(lines)
    projekty = _parse_projekty(sections.get("projekty", []), today)
    todos = _parse_todos(sections.get("do zrobienia", []), today)

    stawka = str(meta.get("stawka") or "").strip() or None
    ostatni = str(meta.get("ostatni_kontakt") or "").strip() or None
    days_contact = round(days_since(ostatni)) if ostatni and days_since(ostatni) is not None else None

    try:
        rel = path.relative_to(sejf).as_posix()
    except ValueError:
        rel = path.name

    return {
        "name": plain_text(name),
        "status": str(meta.get("status") or "").strip().lower() or "aktywny",
        "stawka": stawka,
        "stawka_value": parse_amount(stawka),
        "ostatni_kontakt": ostatni,
        "days_since_contact": days_contact,
        "projekty": projekty,
        "todos": todos,
        "open_todos": len([t for t in todos if not t["done"]]),
        "overdue_projekty": len([p for p in projekty if p["overdue"]]),
        "overdue_todos": len([t for t in todos if t["overdue"]]),
        "file": rel,
    }


# Kolejność statusów w UI - zakończony schodzi na dół.
_STATUS_ORDER = {"aktywny": 0, "pauza": 1, "zakończony": 2, "zakonczony": 2}


def fetch(cfg: Config) -> Block:
    directory = cfg.sejf_path(cfg.get("sources.klienci.dir", "Klienci"))
    if not directory.exists():
        raise FileNotFoundError(f"Brak katalogu klientów: {directory}")

    sejf = cfg.sejf
    clients: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for p in sorted(directory.glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:
            clients.append(_read_client(p, sejf))
        except Exception as exc:  # noqa: BLE001 - jeden zły plik nie kładzie bloku
            skipped.append(p.name)
            logger.warning(f"Klienci: pomijam plik {p.name}: {exc}")
    clients.sort(key=lambda c: (_STATUS_ORDER.get(c["status"], 5), c["name"].lower()))

    active = [c for c in clients if c["status"] == "aktywny"]
    needs_attention = [c for c in clients if c["overdue_projekty"] or c["overdue_todos"]]

    return Block(
        name="klienci",
        data={
            "dir": cfg.get("sources.klienci.dir", "Klienci"),
            "all": clients,
            "active_count": len(active),
            "overdue_count": len(needs_attention),
            "skipped_files": skipped,
        },
        data_as_of=datetime.fromtimestamp(directory.stat().st_mtime).isoformat(timespec="seconds"),
    )


# ── zapis: odhaczanie to-do (wspólne dla klientów i biznesu) ──────────────
def set_task_status(path: Path, key: str, done: bool) -> Dict[str, Any]:
    """Podmienia znacznik `- [ ]`/`- [x]` w linii to-do o podanym kluczu."""
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    target: Optional[Tuple[int, Any]] = None
    for idx, line in enumerate(lines):
        m = _TODO_RE.match(line)
        if m and _todo_key(m.group(4).strip()) == key:
            target = (idx, m)
            break

    if target is None:
        raise KeyError(f"Nie ma to-do o kluczu '{key}' w {path.name}. Odśwież panel.")

    idx, m = target
    mark = "x" if done else " "
    lines[idx] = f"{m.group(1)}{mark}{m.group(3)}{m.group(4)}"

    _backup(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "key": key, "done": done, "text": m.group(4).strip()}


def add_task(path: Path, text: str) -> Dict[str, Any]:
    """Dopisuje to-do na koniec sekcji `## Do zrobienia` (zakłada ją, gdy jej nie ma)."""
    if not text.strip():
        raise ValueError("Zadanie bez treści")
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    new_line = f"- [ ] {text.strip()}"

    section_idx = None
    for idx, line in enumerate(lines):
        m = _SECTION_RE.match(line)
        if m and m.group(1).strip().lower() == "do zrobienia":
            section_idx = idx
            break

    if section_idx is None:
        lines.extend(["", "## Do zrobienia", new_line])
    else:
        end = len(lines)
        for idx in range(section_idx + 1, len(lines)):
            if _SECTION_RE.match(lines[idx]):
                end = idx
                break
        while end > section_idx + 1 and not lines[end - 1].strip():
            end -= 1
        lines.insert(end, new_line)

    _backup(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "key": _todo_key(text.strip()), "text": text.strip()}


def _backup(path: Path) -> None:
    _BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, _BACKUP_DIR / f"{path.stem}.{stamp}.md")
    for old in sorted(_BACKUP_DIR.glob(f"{path.stem}.*.md"))[:-30]:
        old.unlink(missing_ok=True)
