"""
Adapter połączeń — co Claude ma podpięte i co z tego faktycznie odpowiada.

Trzy warstwy, bo każda ma inne źródło prawdy:

1. **Konektory claude.ai** (Gmail, Notion, Slack…) — żyją po stronie konta,
   lokalnie zostaje lista `claudeAiMcpEverConnected` w `~/.claude.json`
   plus `~/.claude/mcp-needs-auth-cache.json` z tymi, które proszą o logowanie.
2. **Serwery MCP** — z `.mcp.json` projektu. Sprawdzamy, czy komenda w ogóle
   istnieje. Nie odpalamy serwera, więc mówimy „konfiguracja gotowa", a nie
   „działa" — to dwie różne rzeczy i nie udajemy, że wiemy więcej.
3. **Klucze API ze `.env`** — jedyna warstwa, którą da się sprawdzić naprawdę.
   Każdy klucz dostaje lekki, tylko-odczytujący strzał do swojego API.

Wartości kluczy nie wychodzą stąd nigdzie. Do interfejsu idzie nazwa zmiennej
i wynik strzału, nigdy sam klucz.
"""
from __future__ import annotations

import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from engine.config import PROJECT_ROOT, Config
from engine.schema import Block
from engine.util import days_since, to_iso

_TIMEOUT = 8
_CLAUDE_JSON = Path.home() / ".claude.json"
_AUTH_CACHE = Path.home() / ".claude" / "mcp-needs-auth-cache.json"


# ── Rejestr strzałów ──────────────────────────────────────────────────────
# id → (etykieta, zmienna w .env, funkcja budująca request)
# Każdy request musi być lekki i tylko odczytujący. Nic, co zmienia stan.
def _probe_anthropic(key: str) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    return (
        "https://api.anthropic.com/v1/models?limit=1",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
        {},
    )


def _probe_openai(key: str):
    return "https://api.openai.com/v1/models", {"Authorization": f"Bearer {key}"}, {}


def _probe_gemini(key: str):
    return "https://generativelanguage.googleapis.com/v1beta/models", {}, {"key": key}


def _probe_stripe(key: str):
    return "https://api.stripe.com/v1/balance", {"Authorization": f"Bearer {key}"}, {}


def _probe_circle(key: str):
    return (
        "https://app.circle.so/api/admin/v2/community_members",
        {"Authorization": f"Token {key}"},
        {"per_page": 1},
    )


def _probe_sender(key: str):
    return (
        "https://api.sender.net/v2/groups",
        {"Authorization": f"Bearer {key}", "Accept": "application/json"},
        {"limit": 1},
    )


def _probe_apify(key: str):
    return "https://api.apify.com/v2/users/me", {"Authorization": f"Bearer {key}"}, {}


def _probe_resend(key: str):
    return "https://api.resend.com/domains", {"Authorization": f"Bearer {key}"}, {}


def _probe_instagram(key: str):
    return "https://graph.instagram.com/me", {}, {"fields": "id,username", "access_token": key}


def _probe_mailerlite(key: str):
    return (
        "https://connect.mailerlite.com/api/groups",
        {"Authorization": f"Bearer {key}", "Accept": "application/json"},
        {"limit": 1},
    )


def _probe_emailoctopus(key: str):
    return "https://api.emailoctopus.com/lists", {"Authorization": f"Bearer {key}"}, {"limit": 1}


PROBES: Dict[str, Dict[str, Any]] = {
    "anthropic": {"label": "Anthropic (Claude API)", "env": "ANTHROPIC_API_KEY", "build": _probe_anthropic,
                  "uzycie": "generowanie briefingów"},
    "openai": {"label": "OpenAI", "env": "OPENAI_API_KEY", "build": _probe_openai,
               "uzycie": "Whisper (obecnie zastąpiony przez Gemini)"},
    "gemini": {"label": "Google Gemini", "env": "GEMINI_API_KEY", "build": _probe_gemini,
               "uzycie": "transkrypcje i grafiki"},
    "stripe": {"label": "Stripe - Be Free Club", "env": "STRIPE_API_KEY", "build": _probe_stripe,
               "uzycie": "przychód, subskrypcje, past due"},
    "stripe_premiere": {"label": "Stripe - Akademia BeFree", "env": "STRIPE_API_KEY_PREMIERE",
                        "build": _probe_stripe, "uzycie": "premiery"},
    "instagram": {"label": "Instagram Graph API", "env": "INSTAGRAM_ACCESS_TOKEN", "build": _probe_instagram,
                  "uzycie": "rolki, stories, metryki"},
    "circle": {"label": "Circle", "env": "CIRCLE_API_TOKEN", "build": _probe_circle,
               "uzycie": "członkowie klubu, wydarzenia LIVE"},
    "sender": {"label": "Sender.net", "env": "SENDER_API_KEY", "build": _probe_sender,
               "uzycie": "newsletter"},
    "apify": {"label": "Apify", "env": "APIFY_API_TOKEN", "build": _probe_apify,
              "uzycie": "scrape konkurencji"},
    "resend": {"label": "Resend", "env": "RESEND_API_KEY", "build": _probe_resend,
               "uzycie": "wysyłka briefingu na maila"},
    "mailerlite": {"label": "MailerLite", "env": "MAILERLITE_API_KEY", "build": _probe_mailerlite,
                   "uzycie": "stara lista, po migracji do Sendera"},
    "emailoctopus": {"label": "EmailOctopus", "env": "EMAILOCTOPUS_API_KEY", "build": _probe_emailoctopus,
                     "uzycie": "stara lista, po migracji do Sendera"},
}


def _run_probe(probe_id: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """Strzela do jednego API i tłumaczy odpowiedź na status po ludzku."""
    env_name = spec["env"]
    key = os.getenv(env_name, "").strip()

    base = {
        "id": probe_id,
        "label": spec["label"],
        "env": env_name,
        "uzycie": spec.get("uzycie", ""),
        "kind": "api",
    }

    if not key:
        return {**base, "status": "brak", "severity": "warn", "message": f"brak {env_name} w .env"}

    try:
        url, headers, params = spec["build"](key)
        resp = requests.get(url, headers=headers, params=params, timeout=_TIMEOUT)
    except requests.Timeout:
        return {**base, "status": "timeout", "severity": "warn",
                "message": f"brak odpowiedzi w {_TIMEOUT} s"}
    except requests.RequestException as exc:
        return {**base, "status": "blad", "severity": "alarm", "message": f"błąd sieci: {exc}"[:120]}

    if resp.status_code in (200, 201):
        return {**base, "status": "aktywny", "severity": "ok", "message": "odpowiada"}
    if resp.status_code in (401, 403):
        return {**base, "status": "odrzucony", "severity": "alarm",
                "message": f"klucz odrzucony (HTTP {resp.status_code})"}
    if resp.status_code == 429:
        return {**base, "status": "limit", "severity": "warn",
                "message": "klucz działa, ale limit zapytań wyczerpany"}
    return {**base, "status": "nietypowy", "severity": "warn",
            "message": f"HTTP {resp.status_code}"}


# ── Konektory claude.ai ───────────────────────────────────────────────────
def _claude_ai_connectors() -> List[Dict[str, Any]]:
    """Lista konektorów kiedykolwiek podpiętych + te, które proszą o logowanie."""
    connected: List[str] = []
    if _CLAUDE_JSON.exists():
        try:
            data = json.loads(_CLAUDE_JSON.read_text(encoding="utf-8"))
            connected = list(data.get("claudeAiMcpEverConnected") or [])
        except (json.JSONDecodeError, OSError):
            connected = []

    needs_auth: Dict[str, Any] = {}
    if _AUTH_CACHE.exists():
        try:
            needs_auth = json.loads(_AUTH_CACHE.read_text(encoding="utf-8")) or {}
        except (json.JSONDecodeError, OSError):
            needs_auth = {}

    items: List[Dict[str, Any]] = []
    for name in sorted(set(connected) | set(needs_auth)):
        entry = needs_auth.get(name)
        pretty = name.replace("claude.ai ", "")
        if entry:
            stamp = entry.get("timestamp")
            when = to_iso(datetime.fromtimestamp(stamp / 1000)) if stamp else None
            items.append({
                "id": name,
                "label": pretty,
                "kind": "claude_ai",
                "status": "wymaga logowania",
                "severity": "warn",
                "message": "autoryzuj w ustawieniach konektorów na claude.ai",
                "since": when,
            })
        else:
            items.append({
                "id": name,
                "label": pretty,
                "kind": "claude_ai",
                "status": "podpięty",
                "severity": "ok",
                "message": "autoryzowany na koncie claude.ai",
            })
    return items


# ── Serwery MCP ───────────────────────────────────────────────────────────
def _mcp_servers() -> List[Dict[str, Any]]:
    """Serwery z `.mcp.json`. Sprawdzamy dostępność komendy, nie odpalamy ich."""
    path = PROJECT_ROOT / ".mcp.json"
    if not path.exists():
        return []
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [{
            "id": ".mcp.json", "label": ".mcp.json", "kind": "mcp",
            "status": "błąd pliku", "severity": "alarm", "message": f"nieczytelny JSON: {exc}",
        }]

    items: List[Dict[str, Any]] = []
    for name, spec in (config.get("mcpServers") or {}).items():
        command = spec.get("command", "")
        args = spec.get("args") or []
        available = bool(command) and (
            Path(command).is_file() and os.access(command, os.X_OK) or shutil.which(command) is not None
        )
        package = next((a for a in args if not a.startswith("-")), "")
        items.append({
            "id": name,
            "label": name,
            "kind": "mcp",
            "status": "gotowy" if available else "brak komendy",
            "severity": "ok" if available else "alarm",
            # Bez odpalenia serwera nie wiemy, czy wstanie — mówimy tylko tyle, ile wiemy.
            "message": ("konfiguracja gotowa, komenda dostępna" if available
                        else f"nie znaleziono: {command}"),
            "uzycie": package,
        })
    return items


def _ignored(cfg: Config) -> List[str]:
    """Nazwy połączeń, których świadomie nie używamy."""
    return [str(name).strip().lower() for name in (cfg.get("sources.connectors.ignore") or [])]


def _keep(items: List[Dict[str, Any]], ignored: List[str]) -> List[Dict[str, Any]]:
    """Odsiewa pozycje z listy ignorowanych. Porównujemy po nazwie i po id."""
    if not ignored:
        return items
    return [
        item for item in items
        if not any(
            skip in str(item.get("label", "")).lower() or skip in str(item.get("id", "")).lower()
            for skip in ignored
        )
    ]


def fetch(cfg: Config) -> Block:
    enabled: List[str] = cfg.get("sources.connectors.probes", list(PROBES.keys()))
    ignored = _ignored(cfg)
    specs = [
        (pid, PROBES[pid]) for pid in enabled
        if pid in PROBES and not any(
            skip in pid.lower() or skip in PROBES[pid]["label"].lower() for skip in ignored
        )
    ]

    # Wszystkie strzały równolegle — inaczej dwanaście razy po sekundzie
    # zamienia odświeżenie panelu w kilkanaście sekund czekania.
    with ThreadPoolExecutor(max_workers=max(1, len(specs))) as pool:
        api_items = list(pool.map(lambda item: _run_probe(*item), specs))

    claude_items = _keep(_claude_ai_connectors(), ignored)
    mcp_items = _keep(_mcp_servers(), ignored)
    everything = claude_items + mcp_items + api_items

    # Token Instagrama odświeża się sam po 50 dniach — pokazujemy jego wiek
    # przy pozycji Instagrama, żeby nie trzeba było szukać w .env.
    token_age = days_since(os.getenv("INSTAGRAM_TOKEN_REFRESHED_AT", ""))
    if token_age is not None:
        for item in api_items:
            if item["id"] == "instagram":
                item["message"] += f" · token odświeżony {token_age:.0f} dni temu"

    problems = [i for i in everything if i["severity"] in ("warn", "alarm")]

    return Block(
        name="connectors",
        data={
            "claude_ai": claude_items,
            "mcp": mcp_items,
            "api": sorted(api_items, key=lambda i: (i["severity"] != "alarm", i["severity"] != "warn", i["label"])),
            "total": len(everything),
            "active": len([i for i in everything if i["severity"] == "ok"]),
            "problems": problems,
            "problem_count": len(problems),
        },
        data_as_of=to_iso(datetime.now()),
    )
