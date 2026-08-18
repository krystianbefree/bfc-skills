"""
Adapter zasięgów - statystyki profilu dla tych, którzy publikują treści.

Opcjonalny (włączany z wywiadu: publikujesz regularnie -> ta zakładka wchodzi).
Czyta `<sejf>/Zasięgi.md`: każdy `## Tytuł` to jedna rolka/post, pod nim linie
`zasieg:`, `polubienia:`, `zapisy:` itd. Człowiek wpisuje liczby ręcznie albo mówi
je Claude'owi, a on dopisuje - tak samo jak reszta panelu żyje z Markdownu. Kto ma
token Instagrama, może później podmienić źródło na `instagram` (tryb do dołożenia).

Kształt danych jak w głównym dashboardzie: kafelki (zasięg w oknie, średni zasięg,
liczba postów) + top posty po zasięgu + seria zasięgu kolejnych postów.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timedelta

from engine.config import Config
from engine.schema import Block
from engine.util import days_since, plain_text, to_iso

_H2 = re.compile(r"^##\s+(.+?)\s*$")
_FIELD = re.compile(r"^([a-ząćęłńóśźż_]+)\s*:\s*(.+)$", re.IGNORECASE)

# Synonimy pól - człowiek pisze po swojemu, my rozumiemy.
_ALIAS = {
    "zasieg": "reach", "zasięg": "reach", "reach": "reach", "wyswietlenia": "reach", "wyświetlenia": "reach",
    "polubienia": "likes", "lajki": "likes", "likes": "likes",
    "komentarze": "comments", "komentarzy": "comments", "comments": "comments",
    "udostepnienia": "shares", "udostępnienia": "shares", "shares": "shares", "wyslane": "shares",
    "zapisy": "saves", "saves": "saves", "zapisane": "saves",
    "data": "date", "date": "date",
    "link": "link", "url": "link",
}


def _key(title: str) -> str:
    norm = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return hashlib.sha1(norm.strip().lower().encode("utf-8")).hexdigest()[:10]


def _read(path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def _num(value: str):
    m = re.search(r"-?\d[\d\s.]*", str(value))
    if not m:
        return None
    try:
        return int(re.sub(r"[\s.]", "", m.group(0)))
    except ValueError:
        return None


def _parse(path):
    if not path.exists():
        return []
    out = []
    cur = None
    for line in _read(path).splitlines():
        h = _H2.match(line)
        if h:
            cur = {"title": plain_text(h.group(1)), "key": _key(plain_text(h.group(1))),
                   "reach": None, "likes": 0, "comments": 0, "shares": 0, "saves": 0,
                   "date": None, "link": ""}
            out.append(cur)
            continue
        if cur is None:
            continue
        f = _FIELD.match(line.strip())
        if not f:
            continue
        field = _ALIAS.get(f.group(1).strip().lower())
        if not field:
            continue
        raw = f.group(2).strip()
        if field == "date":
            cur["date"] = to_iso(raw)
        elif field == "link":
            cur["link"] = plain_text(raw)
        else:
            cur[field] = _num(raw) or 0
    return out


def _engagement(p) -> int:
    return int((p.get("likes") or 0) + (p.get("comments") or 0)
               + (p.get("shares") or 0) + (p.get("saves") or 0))


def fetch(cfg: Config) -> Block:
    path = cfg.sejf_path(cfg.get("sources.statystyki.file", "Zasięgi.md"))
    window = int(cfg.get("sources.statystyki.window_days", 30) or 30)
    posts = _parse(path)

    now = datetime.utcnow()
    since = now - timedelta(days=window)

    for p in posts:
        p["engagement"] = _engagement(p)
        p["engagement_rate"] = round(p["engagement"] / p["reach"] * 100, 1) if p.get("reach") else None

    dated = [p for p in posts if p.get("date")]
    in_window = [p for p in dated if p["date"] >= since.isoformat()]
    reaches = [p["reach"] for p in posts if p.get("reach")]
    avg_reach = round(sum(reaches) / len(reaches)) if reaches else 0

    top = sorted([p for p in posts if p.get("reach")], key=lambda p: p["reach"], reverse=True)[:5]
    for p in top:
        p["vs_avg"] = round(p["reach"] / avg_reach, 2) if avg_reach else None

    series = [{"date": (p["date"] or "")[:10], "reach": p.get("reach") or 0}
              for p in sorted(dated, key=lambda p: p["date"])]

    best = max(reaches) if reaches else 0
    latest = max((p["date"] for p in dated), default=None)

    return Block(
        name="statystyki",
        data={
            "window_days": window,
            "total_posts": len(posts),
            "posts_in_window": len(in_window),
            "reach_in_window": sum(p.get("reach") or 0 for p in in_window),
            "avg_reach": avg_reach,
            "best_reach": best,
            "top_posts": top,
            "reach_series": series,
            "last_post_at": latest,
            "days_since_last": int(days_since(latest, now)) if latest else None,
            "has_data": len(posts) > 0,
        },
        data_as_of=to_iso(datetime.fromtimestamp(path.stat().st_mtime)) if path.exists() else None,
    )
