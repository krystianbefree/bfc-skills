"""
Adapter lejka pozyskiwania (`<sejf>/Pozyskiwanie.md`).

Serce panelu freelancera. Źródłem prawdy zostaje Obsidian - panel czyta plik
i punktowo przenosi firmę między etapami (jedna operacja, kopia przed zapisem).

Format pliku (blueprint `pliki-sejfu.md`):
    ## Prospekt
    - [[Firma A]] - dodana 2026-08-10, źródło: research
    ## Oferta
    - [[Firma E]] - oferta 4000 zł, wysłana 2026-08-08

Nagłówek `##` = etap z configu. Jedna linia = jeden prospekt. Adapter czyta:
liczbę pozycji per etap, `wartość:`/`... zł` do wartości lejka, `follow-up:`
do sygnałów. Etap „Klient" tu nie mieszka - klient przechodzi do `Klienci/`.
"""
from __future__ import annotations

import fnmatch
import hashlib
import re
import shutil
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from engine.config import DATA_DIR, Config
from engine.schema import Block
from engine.util import parse_amount, plain_text

_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_FOLLOWUP_RE = re.compile(r"follow-?up:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_VALUE_RE = re.compile(r"warto[śs][ćc]:\s*([~\d][\d  .,]*)", re.IGNORECASE)
_AMOUNT_RE = re.compile(r"([~\d][\d  .,]*)\s*z[łl]", re.IGNORECASE)
_URL_RE = re.compile(r"https?://\S+")

_BACKUP_DIR = DATA_DIR / "sejf_backups"


def _key(title: str) -> str:
    """Stabilny identyfikator firmy - skrót z jej nazwy."""
    norm = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return hashlib.sha1(norm.strip().lower().encode("utf-8")).hexdigest()[:10]


def _stage_by_header(cfg: Config) -> Dict[str, str]:
    """Mapa: znormalizowany nagłówek `##` -> id etapu z configu."""
    lookup: Dict[str, str] = {}
    for stage in cfg.stages:
        lookup[stage["label"].strip().lower()] = stage["id"]
        lookup[str(stage["id"]).strip().lower()] = stage["id"]
    return lookup


def _split_title(text: str) -> Tuple[str, str, Optional[str]]:
    """Rozkłada treść bullet na (tytuł, notatka, link)."""
    link = None
    url = _URL_RE.search(text)
    if url:
        link = url.group(0).rstrip(".,)")

    m = _WIKILINK_RE.match(text.strip())
    if m:
        title = (m.group(2) or m.group(1)).strip()
        rest = text.strip()[m.end():].lstrip(" -–—,").strip()
        return title, rest, link

    # Bez wikilinka: tytuł to część przed pierwszym " - " albo przecinkiem.
    for sep in (" - ", " – ", " — ", ","):
        if sep in text:
            head, _, tail = text.partition(sep)
            return head.strip(), tail.strip(), link
    return text.strip(), "", link


def _parse_item(raw: str, stage_id: str, stage_label: str, today: date) -> Dict[str, Any]:
    """Parsuje jedną linię prospektu do słownika kontraktu."""
    title, note, link = _split_title(raw)

    follow_up = None
    fm = _FOLLOWUP_RE.search(raw)
    if fm:
        follow_up = fm.group(1)

    value = None
    vm = _VALUE_RE.search(raw)
    if vm:
        value = parse_amount(vm.group(1))
    if value is None:
        am = _AMOUNT_RE.search(raw)
        if am:
            value = parse_amount(am.group(1))

    # Data ostatniego ruchu: pierwsza data, która nie jest follow-upem.
    move_date = None
    for d in _DATE_RE.findall(raw):
        if d != follow_up:
            move_date = d
            break
    if move_date is None and not follow_up:
        m = _DATE_RE.search(raw)
        move_date = m.group(1) if m else None

    age = None
    if move_date:
        try:
            age = (today - datetime.strptime(move_date, "%Y-%m-%d").date()).days
        except ValueError:
            age = None

    follow_overdue = bool(follow_up and follow_up < today.isoformat())

    fields: Dict[str, str] = {}
    if value is not None:
        fields["Wartość"] = f"{round(value)} zł"
    if follow_up:
        fields["Follow-up"] = follow_up + (" (zaległy)" if follow_overdue else "")
    if move_date:
        fields["Ostatni ruch"] = move_date
    if note:
        fields["Notatka"] = plain_text(note)

    return {
        "key": _key(title),
        "title": title,
        "stage": stage_id,
        "stage_label": stage_label,
        "note": plain_text(note),
        "date": move_date,
        "link": link,
        "value": value,
        "follow_up": follow_up,
        "follow_up_overdue": follow_overdue,
        "age_days": age,
        "source_ref": None,
        "raw_status": raw.strip(),
        "fields": fields,
        "blocks": [],
        "body_md": "- " + raw.strip(),
    }


def _read_text(path: Path) -> str:
    """Czyta plik, normalizując CRLF/CR do LF - sejf bywa edytowany na różnych OS."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def parse_funnel(path: Path, cfg: Config) -> List[Dict[str, Any]]:
    """
    Czyta plik lejka i zwraca listę prospektów z etapem.

    Odporne na brudny plik: linie, których nie da się sparsować, są pomijane
    (i odnotowane w logu), a nie wywalają całego bloku.
    """
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku lejka: {path}")

    lookup = _stage_by_header(cfg)
    today = date.today()
    items: List[Dict[str, Any]] = []
    current: Optional[str] = None
    skipped = 0

    for line in _read_text(path).splitlines():
        try:
            heading = _HEADING_RE.match(line)
            if heading:
                current = lookup.get(heading.group(1).strip().lower())
                continue
            if current is None:
                continue
            bullet = _BULLET_RE.match(line)
            if not bullet or not bullet.group(1).strip():
                continue
            items.append(_parse_item(bullet.group(1), current, cfg.stage_label(current), today))
        except Exception as exc:  # noqa: BLE001 - jedna zła linia nie kładzie lejka
            skipped += 1
            logger.warning(f"Lejek: pomijam zepsutą linię {line!r}: {exc}")

    if skipped:
        logger.warning(f"Lejek: pominięto {skipped} zepsutych linii w {path.name}.")
    return items


def _funnel_stage_ids(cfg: Config) -> List[str]:
    """Etapy, których wartość realnie może wpaść: Rozmowa i Oferta."""
    out = []
    for stage in cfg.stages:
        label = f"{stage['label']} {stage['id']}".lower()
        if "rozmow" in label or "ofert" in label:
            out.append(stage["id"])
    return out


# ── DOLEWANIE: import z research + cold-mail (skille klubowe) ──────────────
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
_TABLE_SEP_RE = re.compile(r"^:?-{2,}:?$")
_PROSPEKTY_GLOB = "Prospekty *.md"
_RESEARCH_HEADER_CELLS = {"firma", "company", "nazwa", "prospekt"}


def _norm(name: str) -> str:
    """Znormalizowana nazwa firmy do porównań (ascii, lower, zwinięte spacje)."""
    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", norm).strip().lower()


def _clean_company_cell(cell: str) -> Tuple[str, Optional[str]]:
    """Z komórki tabeli wyciąga (nazwa firmy, opcjonalny link)."""
    text = cell.strip()
    link = None
    md = _MD_LINK_RE.search(text)
    if md:
        name = md.group(1).strip()
        link = md.group(2).strip()
        return plain_text(name), link
    url = _URL_RE.search(text)
    if url:
        link = url.group(0).rstrip(".,)")
        text = _URL_RE.sub("", text).strip()
    return plain_text(text), link


_COLDMAIL_PREFIX_RE = re.compile(r"^\s*cold[\s-]*mail\s*:?\s*", re.IGNORECASE)


def _firm_from_stem(stem: str) -> str:
    """Nazwa firmy z nazwy pliku: ucina sufiks ' - ...' i przedrostek 'Cold mail:'."""
    name = stem.split(" - ", 1)[0].strip()
    name = _COLDMAIL_PREFIX_RE.sub("", name).strip()
    return name


def _scan_research(directory: Path) -> List[Dict[str, Any]]:
    """
    Zbiera firmy z folderu research: tabele `Prospekty *.md` (kolumny
    firma|strona|sygnał|ocena|link) oraz notatki per firma (jeden plik = firma).
    Brak folderu -> pusta lista (po cichu).
    """
    out: List[Dict[str, Any]] = []
    seen: set = set()
    if not directory.exists() or not directory.is_dir():
        return out

    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            is_table = fnmatch.fnmatch(path.name, _PROSPEKTY_GLOB)
            if is_table:
                for row in _read_text(path).splitlines():
                    line = row.strip()
                    if not line.startswith("|"):
                        continue
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if not cells or not cells[0]:
                        continue
                    if all(_TABLE_SEP_RE.match(c or "-") for c in cells):
                        continue  # wiersz separatora ---|---
                    if _norm(cells[0]) in _RESEARCH_HEADER_CELLS:
                        continue  # nagłówek tabeli
                    name, link = _clean_company_cell(cells[0])
                    if not link:
                        for c in cells[1:]:
                            u = _URL_RE.search(c)
                            if u:
                                link = u.group(0).rstrip(".,)")
                                break
                    if not name:
                        continue
                    key = _norm(name)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append({"name": name, "link": link})
            else:
                # Notatka per firma: nazwa z H1 albo z nazwy pliku.
                name = path.stem
                for ln in _read_text(path).splitlines():
                    h1 = re.match(r"^#\s+(.+?)\s*$", ln)
                    if h1:
                        name = h1.group(1).strip()
                        break
                name = _COLDMAIL_PREFIX_RE.sub("", name).strip()
                key = _norm(name)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"name": plain_text(name), "link": None})
        except Exception as exc:  # noqa: BLE001 - jeden zły plik nie psuje importu
            logger.warning(f"Import research: pomijam {path.name}: {exc}")

    return out


def _scan_coldmail(directory: Path) -> List[Dict[str, Any]]:
    """Firmy, do których poszedł cold mail: jeden plik = jedna firma."""
    out: List[Dict[str, Any]] = []
    seen: set = set()
    if not directory.exists() or not directory.is_dir():
        return out

    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            name = _firm_from_stem(path.stem)
            if not name:
                continue
            key = _norm(name)
            if key in seen:
                continue
            seen.add(key)
            out.append({"name": plain_text(name)})
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Import cold-mail: pomijam {path.name}: {exc}")

    return out


def _stage_for(cfg: Config, *needles: str) -> Optional[str]:
    """Zwraca id etapu, którego id/label zawiera którykolwiek z `needles`."""
    for stage in cfg.stages:
        hay = f"{stage.get('id', '')} {stage.get('label', '')}".lower()
        if any(n in hay for n in needles):
            return stage["id"]
    return None


def import_from_skills(cfg: Config) -> List[str]:
    """
    DOLEWANIE do `Pozyskiwanie.md` z research i cold-mail. Nigdy nie rzuca
    wyjątkiem (zwraca log tego, co zaimportowano) i nigdy nie cofa firmy do
    wcześniejszego etapu - szanuje ręczne przesunięcia człowieka.

    - Nowa firma z research -> etap Prospekt (dedup po znormalizowanej nazwie).
    - Firma z cold-mail -> co najmniej etap Kontakt + `follow-up:` (config
      `sources.pozyskiwanie.followup_dni`, domyślnie +3 dni).
    - Zapis punktowy (add_item / set_status): jedna linia + kopia przed zapisem.
    """
    imported: List[str] = []
    try:
        path = cfg.sejf_path(cfg.get("sources.pozyskiwanie.file", "Pozyskiwanie.md"))
        if not path.exists():
            return imported

        research_dir = cfg.sejf_path(
            cfg.get("sources.pozyskiwanie.import_research_dir", "BFC Skille/research"))
        coldmail_dir = cfg.sejf_path(
            cfg.get("sources.pozyskiwanie.import_coldmail_dir", "BFC Skille/cold-mail"))
        followup_dni = int(cfg.get("sources.pozyskiwanie.followup_dni", 3) or 3)

        research = _scan_research(research_dir)
        coldmail = _scan_coldmail(coldmail_dir)
        if not research and not coldmail:
            return imported

        prospekt_id = _stage_for(cfg, "prospekt") or (cfg.stage_ids[0] if cfg.stage_ids else "")
        kontakt_id = _stage_for(cfg, "kontakt")
        if not kontakt_id:
            kontakt_id = cfg.stage_ids[1] if len(cfg.stage_ids) > 1 else prospekt_id
        order = {sid: i for i, sid in enumerate(cfg.stage_ids)}
        kontakt_idx = order.get(kontakt_id, 1)

        existing = {_key(it["title"]): it for it in parse_funnel(path, cfg)}
        batch_keys: set = set()
        follow_up = (date.today() + timedelta(days=followup_dni)).isoformat()

        coldmail_keys = {_key(c["name"]) for c in coldmail}

        # 1. Research -> Prospekt (o ile firmy nie ma nigdzie i nie jest cold-mailowana).
        for r in research:
            k = _key(r["name"])
            if k in existing or k in batch_keys or k in coldmail_keys:
                continue
            note = "źródło: research"
            if r.get("link"):
                note += f", {r['link']}"
            try:
                add_item(path, title=r["name"], stage=cfg.stage_label(prospekt_id), note=note)
                batch_keys.add(k)
                imported.append(f"research -> Prospekt: {r['name']}")
            except ValueError:
                pass  # już w lejku - dedup wygrał
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Import: nie dodałem '{r['name']}' do Prospekt: {exc}")

        # 2. Cold-mail -> co najmniej Kontakt + follow-up (nigdy w tył).
        for c in coldmail:
            k = _key(c["name"])
            if k in batch_keys:
                continue
            it = existing.get(k)
            if it is None:
                try:
                    add_item(path, title=c["name"], stage=cfg.stage_label(kontakt_id),
                             note=f"cold mail, follow-up: {follow_up}")
                    batch_keys.add(k)
                    imported.append(f"cold-mail -> Kontakt: {c['name']}")
                except ValueError:
                    pass
                except Exception as exc:  # noqa: BLE001
                    logger.warning(f"Import: nie dodałem '{c['name']}' do Kontakt: {exc}")
            else:
                cur_idx = order.get(it["stage"], 0)
                if cur_idx < kontakt_idx:
                    try:
                        set_status(path, k, cfg.stage_label(kontakt_id),
                                   note=f"cold mail, follow-up: {follow_up}")
                        batch_keys.add(k)
                        imported.append(f"cold-mail -> awans do Kontakt: {c['name']}")
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(f"Import: nie awansowałem '{c['name']}': {exc}")
                # cur_idx >= kontakt_idx: firma już dalej - szanuj ręczny ruch, nic nie robimy.

        if imported:
            logger.info(f"Import lejka: dolałem {len(imported)} pozycji z research/cold-mail.")
    except Exception as exc:  # noqa: BLE001 - import nigdy nie kładzie bloku
        logger.warning(f"Import lejka pominięty (błąd): {exc}")
    return imported


def fetch(cfg: Config) -> Block:
    """Buduje blok POZYSKIWANIE w kontrakcie kanbana."""
    path = cfg.sejf_path(cfg.get("sources.pozyskiwanie.file", "Pozyskiwanie.md"))
    imported = import_from_skills(cfg)
    items = parse_funnel(path, cfg)

    by_stage: Dict[str, List[Dict[str, Any]]] = {sid: [] for sid in cfg.stage_ids}
    for item in items:
        by_stage.setdefault(item["stage"], []).append(item)

    counts = {sid: len(by_stage.get(sid, [])) for sid in by_stage}

    value_stages = _funnel_stage_ids(cfg)
    funnel_value = round(
        sum(i["value"] or 0 for sid in value_stages for i in by_stage.get(sid, []))
    )

    overdue_followups = [i for i in items if i["follow_up_overdue"]]
    stale_prog = int(cfg.get("signals.dni_bez_ruchu_lejek", 14))
    stale_leads = [i for i in items if (i["age_days"] or 0) > stale_prog]

    return Block(
        name="pozyskiwanie",
        data={
            "file": cfg.get("sources.pozyskiwanie.file", "Pozyskiwanie.md"),
            "unit": cfg.get("pipeline.unit", "prospekt"),
            "unit_plural": cfg.get("pipeline.unit_plural", "prospekty"),
            "by_stage": by_stage,
            "counts": counts,
            "total": len(items),
            "funnel_value": funnel_value,
            "overdue_followups": overdue_followups,
            "stale_leads": stale_leads,
            "imported": imported,
        },
        data_as_of=datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    )


# ── zapis: przeniesienie firmy między etapami ─────────────────────────────
def set_status(path: Path, key: str, new_stage: str, note: str = "") -> Dict[str, Any]:
    """
    Przenosi firmę o kluczu `key` do sekcji `new_stage`.

    Fizycznie relokuje jedną linię: usuwa ją z bieżącego etapu i dopisuje na
    końcu docelowego, aktualizując datę ostatniego ruchu. Kopia przed zapisem.
    """
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku lejka: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()

    # Zbuduj mapę nagłówek->indeks i granice sekcji.
    headers: List[Tuple[int, str]] = [
        (i, m.group(1).strip()) for i, line in enumerate(lines)
        if (m := _HEADING_RE.match(line))
    ]
    if not headers:
        raise ValueError("Plik lejka nie ma żadnego nagłówka etapu (`## ...`).")

    # Znajdź linię firmy.
    src_idx: Optional[int] = None
    for i, line in enumerate(lines):
        bullet = _BULLET_RE.match(line)
        if not bullet:
            continue
        title, _, _ = _split_title(bullet.group(1))
        if _key(title) == key:
            src_idx = i
            break
    if src_idx is None:
        raise KeyError(f"Nie ma firmy o kluczu '{key}' w {path.name}. Odśwież panel.")

    # Docelowy nagłówek: dopasuj po etykiecie/id (bez wielkości liter).
    target_label = new_stage.strip().lower()
    target_header_idx: Optional[int] = None
    for idx, htext in headers:
        if htext.lower() == target_label:
            target_header_idx = idx
            break
    if target_header_idx is None:
        raise ValueError(f"Brak sekcji etapu „{new_stage}” w {path.name}.")

    # Zaktualizuj datę ruchu w przenoszonej linii.
    original = lines[src_idx]
    stamp = date.today().isoformat()
    if _DATE_RE.search(original):
        moved = _DATE_RE.sub(stamp, original, count=1)
    else:
        moved = original.rstrip() + f", ruch {stamp}"
    if note.strip():
        moved = moved.rstrip() + f" ({note.strip()})"

    lines.pop(src_idx)
    # Nagłówek mógł się przesunąć po usunięciu linii nad nim.
    if src_idx < target_header_idx:
        target_header_idx -= 1

    # Koniec sekcji docelowej = następny nagłówek albo EOF, cofnięty nad puste.
    section_end = len(lines)
    for idx, _ in headers:
        pos = idx if idx <= src_idx else idx - 1
        if pos > target_header_idx:
            section_end = min(section_end, pos)
    insert_at = section_end
    while insert_at > target_header_idx + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1

    lines.insert(insert_at, moved)

    _backup(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    title, _, _ = _split_title(_BULLET_RE.match(moved).group(1))
    return {"ok": True, "key": key, "title": title, "stage": new_stage}


def add_item(path: Path, title: str, stage: str = "", note: str = "", value: str = "") -> Dict[str, Any]:
    """Dopisuje nową firmę na koniec danego etapu (domyślnie pierwszy z pliku)."""
    if not title.strip():
        raise ValueError("Prospekt bez nazwy")
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku lejka: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    headers = [(i, m.group(1).strip()) for i, line in enumerate(lines) if (m := _HEADING_RE.match(line))]
    if not headers:
        raise ValueError("Plik lejka nie ma żadnego nagłówka etapu.")

    # Dedup po nazwie.
    for line in lines:
        b = _BULLET_RE.match(line)
        if b:
            t, _, _ = _split_title(b.group(1))
            if _key(t) == _key(title):
                raise ValueError(f'„{title.strip()}" jest już w lejku')

    want = stage.strip().lower()
    header_idx = headers[0][0]
    for idx, htext in headers:
        if htext.lower() == want:
            header_idx = idx
            break

    section_end = len(lines)
    for idx, _ in headers:
        if idx > header_idx:
            section_end = min(section_end, idx)
    insert_at = section_end
    while insert_at > header_idx + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1

    stamp = date.today().isoformat()
    parts = [f"[[{title.strip()}]]", f"dodana {stamp}"]
    line = f"- {parts[0]} - {parts[1]}"
    if value.strip():
        line += f", wartość: {value.strip()}"
    if note.strip():
        line += f", {note.strip()}"

    lines.insert(insert_at, line)
    _backup(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "key": _key(title), "title": title.strip()}


def _backup(path: Path) -> None:
    _BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, _BACKUP_DIR / f"{path.stem}.{stamp}.md")
    for old in sorted(_BACKUP_DIR.glob(f"{path.stem}.*.md"))[:-30]:
        old.unlink(missing_ok=True)
