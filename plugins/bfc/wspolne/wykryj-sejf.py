#!/usr/bin/env python3
"""Wykrywa sejfy Obsidian zarejestrowane w systemie i wypisuje je jako JSON.

Obsidian trzyma liste sejfow w swoim pliku konfiguracyjnym. Czytamy go tylko do odczytu,
zeby zaproponowac uzytkownikowi wybor zamiast kazac mu wklejac sciezke.

Wyjscie: JSON na stdout, np.
  {"znalezione": [{"sciezka": "/Users/x/Sejf", "nazwa": "Sejf", "ostatnio_otwarty": true}]}
Kod wyjscia zawsze 0 - brak sejfow to nie blad, tylko pusta lista.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def sciezki_konfiguracji() -> list[Path]:
    """Lokalizacje obsidian.json na macOS, Windows i Linuksie."""
    dom = Path.home()
    kandydaci = [
        dom / "Library" / "Application Support" / "obsidian" / "obsidian.json",
        dom / ".config" / "obsidian" / "obsidian.json",
        dom / ".var" / "app" / "md.obsidian.Obsidian" / "config" / "obsidian" / "obsidian.json",
    ]
    appdata = os.environ.get("APPDATA")
    if appdata:
        kandydaci.append(Path(appdata) / "obsidian" / "obsidian.json")
    return kandydaci


def zbierz() -> list[dict]:
    znalezione: list[dict] = []
    widziane: set[str] = set()

    for plik in sciezki_konfiguracji():
        if not plik.is_file():
            continue
        try:
            dane = json.loads(plik.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue

        for wpis in (dane.get("vaults") or {}).values():
            sciezka = wpis.get("path")
            if not sciezka or sciezka in widziane:
                continue
            if not Path(sciezka).is_dir():
                continue
            widziane.add(sciezka)
            znalezione.append(
                {
                    "sciezka": sciezka,
                    "nazwa": Path(sciezka).name,
                    "ostatnio_otwarty": bool(wpis.get("open")),
                    "ts": wpis.get("ts") or 0,
                }
            )

    # Najswiezej uzywane na gorze - to prawie zawsze ten sejf, o ktory chodzi.
    znalezione.sort(key=lambda w: (w["ostatnio_otwarty"], w["ts"]), reverse=True)
    for wpis in znalezione:
        wpis.pop("ts", None)
    return znalezione


def main() -> int:
    print(json.dumps({"znalezione": zbierz()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
