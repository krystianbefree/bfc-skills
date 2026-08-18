#!/usr/bin/env python3
"""
Metryki profilu Instagram przez Apify - cross-platform (urllib, nie curl).

Zwraca followers, days_since_last_post, engagement_rate dla jednego handla.
Brak `APIFY_TOKEN` albo błąd -> wypisuje {"skipped": "[do reki]", ...} i kończy
kodem 0. Nigdy nie wywala przebiegu i nigdy nie zmyśla liczby.

Użycie:
  python3 apify_ig.py <username_bez_@>
Token: zmienna środowiskowa APIFY_TOKEN albo linia APIFY_TOKEN=... w .env w CWD.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_ACTOR = "apify~instagram-profile-scraper"
_ENDPOINT = f"https://api.apify.com/v2/acts/{_ACTOR}/run-sync-get-dataset-items"
_TIMEOUT = 90


def _token() -> str:
    tok = os.environ.get("APIFY_TOKEN", "").strip()
    if tok:
        return tok
    # Lekki odczyt jednej zmiennej z .env w CWD, bez zależności zewnętrznych.
    envf = Path.cwd() / ".env"
    if envf.is_file():
        for line in envf.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("APIFY_TOKEN"):
                _, _, val = line.partition("=")
                return val.strip().strip('"').strip("'")
    return ""


def _skip(powod: str) -> int:
    print(json.dumps({"skipped": "[do reki]", "powod": powod}, ensure_ascii=False))
    return 0


def _days_since(ts: object) -> object:
    """Dni od najnowszego posta. Przyjmuje ISO string albo epoch (s)."""
    dt = None
    if isinstance(ts, (int, float)):
        try:
            dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    elif isinstance(ts, str) and ts.strip():
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return round((datetime.now(timezone.utc) - dt).total_seconds() / 86400, 1)


def _first(d: dict, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return None


def fetch(username: str, token: str) -> dict:
    body = json.dumps({"usernames": [username]}).encode("utf-8")
    req = urllib.request.Request(
        f"{_ENDPOINT}?token={token}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        items = json.loads(resp.read().decode("utf-8"))
    if not items or not isinstance(items[0], dict):
        return {"skipped": "[do reki]", "powod": "nieoczekiwany kształt odpowiedzi Apify"}

    p = items[0]
    followers = _first(p, "followersCount", "followers")
    posts = p.get("latestPosts") or p.get("posts") or []

    days = None
    if posts:
        ts = _first(posts[0], "timestamp", "takenAt", "taken_at_timestamp")
        days = _days_since(ts)

    # Engagement rate: średnia (like+comment)/followers z dostępnych postów.
    er = None
    if followers and posts:
        vals = []
        for post in posts[:12]:
            likes = _first(post, "likesCount", "likes") or 0
            comments = _first(post, "commentsCount", "comments") or 0
            try:
                vals.append((float(likes) + float(comments)) / float(followers))
            except (TypeError, ValueError, ZeroDivisionError):
                pass
        if vals:
            er = round(sum(vals) / len(vals), 4)

    return {
        "username": username,
        "followers": followers,
        "days_since_last_post": days,
        "engagement_rate": er,
    }


def main(argv) -> int:
    if len(argv) < 2 or not argv[1].strip():
        return _skip("brak username")
    username = argv[1].strip().lstrip("@")
    token = _token()
    if not token:
        return _skip("brak APIFY_TOKEN")
    try:
        result = fetch(username, token)
    except urllib.error.HTTPError as exc:
        return _skip(f"Apify HTTP {exc.code}")
    except (urllib.error.URLError, TimeoutError) as exc:
        return _skip(f"sieć: {exc}")
    except (ValueError, KeyError, AttributeError, TypeError, IndexError) as exc:
        return _skip(f"nieoczekiwana odpowiedź: {exc}")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
