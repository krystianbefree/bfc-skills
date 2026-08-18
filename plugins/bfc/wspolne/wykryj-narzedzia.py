#!/usr/bin/env python3
"""
Wykrywa opcjonalne narzędzia, które pogłębiają działanie skilli BFC.
Cross-platform (stdlib) - działa tak samo na macOS, Linux i Windows, bez basha.

Wypisuje po jednej linii: nazwa=tak|nie. Zawsze kończy kodem 0 - brak narzędzia
to nie błąd. Wartości kluczy nigdy nie są wypisywane.

Uruchamiaj łańcuchem: python3 wykryj-narzedzia.py -> python wykryj-narzedzia.py -> py -3 wykryj-narzedzia.py
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _env_or_dotenv(var: str) -> bool:
    """Zmienna w środowisku albo niepusta w .env w CWD. Wartości nie czytamy do wyjścia."""
    if os.environ.get(var, "").strip():
        return True
    envf = Path.cwd() / ".env"
    if envf.is_file():
        try:
            for line in envf.read_text(encoding="utf-8", errors="replace").splitlines():
                s = line.strip()
                if s.startswith(var):
                    _, _, val = s.partition("=")
                    if val.strip().strip('"').strip("'"):
                        return True
        except OSError:
            pass
    return False


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def main() -> int:
    firecrawl = _has("firecrawl") or _env_or_dotenv("FIRECRAWL_API_KEY")
    apify = _env_or_dotenv("APIFY_TOKEN") or _env_or_dotenv("APIFY_API_TOKEN")
    lighthouse = _has("lighthouse")
    playwright = _has("playwright") or _has("playwright-cli")

    for name, val in (
        ("firecrawl", firecrawl),
        ("apify", apify),
        ("lighthouse", lighthouse),
        ("playwright", playwright),
    ):
        print(f"{name}={'tak' if val else 'nie'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
