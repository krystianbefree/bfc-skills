#!/usr/bin/env python3
"""Walidacja repo bfc-skills. Odpalaj przed kazdym pushem.

Sprawdza to, co realnie psuje sie u klubowiczow po instalacji:
manifesty, frontmattery, sciezki wychodzace poza plugin, martwe odwolania
i jakosc jezyka. Konczy sie kodem 1, gdy cokolwiek nie przeszlo.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
PLUGINY = KORZEN / "plugins"

DIAKRYTYKI = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
MYSLNIKI = {"—": "em-dash", "–": "en-dash"}

# Odwolania z tymi znakami to wzorce dla modelu, nie realne sciezki.
PLACEHOLDERY = ("<", "{{", "*", "$(")

# Pliki tworzone dopiero u uzytkownika, w jego sejfie. W repo ich nie ma i byc nie moze.
PLIKI_RUNTIME = {
    "Profil.md", "Config.md", "SKILL.md", "sejf.txt",
    "Pozyskiwanie.md", "Kasa.md", "Do nagrania.md", "Zasięgi.md",
    # Notatki-fundamenty tworzone przez /bfc:start w sejfie uzytkownika.
    "Oferta.md", "Grupa docelowa.md", "Metoda prospectingu.md", "Dowody.md", "Głos.md",
}

KOD_INLINE = re.compile(r"`[^`]*`")

bledy: list[str] = []
ostrzezenia: list[str] = []


def wzgledna(sciezka: Path) -> str:
    return str(sciezka.relative_to(KORZEN))


def bez_kodu(linia: str) -> str:
    """Usuwa kod inline. To, co pokazujemy w backtickach, jest ilustracja reguly,
    a nie jej zlamaniem - inaczej plik opisujacy zakaz myslnikow sam by go lamal."""
    return KOD_INLINE.sub("", linia)


def blad(sciezka: Path, tresc: str) -> None:
    bledy.append(f"{wzgledna(sciezka)}: {tresc}")


def ostrzezenie(sciezka: Path, tresc: str) -> None:
    ostrzezenia.append(f"{wzgledna(sciezka)}: {tresc}")


# --- 1. Manifesty ------------------------------------------------------------


def sprawdz_manifesty() -> None:
    katalog = KORZEN / ".claude-plugin" / "marketplace.json"
    if not katalog.is_file():
        bledy.append("brak .claude-plugin/marketplace.json")
        return

    try:
        dane = json.loads(katalog.read_text(encoding="utf-8"))
    except ValueError as exc:
        blad(katalog, f"niepoprawny JSON: {exc}")
        return

    for pole in ("name", "owner", "plugins"):
        if pole not in dane:
            blad(katalog, f"brak wymaganego pola '{pole}'")

    for wpis in dane.get("plugins", []):
        nazwa = wpis.get("name")
        zrodlo = wpis.get("source")
        if not nazwa or not zrodlo:
            blad(katalog, f"wpis pluginu bez 'name' albo 'source': {wpis}")
            continue

        katalog_pluginu = (KORZEN / str(zrodlo)).resolve()
        if not katalog_pluginu.is_dir():
            blad(katalog, f"plugin '{nazwa}' wskazuje na nieistniejacy katalog {zrodlo}")
            continue

        manifest = katalog_pluginu / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            blad(manifest, "brak plugin.json")
            continue

        try:
            manifest_dane = json.loads(manifest.read_text(encoding="utf-8"))
        except ValueError as exc:
            blad(manifest, f"niepoprawny JSON: {exc}")
            continue

        if manifest_dane.get("name") != nazwa:
            blad(
                manifest,
                f"name='{manifest_dane.get('name')}' nie zgadza sie z wpisem w marketplace ('{nazwa}')",
            )
        if not manifest_dane.get("version"):
            ostrzezenie(manifest, "brak 'version' - klubowicze nie dostana aktualizacji")


def sprawdz_diakrytyki_w_json() -> None:
    for plik in KORZEN.rglob("*.json"):
        if ".git" in plik.parts:
            continue
        tresc = plik.read_text(encoding="utf-8")
        znalezione = sorted(DIAKRYTYKI & set(tresc))
        if znalezione:
            blad(plik, f"polskie znaki w JSON ({''.join(znalezione)}) - psuja sie w UI i terminalach")


# --- 2. Skille ---------------------------------------------------------------


def frontmatter(tresc: str) -> dict[str, str] | None:
    if not tresc.startswith("---"):
        return None
    koniec = tresc.find("\n---", 3)
    if koniec == -1:
        return None
    pola: dict[str, str] = {}
    for linia in tresc[3:koniec].splitlines():
        if ":" in linia and not linia.startswith(" "):
            klucz, _, wartosc = linia.partition(":")
            pola[klucz.strip()] = wartosc.strip()
    return pola


def sprawdz_skille() -> list[Path]:
    skille = sorted(PLUGINY.rglob("skills/*/SKILL.md"))
    if not skille:
        bledy.append("nie znaleziono zadnego SKILL.md")
        return []

    for plik in skille:
        tresc = plik.read_text(encoding="utf-8")
        pola = frontmatter(tresc)
        if pola is None:
            blad(plik, "brak frontmattera")
            continue

        nazwa = pola.get("name")
        opis = pola.get("description")

        if not nazwa:
            blad(plik, "frontmatter bez 'name'")
        elif nazwa != plik.parent.name:
            blad(plik, f"name='{nazwa}' nie zgadza sie z katalogiem '{plik.parent.name}'")

        if not opis:
            blad(plik, "frontmatter bez 'description' - skill nigdy sie sam nie uruchomi")
        elif len(opis) < 80:
            ostrzezenie(plik, "description krotszy niz 80 znakow - model rzadziej po niego siegnie")

    return skille


def katalog_pluginu(plik: Path) -> Path:
    for rodzic in plik.parents:
        if (rodzic / ".claude-plugin" / "plugin.json").is_file():
            return rodzic
    return KORZEN


def sprawdz_sciezki_poza_plugin() -> None:
    """Plugin po instalacji widzi wylacznie swoj katalog. '../' nie zadziala."""
    for plik in PLUGINY.rglob("*.md"):
        for numer, linia in enumerate(plik.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"(?<![.\w])\.\./", bez_kodu(linia)):
                blad(plik, f"linia {numer}: odwolanie '../' wyjdzie poza katalog pluginu")


def sprawdz_odwolania(skille: list[Path]) -> None:
    """Kazdy plik wskazany w SKILL.md i wywiad.md musi istniec."""
    wzorzec = re.compile(r"`([^`\n]+?\.(?:md|sh|py))`")

    do_sprawdzenia = list(skille)
    for skill in skille:
        do_sprawdzenia.extend(
            p for p in (skill.parent / "wywiad.md", skill.parent / "config.template.md") if p.is_file()
        )

    for plik in do_sprawdzenia:
        plugin = katalog_pluginu(plik)
        for odwolanie in set(wzorzec.findall(plik.read_text(encoding="utf-8"))):
            if any(znak in odwolanie for znak in PLACEHOLDERY):
                continue
            if odwolanie in PLIKI_RUNTIME:
                continue

            surowe = odwolanie.replace("${CLAUDE_PLUGIN_ROOT}/", "")
            kandydaci = [
                plugin / surowe,
                plik.parent / surowe,
                KORZEN / surowe,
            ]
            if not any(k.is_file() for k in kandydaci):
                blad(plik, f"odwolanie do nieistniejacego pliku: {odwolanie}")


def sprawdz_komplet_skilli(skille: list[Path]) -> None:
    """Skill dla klubowicza bez wywiadu i szablonu configu to niedokonczony skill."""
    for plik in skille:
        if "bfc-admin" in plik.parts or plik.parent.name == "start":
            continue
        tresc = plik.read_text(encoding="utf-8")
        if "Krok 0" not in tresc:
            blad(plik, "brak sekcji 'Krok 0' - skill nie ma bramki konfiguracyjnej")
        for wymagany in ("wywiad.md", "config.template.md"):
            if not (plik.parent / wymagany).is_file():
                blad(plik, f"brak pliku {wymagany}")


# --- 3. Jezyk ----------------------------------------------------------------


def sprawdz_myslniki() -> None:
    pliki = list(PLUGINY.rglob("*.md")) + [KORZEN / "README.md", KORZEN / "CLAUDE.md"]
    for plik in pliki:
        if not plik.is_file():
            continue
        for numer, linia in enumerate(plik.read_text(encoding="utf-8").splitlines(), 1):
            tresc = bez_kodu(linia)
            for znak, nazwa in MYSLNIKI.items():
                if znak in tresc:
                    blad(plik, f"linia {numer}: {nazwa} '{znak}' - zamien na '-'")


def sprawdz_sentinele() -> None:
    """'TODO:' jest dozwolone wylacznie w szablonach i w opisie mechaniki."""
    dozwolone = {"config.template.md", "profil.template.md", "onboarding.md", "wywiad.md"}
    for plik in PLUGINY.rglob("*.md"):
        if plik.name in dozwolone:
            continue
        tresc = plik.read_text(encoding="utf-8")
        for numer, linia in enumerate(tresc.splitlines(), 1):
            if "TODO:" in bez_kodu(linia):
                ostrzezenie(plik, f"linia {numer}: niedokonczony sentinel TODO:")


# --- Wejscie -----------------------------------------------------------------


def main() -> int:
    sprawdz_manifesty()
    sprawdz_diakrytyki_w_json()
    skille = sprawdz_skille()
    sprawdz_sciezki_poza_plugin()
    sprawdz_odwolania(skille)
    sprawdz_komplet_skilli(skille)
    sprawdz_myslniki()
    sprawdz_sentinele()

    if ostrzezenia:
        print(f"OSTRZEZENIA ({len(ostrzezenia)}):")
        for wpis in ostrzezenia:
            print(f"  ! {wpis}")
        print()

    if bledy:
        print(f"BLEDY ({len(bledy)}):")
        for wpis in bledy:
            print(f"  x {wpis}")
        print("\nWalidacja nie przeszla. Nie pushuj.")
        return 1

    print(f"OK. Skille: {len(skille)}. Bledow: 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
