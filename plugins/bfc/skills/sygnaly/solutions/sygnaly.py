#!/usr/bin/env python3
"""
Silnik /bfc:sygnaly - lista obserwowanych firm, tanie sondy, pamięć zmian i uczenie.

Zasada: model nie czyta stron ani rejestrów "na wszelki wypadek". Skrypt odpytuje
tanie źródła (API KRS, strona firmy z sitemapą i narzędziami, archiwum internetu,
opcjonalnie Apify i Meta), porównuje z tym, co widział ostatnio, i oddaje modelowi
WYŁĄCZNIE zmiany. Brak zmian = zero tokenów. Przy pierwszym odczycie firmy skrypt
sięga w przeszłość (historia KRS, archiwum strony, daty opinii i ogłoszeń), więc
sygnały widać od pierwszego skanu, bez czekania na drugi.

Źródła, których nie da się odpytać skryptem (ogłoszenia o pracę bez danych
strukturalnych, Baza Konkurencyjności, LinkedIn), model zbiera sam i przekazuje
komendą `obserwacja` - skrypt pamięta, co już widział.

Tylko biblioteka standardowa. Działa na Mac, Linux i Windows.
Uruchamiaj łańcuchem: python3 -> python -> py -3.

Komendy (DIR = <sejf>/BFC Skille/sygnaly):
  init DIR
  dodaj DIR <plik.json>                  firma albo lista firm (opcjonalnie z polem "sygnaly")
  lista DIR
  plan DIR [--tryb lekki|pelny|auto] [--limit N] [--dzis RRRR-MM-DD]
  sonda DIR ID krs|strona|opinie|instagram|reklamy
  obserwacja DIR ID praca|baza|linkedin|inne <plik.json>
  sygnal DIR ID <plik.json>              zapis potwierdzonego sygnału
  ocena DIR [--dzis RRRR-MM-DD]          priorytety (wagi + uczenie) i sygnały branżowe
  status DIR ID obserwuj|nie-teraz|porzucona|napisano|skreslona [--do RRRR-MM-DD] [--powod TEKST]
  wynik DIR ID odpisali|spotkanie|klient|cisza
  skutecznosc DIR                        które sygnały dają odpowiedzi
  uzupelnij DIR ID <plik.json>           dopisz brakujące pola (krs, google_maps, instagram...)
  kontakt-dodaj DIR <plik.json>
  kontakt-obserwacja DIR ID <plik.json>
  linkedin-import DIR <Connections.csv>  zmiany pracy w sieci kontaktów z eksportu LinkedIna
  panel DIR <Pozyskiwanie.md> [--etap NAZWA]   firmy z priorytetem do lejka panelu
  render DIR

Każda komenda wypisuje jeden obiekt JSON na stdout i kończy się kodem 0, także
przy błędzie sieci (wtedy {"skipped": "[do reki]", "powod": ...}). Nigdy nie
zmyśla wartości.

Klucze (zmienne środowiskowe albo .env w bieżącym katalogu):
  APIFY_TOKEN albo APIFY_API_TOKEN   sondy opinie i instagram
  META_ADLIB_TOKEN                   sonda reklamy (Meta Ad Library API)
"""
from __future__ import annotations

import csv
import difflib
import hashlib
import html.parser
import importlib.util
import json
import os
import re
import shutil
import ssl
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

WERSJA = 2
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
TIMEOUT = 25
RODZINY = {"wzrost", "zmiana", "bol", "intencja", "kalendarz", "niespojnosc", "nie"}
STATUSY = {"obserwuj", "nie-teraz", "porzucona", "napisano", "skreslona"}
WYNIKI = {"odpisali", "spotkanie", "klient", "cisza"}
POZYTYWNE_WYNIKI = {"odpisali", "spotkanie", "klient"}

DOMYSLNE = {
    "limit_na_skan": 15,
    "okno_priorytetu_dni": 21,
    "prog_priorytetu": 2.0,          # suma wag sygnałów w oknie
    "przeglad_po_dniach": 90,
    "waznosc_sygnalu_dni": 90,
    "opinie_max_na_firme": 30,
    "kontakty_co_dni": 30,
    "tryb_domyslny": "auto",         # auto = lekki, a pełny co pelny_co_dni
    "pelny_co_dni": 28,
    "archiwum_strony": True,         # porównanie z wersją sprzed ~90 dni przy pierwszym odczycie
    "branzowy_min_firm": 3,
    "wylaczanie_po_dniach": 90,
    "wylaczanie_min_uruchomien": 10,
    "wagi": {"wzrost": 1.0, "zmiana": 1.0, "bol": 1.0, "intencja": 1.5,
             "kalendarz": 0.5, "niespojnosc": 1.5, "nie": 0.0},
    "sondy": {
        # koszt: darmowa = skrypt, zero tokenów; platna = Apify; model = szuka model (tokeny)
        "krs":       {"wlaczona": True,  "co_dni": 7,  "koszt": "darmowa"},
        "strona":    {"wlaczona": True,  "co_dni": 7,  "koszt": "darmowa"},
        "praca":     {"wlaczona": True,  "co_dni": 14, "koszt": "model"},
        "reklamy":   {"wlaczona": True,  "co_dni": 14, "koszt": "darmowa"},
        "opinie":    {"wlaczona": True,  "co_dni": 30, "koszt": "platna"},
        "instagram": {"wlaczona": True,  "co_dni": 30, "koszt": "platna"},
        "baza":      {"wlaczona": True,  "co_dni": 30, "koszt": "model"},
        "linkedin":  {"wlaczona": False, "co_dni": 30, "koszt": "model"},
    },
}


# --- narzędzia ogólne --------------------------------------------------------


def wypisz(obj: dict) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows: konsola cp1250
    except (AttributeError, ValueError):
        pass
    print(json.dumps(obj, ensure_ascii=False, indent=1))
    return 0


def pomin(powod: str, **extra) -> int:
    return wypisz({"skipped": "[do reki]", "powod": powod, **extra})


def dzis_z(args: list[str]) -> date:
    v = opcja(args, "--dzis")
    return date.fromisoformat(v) if v else date.today()


def opcja(args: list[str], nazwa: str, domyslna=None):
    if nazwa in args:
        i = args.index(nazwa)
        if i + 1 < len(args):
            return args[i + 1]
    return domyslna


def pozycyjne(args: list[str]) -> list[str]:
    out, pomin_nast = [], False
    for a in args:
        if pomin_nast:
            pomin_nast = False
            continue
        if a.startswith("--"):
            pomin_nast = True
            continue
        out.append(a)
    return out


def wczytaj_json_arg(arg: str):
    """Przyjmuje ścieżkę do pliku (bezpieczniej na Windows) albo JSON wprost."""
    a = arg[1:] if arg.startswith("@") else arg
    if len(a) < 500 and Path(a).is_file():
        return json.loads(Path(a).read_text(encoding="utf-8"))
    return json.loads(arg)


def zapisz_atomowo(sciezka: Path, tresc: str) -> None:
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    tmp = sciezka.with_suffix(sciezka.suffix + ".tmp")
    tmp.write_text(tresc, encoding="utf-8")
    os.replace(tmp, sciezka)


def slug(tekst: str) -> str:
    t = str(tekst or "").lower().replace("ł", "l")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60]


def domena(url: str) -> str:
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    host = urllib.parse.urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def cyfry(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


def dni_od(iso: str | None, dzis: date) -> int | None:
    if not iso:
        return None
    try:
        return (dzis - date.fromisoformat(str(iso)[:10])).days
    except ValueError:
        return None


def token(*nazwy: str) -> str:
    for n in nazwy:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    envf = Path.cwd() / ".env"
    if envf.is_file():
        for linia in envf.read_text(encoding="utf-8", errors="replace").splitlines():
            linia = linia.strip()
            for n in nazwy:
                if linia.startswith(n + "="):
                    return linia.partition("=")[2].strip().strip('"').strip("'")
    return ""


def pobierz(url: str, *, dane: bytes | None = None, naglowki: dict | None = None,
            timeout: int = TIMEOUT, max_bajtow: int = 4_000_000,
            bez_weryfikacji_ssl: bool = False) -> tuple[int, str, str]:
    h = {"User-Agent": UA, "Accept-Language": "pl,en;q=0.8"}
    h.update(naglowki or {})
    req = urllib.request.Request(url, data=dane, headers=h, method="POST" if dane else "GET")
    ctx = ssl._create_unverified_context() if bez_weryfikacji_ssl else None
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        surowe = r.read(max_bajtow)
        kod = r.status
        finalny = r.geturl()
        charset = r.headers.get_content_charset() or "utf-8"
    return kod, surowe.decode(charset, errors="replace"), finalny


def pobierz_strone(url: str, **kw) -> tuple[int, str, str, bool]:
    """Jak pobierz, ale przy błędzie certyfikatu ponawia bez weryfikacji (czytamy tylko publiczne strony)."""
    try:
        kod, txt, fin = pobierz(url, **kw)
        return kod, txt, fin, False
    except urllib.error.URLError as e:
        if not isinstance(getattr(e, "reason", None), ssl.SSLError):
            raise
        kod, txt, fin = pobierz(url, bez_weryfikacji_ssl=True, **kw)
        return kod, txt, fin, True


def _iso(s) -> str | None:
    s = str(s or "").strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else None


# --- magazyn -----------------------------------------------------------------


class Magazyn:
    def __init__(self, katalog: str):
        self.dir = Path(katalog)
        self.plik = self.dir / "obserwowane.json"
        self.stan_dir = self.dir / "stan"
        if self.plik.is_file():
            self.dane = json.loads(self.plik.read_text(encoding="utf-8"))
        else:
            self.dane = {"wersja": WERSJA, "firmy": [], "kontakty": []}
        for k, v in (("firmy", []), ("kontakty", []), ("sondy_stat", {}), ("siec", {})):
            self.dane.setdefault(k, v)
        self.ust = self._ustawienia()

    def _ustawienia(self) -> dict:
        u = json.loads(json.dumps(DOMYSLNE))
        p = self.dir / "ustawienia.json"
        if p.is_file():
            try:
                wlasne = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                wlasne = {}
            for k, v in wlasne.items():
                if k in ("sondy", "wagi") and isinstance(v, dict):
                    for s, cfg in v.items():
                        if k == "sondy" and isinstance(cfg, dict):
                            u["sondy"].setdefault(s, {}).update(cfg)
                        elif k == "wagi":
                            u["wagi"][s] = cfg
                else:
                    u[k] = v
        return u

    def zapisz(self) -> None:
        zapisz_atomowo(self.plik, json.dumps(self.dane, ensure_ascii=False, indent=1))

    def firma(self, ident: str) -> dict | None:
        return next((f for f in self.dane["firmy"] if f["id"] == ident), None)

    def stan(self, ident: str) -> dict:
        p = self.stan_dir / f"{ident}.json"
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def zapisz_stan(self, ident: str, stan: dict) -> None:
        zapisz_atomowo(self.stan_dir / f"{ident}.json", json.dumps(stan, ensure_ascii=False, indent=1))

    def policz_uruchomienie(self, sonda: str, dzis: date) -> None:
        st = self.dane["sondy_stat"].setdefault(sonda, {"od": dzis.isoformat(), "uruchomienia": 0})
        st["uruchomienia"] = st.get("uruchomienia", 0) + 1


# --- komendy: lista ----------------------------------------------------------


def k_init(m: Magazyn, args, dzis) -> int:
    m.dir.mkdir(parents=True, exist_ok=True)
    m.stan_dir.mkdir(parents=True, exist_ok=True)
    if not m.plik.is_file():
        m.zapisz()
    return wypisz({"ok": True, "katalog": str(m.dir), "firm": len(m.dane["firmy"])})


def _klucze_duplikatu(f: dict) -> set[str]:
    k = {"nazwa:" + slug(f.get("nazwa", ""))}
    if f.get("strona"):
        k.add("dom:" + domena(f["strona"]))
    if cyfry(f.get("krs")):
        k.add("krs:" + cyfry(f["krs"]).zfill(10))
    if cyfry(f.get("nip")):
        k.add("nip:" + cyfry(f["nip"]))
    return k


POLA_FIRMY = ("nazwa", "strona", "krs", "nip", "instagram", "google_maps", "linkedin",
              "miasto", "branza", "segment", "zrodlo", "notatka", "score")


def _waliduj_sygnal(s: dict, dzis: date) -> tuple[dict | None, str]:
    rodz = s.get("rodzina")
    if rodz not in RODZINY or not s.get("sygnal"):
        return None, f"rodzina musi byc z {sorted(RODZINY)} + pole sygnal"
    if not s.get("zrodlo_url") and rodz != "kalendarz":
        return None, "brak zrodlo_url - sygnal bez zrodla nie wchodzi"
    wpis = {"data": (_iso(s.get("data")) or dzis.isoformat()), "rodzina": rodz,
            "sygnal": s["sygnal"], "opis": s.get("opis", ""), "zrodlo_url": s.get("zrodlo_url", ""),
            "sonda": s.get("sonda", ""), "typ": s.get("typ", ""), "dodano": dzis.isoformat()}
    if s.get("waga") is not None:
        try:
            wpis["waga"] = float(s["waga"])
        except (TypeError, ValueError):
            pass
    return wpis, ""


def k_dodaj(m: Magazyn, args, dzis) -> int:
    wejscie = wczytaj_json_arg(args[0])
    lista = wejscie if isinstance(wejscie, list) else [wejscie]
    istniejace = {}
    for f in m.dane["firmy"]:
        for k in _klucze_duplikatu(f):
            istniejace[k] = f
    dodane, pominiete = [], []
    for nowa in lista:
        if not isinstance(nowa, dict) or not str(nowa.get("nazwa", "")).strip():
            pominiete.append({"wejscie": nowa, "powod": "brak nazwy"})
            continue
        trafienie = next((istniejace[k] for k in _klucze_duplikatu(nowa) if k in istniejace), None)
        if trafienie:
            pominiete.append({"nazwa": nowa["nazwa"], "id": trafienie["id"],
                              "powod": f"juz na liscie (status: {trafienie['status']})"})
            continue
        ident = slug(nowa["nazwa"]) or "firma"
        baza, n = ident, 2
        while m.firma(ident):
            ident = f"{baza}-{n}"
            n += 1
        f = {p: nowa.get(p) for p in POLA_FIRMY if nowa.get(p) not in (None, "")}
        if f.get("krs"):
            f["krs"] = cyfry(f["krs"]).zfill(10)
        f.update({"id": ident, "dodano": nowa.get("dodano") or dzis.isoformat(),
                  "status": "obserwuj", "ostatni_skan": None, "sondy": {}, "sygnaly": []})
        odrzucone = []
        for s in nowa.get("sygnaly") or []:  # firmy znalezione trybem "szukaj" przychodzą z sygnałem
            wpis, powod = _waliduj_sygnal(s, dzis)
            if wpis:
                f["sygnaly"].append(wpis)
            else:
                odrzucone.append(powod)
        m.dane["firmy"].append(f)
        for k in _klucze_duplikatu(f):
            istniejace[k] = f
        dodane.append({"id": ident, "nazwa": f["nazwa"], "sygnaly": len(f["sygnaly"]),
                       **({"sygnaly_odrzucone": odrzucone} if odrzucone else {})})
    m.zapisz()
    return wypisz({"dodane": dodane, "pominiete": pominiete, "razem_na_liscie": len(m.dane["firmy"])})


def k_uzupelnij(m: Magazyn, args, dzis) -> int:
    f = m.firma(args[0])
    if not f:
        return pomin("nie ma takiej firmy", id=args[0])
    pola = wczytaj_json_arg(args[1])
    zmienione = {}
    for p, v in pola.items():
        if p in POLA_FIRMY and v not in (None, ""):
            f[p] = cyfry(v).zfill(10) if p == "krs" else v
            zmienione[p] = f[p]
    m.zapisz()
    return wypisz({"id": f["id"], "uzupelnione": zmienione})


def _aktywne(f: dict, dzis: date, waznosc: int) -> list[dict]:
    out = []
    for s in f.get("sygnaly", []):
        d = dni_od(s.get("data"), dzis)
        if d is not None and d <= waznosc:
            out.append(s)
    return out


def k_lista(m: Magazyn, args, dzis) -> int:
    waz = m.ust["waznosc_sygnalu_dni"]
    wiersze, licz = [], {}
    for f in m.dane["firmy"]:
        akt = [s for s in _aktywne(f, dzis, waz) if s.get("rodzina") != "nie"]
        wiersze.append({"id": f["id"], "nazwa": f["nazwa"], "status": f["status"],
                        "status_do": f.get("status_do"), "dodano": f["dodano"],
                        "ostatni_skan": f.get("ostatni_skan"), "aktywne_sygnaly": len(akt),
                        "notatka": f.get("notatka")})
        licz[f["status"]] = licz.get(f["status"], 0) + 1
    return wypisz({"firmy": wiersze, "statusy": licz, "kontakty": len(m.dane["kontakty"]),
                   "siec_linkedin": len(m.dane["siec"])})


# --- plan skanu --------------------------------------------------------------


def _sonda_mozliwa(nazwa: str, f: dict) -> bool:
    return {
        "krs": bool(f.get("krs")),
        "strona": bool(f.get("strona")),
        "opinie": bool(f.get("google_maps") or f.get("miasto")),
        "instagram": bool(f.get("instagram")),
        "linkedin": bool(f.get("linkedin")),
    }.get(nazwa, True)  # praca, baza, reklamy: wystarczy nazwa


def _koszt(m: Magazyn, sonda: str) -> str:
    typ = m.ust["sondy"].get(sonda, {}).get("koszt", "model")
    if sonda == "reklamy" and not token("META_ADLIB_TOKEN"):
        return "model"
    return typ


def _propozycje_wylaczenia(m: Magazyn, dzis: date) -> list[dict]:
    po, minimum = m.ust["wylaczanie_po_dniach"], m.ust["wylaczanie_min_uruchomien"]
    out = []
    for sonda, cfg in m.ust["sondy"].items():
        if not cfg.get("wlaczona"):
            continue
        st = m.dane["sondy_stat"].get(sonda) or {}
        if (dni_od(st.get("od"), dzis) or 0) < po or st.get("uruchomienia", 0) < minimum:
            continue
        trafione = sum(1 for f in m.dane["firmy"] for s in f.get("sygnaly", [])
                       if s.get("sonda") == sonda and (dni_od(s.get("data"), dzis) or 10**6) <= po)
        if trafione == 0:
            out.append({"sonda": sonda, "uruchomien": st["uruchomienia"], "od": st["od"],
                        "koszt": _koszt(m, sonda),
                        "powod": f"{st['uruchomienia']} uruchomien, zero zapisanych sygnalow w {po} dni"})
    return out


def k_plan(m: Magazyn, args, dzis) -> int:
    ust = m.ust
    limit = int(opcja(args, "--limit", ust["limit_na_skan"]))
    tryb = opcja(args, "--tryb", ust.get("tryb_domyslny", "auto"))
    if tryb == "auto":
        od_pelnego = dni_od(m.dane.get("ostatni_pelny"), dzis)
        tryb = "pelny" if od_pelnego is None or od_pelnego >= ust["pelny_co_dni"] else "lekki"
    if tryb == "pelny":
        m.dane["ostatni_pelny"] = dzis.isoformat()

    wrocily = []
    for f in m.dane["firmy"]:
        if f["status"] == "nie-teraz" and f.get("status_do") and f["status_do"] <= dzis.isoformat():
            f["status"] = "obserwuj"
            wrocily.append({"id": f["id"], "nazwa": f["nazwa"], "bylo_do": f.pop("status_do")})

    kandydaci = []
    for f in m.dane["firmy"]:
        if f["status"] != "obserwuj":
            continue
        sondy, braki = [], []
        for nazwa, cfg in ust["sondy"].items():
            if not cfg.get("wlaczona"):
                continue
            if tryb == "lekki" and _koszt(m, nazwa) != "darmowa":
                continue
            if not _sonda_mozliwa(nazwa, f):
                braki.append(nazwa)
                continue
            d = dni_od(f["sondy"].get(nazwa), dzis)
            if d is None or d >= int(cfg.get("co_dni", 7)):
                sondy.append(nazwa)
        if sondy:
            kandydaci.append({"id": f["id"], "nazwa": f["nazwa"], "sondy": sondy,
                              "brak_danych_do": braki, "pierwszy_odczyt": not f.get("ostatni_skan"),
                              "_skan": f.get("ostatni_skan") or ""})
    kandydaci.sort(key=lambda k: k["_skan"])  # najdawniej skanowane najpierw
    do_skanu = kandydaci[:limit]
    for k in do_skanu:
        k.pop("_skan")

    koszty = {"darmowe": 0, "platne_apify": 0, "model": 0}
    for k in do_skanu:
        for s in k["sondy"]:
            koszty[{"darmowa": "darmowe", "platna": "platne_apify"}.get(_koszt(m, s), "model")] += 1

    kontakty = [] if tryb == "lekki" else [
        {"id": c["id"], "imie": c.get("imie"), "firma": c.get("firma")}
        for c in m.dane["kontakty"]
        if (dni_od(c.get("ostatni_skan"), dzis) or 10**6) >= ust["kontakty_co_dni"]
    ]
    m.zapisz()
    return wypisz({
        "dzis": dzis.isoformat(), "tryb": tryb,
        "do_skanu": do_skanu,
        "pominiete_przez_limit": max(0, len(kandydaci) - limit),
        "koszty": koszty,
        "klucze": {"apify": bool(token("APIFY_TOKEN", "APIFY_API_TOKEN")),
                   "meta": bool(token("META_ADLIB_TOKEN"))},
        "przeglad": _przeglad(m, dzis),
        "wrocily_z_nie_teraz": wrocily,
        "kontakty_do_sprawdzenia": kontakty,
        "propozycje_wylaczenia_sond": _propozycje_wylaczenia(m, dzis),
        "linkedin_ostatni_import": m.dane.get("siec_import"),
    })


def _przeglad(m: Magazyn, dzis: date, ile: int = 10) -> list[dict]:
    po = m.ust["przeglad_po_dniach"]
    out = []
    for f in m.dane["firmy"]:
        if f["status"] != "obserwuj" or f.get("sygnaly"):
            continue
        wiek = dni_od(f["dodano"], dzis) or 0
        od_przegladu = dni_od(f.get("przeglad_ostatni"), dzis)
        if wiek >= po and (od_przegladu is None or od_przegladu >= po):
            out.append({"id": f["id"], "nazwa": f["nazwa"], "dodano": f["dodano"], "dni": wiek,
                        "notatka": f.get("notatka"), "score": f.get("score")})
    out.sort(key=lambda x: x["dodano"])
    return out[:ile]


# --- statusy, wyniki, skuteczność ------------------------------------------


def k_status(m: Magazyn, args, dzis) -> int:
    f = m.firma(args[0])
    if not f:
        return pomin("nie ma takiej firmy", id=args[0])
    nowy = args[1]
    if nowy not in STATUSY:
        return pomin(f"nieznany status: {nowy}", dozwolone=sorted(STATUSY))
    if nowy == "nie-teraz":
        do = opcja(args, "--do")
        if not do:
            return pomin("nie-teraz wymaga --do RRRR-MM-DD")
        f["status_do"] = do
    else:
        f.pop("status_do", None)
    if nowy == "obserwuj":
        f["przeglad_ostatni"] = dzis.isoformat()
    if nowy == "napisano":
        # Zdjęcie sygnałów w chwili wysyłki - z tego uczy się `skutecznosc`.
        akt = [s for s in _aktywne(f, dzis, m.ust["waznosc_sygnalu_dni"]) if s["rodzina"] != "nie"]
        f["wyslano"] = {"data": dzis.isoformat(), "z_sygnalem": bool(akt),
                        "rodziny": sorted({s["rodzina"] for s in akt}),
                        "klucze": sorted({_klucz_sygnalu(s) for s in akt})}
        f.pop("wynik", None)
    powod = opcja(args, "--powod")
    if powod:
        f["powod"] = powod
    f["status"] = nowy
    f["status_zmieniony"] = dzis.isoformat()
    m.zapisz()
    return wypisz({"id": f["id"], "status": nowy, "status_do": f.get("status_do"),
                   "wyslano": f.get("wyslano") if nowy == "napisano" else None})


def k_wynik(m: Magazyn, args, dzis) -> int:
    f = m.firma(args[0])
    if not f:
        return pomin("nie ma takiej firmy", id=args[0])
    w = args[1]
    if w not in WYNIKI:
        return pomin(f"nieznany wynik: {w}", dozwolone=sorted(WYNIKI))
    if not f.get("wyslano"):
        return pomin("firma nie ma statusu napisano - najpierw status napisano", id=f["id"])
    f["wynik"] = {"wynik": w, "data": dzis.isoformat()}
    m.zapisz()
    return wypisz({"id": f["id"], "wynik": w, "z_sygnalem": f["wyslano"]["z_sygnalem"]})


def _klucz_sygnalu(s: dict) -> str:
    if s.get("sonda") and s.get("typ"):
        if s["typ"].startswith(s["sonda"] + "_"):
            return s["typ"]
        return f"{s['sonda']}_{s['typ']}"
    return s.get("rodzina", "")


def _statystyka_wysylek(m: Magazyn) -> dict:
    """Liczy, ile wysłanych wiadomości dostało odpowiedź, w podziale na rodziny i klucze sygnałów."""
    wynik = {"razem": [0, 0], "z_sygnalem": [0, 0], "bez_sygnalu": [0, 0], "rodziny": {}, "klucze": {}}
    for f in m.dane["firmy"]:
        w = f.get("wyslano")
        if not w or not f.get("wynik"):
            continue  # bez znanego wyniku nie wiemy nic
        ok = 1 if f["wynik"]["wynik"] in POZYTYWNE_WYNIKI else 0
        for grupa in ("razem", "z_sygnalem" if w["z_sygnalem"] else "bez_sygnalu"):
            wynik[grupa][0] += 1
            wynik[grupa][1] += ok
        for r in w.get("rodziny", []):
            wynik["rodziny"].setdefault(r, [0, 0])
            wynik["rodziny"][r][0] += 1
            wynik["rodziny"][r][1] += ok
        for k in w.get("klucze", []):
            wynik["klucze"].setdefault(k, [0, 0])
            wynik["klucze"][k][0] += 1
            wynik["klucze"][k][1] += ok
    return wynik


def _mnozniki(m: Magazyn) -> dict:
    """Waga uczona: rodzina, po której ten człowiek dostaje więcej odpowiedzi, liczy się mocniej (0.5-2.0)."""
    st = _statystyka_wysylek(m)
    n, r = st["z_sygnalem"]
    if n < 5:
        return {}
    baza = (r + 1) / (n + 2)
    out = {}
    for rodz, (nr, rr) in st["rodziny"].items():
        if nr >= 5:
            out[rodz] = round(max(0.5, min(2.0, ((rr + 1) / (nr + 2)) / baza)), 2)
    return out


def k_skutecznosc(m: Magazyn, args, dzis) -> int:
    st = _statystyka_wysylek(m)

    def proc(para):
        n, r = para
        return {"wyslane": n, "odpowiedzi": r, "procent": round(100 * r / n) if n else None}

    bez_wyniku = sum(1 for f in m.dane["firmy"] if f.get("wyslano") and not f.get("wynik"))
    return wypisz({
        "razem": proc(st["razem"]), "z_sygnalem": proc(st["z_sygnalem"]), "bez_sygnalu": proc(st["bez_sygnalu"]),
        "rodziny": {k: proc(v) for k, v in sorted(st["rodziny"].items(), key=lambda x: -x[1][0])},
        "klucze": {k: proc(v) for k, v in sorted(st["klucze"].items(), key=lambda x: -x[1][0])[:15]},
        "mnozniki_wag": _mnozniki(m),
        "wyslane_bez_znanego_wyniku": bez_wyniku,
        "uwaga": "mnozniki dzialaja od 5 wyslanych wiadomosci z wynikiem w danej rodzinie",
    })


# --- sygnały i ocena ---------------------------------------------------------


def k_sygnal(m: Magazyn, args, dzis) -> int:
    f = m.firma(args[0])
    if not f:
        return pomin("nie ma takiej firmy", id=args[0])
    wejscie = wczytaj_json_arg(args[1])
    lista = wejscie if isinstance(wejscie, list) else [wejscie]
    zapisane, odrzucone = [], []
    for s in lista:
        wpis, powod = _waliduj_sygnal(s, dzis)
        if not wpis:
            odrzucone.append({"wejscie": s, "powod": powod})
            continue
        if any(x["sygnal"] == wpis["sygnal"] and x["data"] == wpis["data"] for x in f["sygnaly"]):
            odrzucone.append({"sygnal": wpis["sygnal"], "powod": "juz zapisany"})
            continue
        f["sygnaly"].append(wpis)
        zapisane.append(wpis)
    m.zapisz()
    return wypisz({"id": f["id"], "zapisane": zapisane, "odrzucone": odrzucone})


def _ocen_firme(m: Magazyn, f: dict, dzis: date, mnozniki: dict) -> dict | None:
    ust = m.ust
    akt = _aktywne(f, dzis, ust["waznosc_sygnalu_dni"])
    negatywne = [s for s in akt if s["rodzina"] == "nie"]
    pozytywne = [s for s in akt if s["rodzina"] != "nie"]
    if not pozytywne and not negatywne:
        return None
    w_oknie = [s for s in pozytywne if (dni_od(s["data"], dzis) or 0) <= ust["okno_priorytetu_dni"]]
    punkty = sum(float(s.get("waga", ust["wagi"].get(s["rodzina"], 1.0))) * mnozniki.get(s["rodzina"], 1.0)
                 for s in w_oknie)
    niespojnosc = any(s["rodzina"] == "niespojnosc" for s in w_oknie)
    return {
        "id": f["id"], "nazwa": f["nazwa"], "status": f["status"],
        "priorytet": (punkty >= float(ust["prog_priorytetu"]) or niespojnosc) and not negatywne,
        "punkty": round(punkty, 2), "w_oknie": len(w_oknie), "aktywne": len(pozytywne),
        "rodziny": sorted({s["rodzina"] for s in pozytywne}),
        "negatywne": negatywne,
        "sygnaly": sorted(pozytywne, key=lambda s: s["data"], reverse=True),
        "notatka": f.get("notatka"), "segment": f.get("segment") or f.get("branza") or "",
    }


def _branzowe(m: Magazyn, dzis: date) -> list[dict]:
    """Ta sama zmiana u kilku firm z jednego segmentu naraz = sygnał rynkowy, jedna wiadomość do wielu."""
    okno, minimum = m.ust["okno_priorytetu_dni"], int(m.ust["branzowy_min_firm"])
    grupy: dict[tuple, dict] = {}
    for f in m.dane["firmy"]:
        if f["status"] in ("porzucona", "skreslona"):
            continue
        seg = f.get("segment") or f.get("branza") or "wszystkie"
        for s in f.get("sygnaly", []):
            if s["rodzina"] == "nie" or not s.get("typ") or (dni_od(s["data"], dzis) or 10**6) > okno:
                continue
            g = grupy.setdefault((seg, _klucz_sygnalu(s)), {"firmy": {}, "przyklad": s["sygnal"]})
            g["firmy"][f["id"]] = f["nazwa"]
    out = []
    for (seg, klucz), g in grupy.items():
        if len(g["firmy"]) >= minimum:
            out.append({"segment": seg, "klucz": klucz, "przyklad": g["przyklad"],
                        "liczba_firm": len(g["firmy"]), "firmy": sorted(g["firmy"].values())})
    return sorted(out, key=lambda x: -x["liczba_firm"])


def k_ocena(m: Magazyn, args, dzis) -> int:
    mnozniki = _mnozniki(m)
    wynik = []
    for f in m.dane["firmy"]:
        if f["status"] in ("porzucona", "skreslona"):
            continue
        o = _ocen_firme(m, f, dzis, mnozniki)
        if o:
            wynik.append(o)
    wynik.sort(key=lambda w: (not w["priorytet"], -w["punkty"], -w["aktywne"]))
    return wypisz({"dzis": dzis.isoformat(), "okno_dni": m.ust["okno_priorytetu_dni"],
                   "prog_punktow": m.ust["prog_priorytetu"], "mnozniki_wag": mnozniki,
                   "firmy": wynik, "sygnaly_branzowe": _branzowe(m, dzis)})


# --- sonda: KRS ---------------------------------------------------------------


def _osoba(o: dict) -> str:
    naz = o.get("nazwisko") or {}
    im = o.get("imiona") or {}
    return "|".join([str(o.get("funkcjaWOrganie", "")),
                     str(naz.get("nazwiskoICzlon", "")) if isinstance(naz, dict) else str(naz),
                     str(im.get("imie", "")) if isinstance(im, dict) else str(im)])


def _krs_odpis(krs: str, rodzaj: str = "OdpisAktualny") -> tuple[dict | None, str]:
    for rejestr in ("P", "S"):
        url = f"https://api-krs.ms.gov.pl/api/krs/{rodzaj}/{krs}?rejestr={rejestr}&format=json"
        try:
            _, txt, _ = pobierz(url, naglowki={"Accept": "application/json"}, max_bajtow=20_000_000)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            return None, f"KRS HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            return None, f"siec: {e}"
        try:
            return json.loads(txt)["odpis"], url
        except (json.JSONDecodeError, KeyError):
            continue
    return None, "nie znaleziono w KRS (rejestr P ani S)"


def _krs_stan(o: dict) -> dict:
    d, nag = o.get("dane", {}), o.get("naglowekA", {})
    d1, d2, d3, d6 = (d.get(k) or {} for k in ("dzial1", "dzial2", "dzial3", "dzial6"))
    pod = d1.get("danePodmiotu") or {}
    sia = d1.get("siedzibaIAdres") or {}
    adr = sia.get("adres") or {}
    kap = ((d1.get("kapital") or {}).get("wysokoscKapitaluZakladowego") or {})
    sklad = (d2.get("reprezentacja") or {}).get("sklad") or []
    pkd = ((d3.get("przedmiotDzialalnosci") or {}).get("przedmiotPrzewazajacejDzialalnosci") or [])
    pkd0 = pkd[0] if pkd and isinstance(pkd[0], dict) else {}
    d6_klucze = sorted(k for k, v in d6.items() if v)
    return {
        "numer_wpisu": nag.get("numerOstatniegoWpisu"),
        "data_wpisu": nag.get("dataOstatniegoWpisu"),
        "nazwa": pod.get("nazwa"), "forma": pod.get("formaPrawna"),
        "adres": " ".join(str(adr.get(k, "")) for k in ("ulica", "nrDomu", "kodPocztowy", "miejscowosc")).strip(),
        "www": sia.get("adresStronyInternetowej"),
        "kapital": kap.get("wartosc"),
        "zarzad": sorted(_osoba(o) for o in sklad if isinstance(o, dict)),
        "prokurenci": sorted(_osoba(o) for o in (d2.get("prokurenci") or []) if isinstance(o, dict)),
        "pkd": f"{pkd0.get('kodDzial', '')}.{pkd0.get('kodKlasa', '')}.{pkd0.get('kodPodklasa', '')} {pkd0.get('opis', '')}".strip(". "),
        "dzial6": d6_klucze,
        "likwidacja_lub_upadlosc": any(re.search(r"likwid|upad|restruktur", k, re.I) for k in d6_klucze),
    }


def _kwota(s) -> float | None:
    try:
        return float(str(s).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return None


def _data_krs(s: str | None) -> str | None:
    try:
        return datetime.strptime(s, "%d.%m.%Y").date().isoformat() if s else None
    except ValueError:
        return None


# Ścieżka w pełnym odpisie -> (typ zmiany, rodzina, opis). Pierwsze dopasowanie wygrywa.
KRS_SEKCJE = [
    ("dzial6", "dzial6", "zmiana", "Wpis w dziale 6 (połączenie, przekształcenie, likwidacja albo upadłość)"),
    ("dzial2.reprezentacja", "zarzad", "zmiana", "Zmiana w zarządzie"),
    ("dzial2.prokurenci", "prokura", "zmiana", "Zmiana prokurentów"),
    ("dzial2.organNadzoru", "rada", "zmiana", "Zmiana w radzie nadzorczej"),
    ("dzial1.kapital", "kapital", "zmiana", "Zmiana kapitału zakładowego"),
    ("dzial1.wspolnicy", "wspolnicy", "zmiana", "Zmiana wspólników"),
    ("dzial1.jedynyAkcjonariusz", "wspolnicy", "zmiana", "Zmiana akcjonariusza"),
    ("dzial1.siedzibaIAdres", "adres", "zmiana", "Zmiana siedziby albo adresu"),
    ("dzial1.jednostkiTerenoweOddzialy", "oddzial", "wzrost", "Zmiana w oddziałach (nowy oddział albo zamknięty)"),
    ("dzial1.danePodmiotu.nazwa", "nazwa", "zmiana", "Zmiana nazwy firmy"),
    ("dzial1.danePodmiotu.formaPrawna", "forma", "zmiana", "Zmiana formy prawnej"),
    ("dzial3.przedmiotDzialalnosci", "pkd", "zmiana", "Zmiana przedmiotu działalności (PKD)"),
]


def _krs_historia(krs: str, dzis: date, dni: int = 90) -> tuple[list[dict], str]:
    """Pierwszy odczyt: co zmieniło się w KRS w ostatnich `dni` dniach (z pełnego odpisu)."""
    odpis, url = _krs_odpis(krs, "OdpisPelny")
    if odpis is None:
        return [], url
    wpisy = {}
    for w in (odpis.get("naglowekP") or {}).get("wpis") or []:
        d = _data_krs(w.get("dataWpisu"))
        syg = str(w.get("sygnaturaAktSprawyDotyczacejWpisu") or "")
        if d and (dni_od(d, dzis) or 10**6) <= dni and not syg.startswith("RDF"):  # RDF = złożone sprawozdania
            wpisy[str(w.get("numerWpisu"))] = d
    if not wpisy:
        return [], url
    trafienia: dict[tuple, dict] = {}

    def chodz(x, sciezka):
        if isinstance(x, dict):
            for nr_pole in ("nrWpisuWprow", "nrWpisuWykr"):
                nr = str(x.get(nr_pole) or "")
                if nr in wpisy:
                    for prefiks, typ, rodz, opis in KRS_SEKCJE:
                        if sciezka.startswith(prefiks):
                            k = (typ, nr)
                            t = trafienia.setdefault(k, {"typ": typ, "rodzina": rodz, "opis": opis,
                                                         "data": wpisy[nr], "wprow": [], "wykr": []})
                            t["wprow" if nr_pole == "nrWpisuWprow" else "wykr"].append(x)
                            break
            for k, v in x.items():
                chodz(v, f"{sciezka}.{k}" if sciezka else k)
        elif isinstance(x, list):
            for v in x:
                chodz(v, sciezka)

    chodz(odpis.get("dane") or {}, "")
    zmiany = []
    for (typ, nr), t in sorted(trafienia.items(), key=lambda kv: kv[1]["data"]):
        opis, rodz = t["opis"], t["rodzina"]
        if typ == "kapital":
            nowe = [_kwota(x.get("wartosc")) for x in t["wprow"] if x.get("wartosc")]
            stare = [_kwota(x.get("wartosc")) for x in t["wykr"] if x.get("wartosc")]
            if nowe and stare and None not in (nowe[0], stare[0]) and nowe[0] > stare[0]:
                rodz, opis = "wzrost", f"Podwyższenie kapitału: {stare[0]:,.0f} -> {nowe[0]:,.0f} zł".replace(",", " ")
        if typ == "oddzial":
            otwarte = sum(1 for x in t["wprow"] if "nazwa" in x and not x.get("nrWpisuWykr"))
            zamkniete = sum(1 for x in t["wykr"] if "nazwa" in x)
            if otwarte and not zamkniete:
                rodz, opis = "wzrost", f"Nowy oddział w KRS ({otwarte})"
            elif zamkniete and not otwarte:
                rodz, opis = "zmiana", f"Zamknięty oddział w KRS ({zamkniete})"
            else:
                rodz, opis = "zmiana", "Zmiany w oddziałach w KRS"
        if typ == "dzial6":
            tekst = json.dumps(t["wprow"], ensure_ascii=False).lower()
            if re.search(r"likwid|upad|restruktur", tekst):
                rodz, opis = "nie", "Otwarta likwidacja, upadłość albo restrukturyzacja (KRS dział 6)"
        if typ == "zarzad":
            ludzie_in = sum(1 for x in t["wprow"] if "funkcjaWOrganie" in x or "nazwisko" in x)
            ludzie_out = sum(1 for x in t["wykr"] if "funkcjaWOrganie" in x or "nazwisko" in x)
            if ludzie_in or ludzie_out:
                opis = f"Zmiana w zarządzie: doszło {ludzie_in}, odeszło {ludzie_out}"
        zmiany.append({"typ": typ, "rodzina": rodz, "opis": f"{opis} (wpis nr {nr})", "data": t["data"],
                       "zrodlo_url": url, "z_historii": True})
    return zmiany, url


def sonda_krs(m: Magazyn, f: dict, dzis: date) -> dict:
    odpis, url = _krs_odpis(f["krs"])
    if odpis is None:
        return {"skipped": "[do reki]", "powod": url}
    nowy = _krs_stan(odpis)
    pelny = m.stan(f["id"])
    stary = pelny.get("krs")
    data_zm = _data_krs(nowy["data_wpisu"]) or dzis.isoformat()
    zmiany = []
    if stary is None:
        zmiany, _ = _krs_historia(f["krs"], dzis, m.ust["waznosc_sygnalu_dni"])
    elif stary.get("numer_wpisu") != nowy["numer_wpisu"]:
        doszli = set(nowy["zarzad"]) - set(stary.get("zarzad", []))
        odeszli = set(stary.get("zarzad", [])) - set(nowy["zarzad"])
        if doszli or odeszli:
            funkcje = sorted({o.split("|")[0] for o in doszli | odeszli if o.split("|")[0]})
            zmiany.append({"typ": "zarzad", "rodzina": "zmiana",
                           "opis": f"Zmiana w zarządzie: doszło {len(doszli)}, odeszło {len(odeszli)}"
                                   + (f" ({', '.join(funkcje)})" if funkcje else "")})
        if nowy["kapital"] != stary.get("kapital"):
            a, b = _kwota(stary.get("kapital")), _kwota(nowy["kapital"])
            wzrost = a is not None and b is not None and b > a
            zmiany.append({"typ": "kapital", "rodzina": "wzrost" if wzrost else "zmiana",
                           "opis": f"Kapitał zakładowy: {stary.get('kapital')} -> {nowy['kapital']} zł"})
        for pole, opis in (("adres", "Nowy adres siedziby"), ("pkd", "Zmiana przeważającej działalności (PKD)"),
                           ("nazwa", "Zmiana nazwy firmy"), ("www", "Zmiana adresu strony w KRS"),
                           ("forma", "Zmiana formy prawnej")):
            if nowy[pole] != stary.get(pole):
                zmiany.append({"typ": pole, "rodzina": "zmiana",
                               "opis": f"{opis}: {stary.get(pole)} -> {nowy[pole]}"})
        if nowy["prokurenci"] != stary.get("prokurenci", []):
            zmiany.append({"typ": "prokura", "rodzina": "zmiana", "opis": "Zmiana prokurentów"})
        nowe6 = set(nowy["dzial6"]) - set(stary.get("dzial6", []))
        if nowe6:
            zmiany.append({"typ": "dzial6", "rodzina": "nie" if nowy["likwidacja_lub_upadlosc"] else "zmiana",
                           "opis": "Nowe wpisy w dziale 6 KRS: " + ", ".join(sorted(nowe6))})
        if not zmiany:
            zmiany.append({"typ": "wpis", "rodzina": "zmiana",
                           "opis": f"Nowy wpis w KRS nr {nowy['numer_wpisu']} - szczegóły w odpisie"})
        for z in zmiany:
            z.update({"data": data_zm, "zrodlo_url": url})
    pelny["krs"] = nowy
    m.zapisz_stan(f["id"], pelny)
    return {"zmiany": zmiany, "pierwszy_odczyt": stary is None,
            "stan": {**{k: nowy[k] for k in ("nazwa", "data_wpisu", "kapital", "pkd", "likwidacja_lub_upadlosc")},
                     "liczba_w_zarzadzie": len(nowy["zarzad"])}}


# --- sonda: strona (tekst, sitemapa, narzędzia, ogłoszenia, archiwum) --------


class _Parser(html.parser.HTMLParser):
    POMIJAJ = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.kawalki, self.linki, self.formy, self._pomin = [], [], 0, 0
        self.tytul, self._w_tytule = "", False
        self.jsonld, self._w_jsonld, self._bufor = [], False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and "ld+json" in str(a.get("type", "")).lower():
            self._w_jsonld, self._bufor = True, []
        if tag in self.POMIJAJ:
            self._pomin += 1
        elif tag == "a" and a.get("href"):
            self.linki.append(a["href"])
        elif tag == "form":
            self.formy += 1
        elif tag == "title":
            self._w_tytule = True

    def handle_endtag(self, tag):
        if tag == "script" and self._w_jsonld:
            self.jsonld.append("".join(self._bufor))
            self._w_jsonld = False
        if tag in self.POMIJAJ and self._pomin:
            self._pomin -= 1
        elif tag == "title":
            self._w_tytule = False

    def handle_data(self, data):
        if self._w_jsonld:
            self._bufor.append(data)
        if self._w_tytule:
            self.tytul += data
        if not self._pomin and data.strip():
            self.kawalki.append(data.strip())


SLOWA = {
    "rekrutacja": ["kariera", "praca u nas", "dołącz do", "dolacz do", "rekrutac", "oferty pracy",
                   "zatrudnimy", "szukamy osoby", "szukamy do zespołu", "aplikuj"],
    "nowa lokalizacja": ["nowa lokalizacja", "nowy oddział", "otwieramy", "otwarcie", "nowy salon",
                         "nowy gabinet", "druga lokalizacja", "nowa siedziba"],
    "nowa oferta": ["nowość", "nowa usługa", "wprowadzamy", "premiera", "nowy produkt", "nowa kolekcja"],
    "dofinansowanie": ["dofinansowan", "fundusze europejskie", "współfinansowany", "wspolfinansowany",
                       "unia europejska", "kpo", "krajowy plan odbudowy"],
}
SLOWO_RODZINA = {"rekrutacja": "wzrost", "nowa lokalizacja": "wzrost", "nowa oferta": "zmiana",
                 "dofinansowanie": "intencja"}

# Narzędzia rozpoznawane w kodzie strony. (nazwa, regex, grupa)
NARZEDZIA = [
    ("piksel Meta", r"connect\.facebook\.net/[^\"']*fbevents\.js|fbq\(\s*['\"]init", "reklamy"),
    ("Google Ads", r"googleads\.g\.doubleclick\.net|gtag\(\s*['\"]config['\"]\s*,\s*['\"]AW-|['\"]AW-\d{6,}", "reklamy"),
    ("piksel TikTok", r"analytics\.tiktok\.com|ttq\.load", "reklamy"),
    ("LinkedIn Insight", r"snap\.licdn\.com|_linkedin_partner_id", "reklamy"),
    ("Google Analytics 4", r"googletagmanager\.com/gtag/js\?id=G-|['\"]G-[A-Z0-9]{6,}['\"]", "analityka"),
    ("Google Tag Manager", r"googletagmanager\.com/gtm\.js|GTM-[A-Z0-9]{4,}", "analityka"),
    ("Hotjar", r"static\.hotjar\.com|hotjar\.com/c/hotjar", "analityka"),
    ("Microsoft Clarity", r"clarity\.ms/tag", "analityka"),
    ("Booksy", r"booksy\.com", "rezerwacje"),
    ("ZnanyLekarz", r"znanylekarz\.pl|docplanner", "rezerwacje"),
    ("Calendly", r"calendly\.com", "rezerwacje"),
    ("czat na stronie", r"tawk\.to|livechatinc\.com|smartsupp|intercom|crisp\.chat|tidio|zendesk\.com/embeddable", "czat"),
    ("WordPress", r"wp-content/|wp-includes/", "cms"),
    ("WooCommerce", r"woocommerce", "sklep"),
    ("Shopify", r"cdn\.shopify\.com|myshopify\.com", "sklep"),
    ("PrestaShop", r"prestashop", "sklep"),
    ("Shoper", r"shoper\.pl|shoplo", "sklep"),
    ("Wix", r"static\.wixstatic\.com|wix\.com", "cms"),
    ("Webflow", r"webflow\.com|assets\.website-files\.com", "cms"),
    ("newsletter", r"mailerlite|getresponse|mailchimp|klaviyo|freshmail|sendinblue|brevo", "newsletter"),
]
NARZEDZIE_RODZINA = {"reklamy": ("wzrost", "Pojawił się {n} - zwykle przygotowanie pod reklamy"),
                     "rezerwacje": ("zmiana", "Pojawiły się rezerwacje online ({n})"),
                     "czat": ("zmiana", "Pojawił się {n}"),
                     "sklep": ("zmiana", "Nowa platforma sklepu ({n})"),
                     "cms": ("zmiana", "Zmiana platformy strony ({n})")}
ZASOBY = re.compile(r"\.(jpe?g|png|gif|webp|svg|pdf|css|js|ico|mp4|zip|woff2?|xml|json)$", re.I)
ULOTNE = re.compile(r"cookie|ciasteczk|polityk[aię] prywatno|rodo|akceptuj|zgod[ayę] na|newsletter|"
                    r"©|copyright|wszelkie prawa", re.I)
KARIERA = re.compile(r"kariera|praca|jobs|career|rekrutac|dolacz|dołącz", re.I)


def _normalizuj(kawalki: list[str]) -> str:
    """Tekst bez rzeczy, które zmieniają się same (banery cookie, stopka, daty, liczniki)."""
    dobre = [k for k in kawalki if len(k) > 2 and not ULOTNE.search(k)]
    t = " ".join(dobre).lower()
    t = re.sub(r"\d+", "0", t)
    return re.sub(r"\s+", " ", t)[:60000]


def _parsuj(html_txt: str, finalny: str) -> dict:
    p = _Parser()
    try:
        p.feed(html_txt)
    except Exception:  # noqa: BLE001 - zepsuty HTML nie może wywrócić skanu
        pass
    dom = domena(finalny)
    sciezki = set()
    for href in p.linki:
        u = urllib.parse.urljoin(finalny, href)
        pu = urllib.parse.urlparse(u)
        if pu.scheme in ("http", "https") and domena(u) == dom:
            s = pu.path.rstrip("/") or "/"
            if not ZASOBY.search(s):
                sciezki.add(s)
    surowy = " ".join(p.kawalki)
    niski = surowy.lower()
    lata = [int(r) for r in re.findall(r"(?:©|copyright)\s*(?:\d{4}\s*[-–]\s*)?(\d{4})", niski)]
    narz = sorted({n for n, wzor, _ in NARZEDZIA if re.search(wzor, html_txt, re.I)})
    tekst = _normalizuj(p.kawalki)
    return {
        "tytul": p.tytul.strip()[:200], "tekst": tekst,
        "hash": hashlib.sha1(tekst.encode("utf-8")).hexdigest(),
        "sciezki": sorted(sciezki)[:500],
        "slowa": sorted(k for k, lista in SLOWA.items() if any(s in niski for s in lista)),
        "ma_formularz": p.formy > 0 or "formularz" in niski,
        "rok_stopki": max(lata) if lata else None,
        "narzedzia": narz,
        "jsonld": p.jsonld,
    }


def _ogloszenia_jsonld(bloki: list[str], url_strony: str) -> list[dict]:
    out = []

    def zbierz(x):
        if isinstance(x, list):
            for v in x:
                zbierz(v)
        elif isinstance(x, dict):
            typ = x.get("@type")
            typy = typ if isinstance(typ, list) else [typ]
            if "JobPosting" in typy and x.get("title"):
                out.append({"tytul": re.sub(r"\s+", " ", str(x["title"])).strip()[:120],
                            "url": x.get("url") or url_strony, "data": _iso(x.get("datePosted"))})
            for k in ("@graph", "itemListElement", "item"):
                if k in x:
                    zbierz(x[k])

    for b in bloki:
        try:
            zbierz(json.loads(b))
        except (json.JSONDecodeError, ValueError):
            continue
    return out


def _sitemap(baza: str) -> dict | None:
    """Ścieżki i daty zmian z sitemapy. Brak sitemapy -> None (wtedy liczą się linki ze strony)."""
    pu = urllib.parse.urlparse(baza)
    root = f"{pu.scheme}://{pu.netloc}"
    kandydaci = []
    try:
        _, robots, _, _ = pobierz_strone(root + "/robots.txt", timeout=15, max_bajtow=200_000)
        kandydaci += re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots)
    except Exception:  # noqa: BLE001
        pass
    kandydaci += [root + "/sitemap.xml", root + "/sitemap_index.xml", root + "/wp-sitemap.xml"]
    widziane, wpisy = set(), {}
    kolejka = list(dict.fromkeys(kandydaci))
    pobrane = 0
    while kolejka and pobrane < 6:
        u = kolejka.pop(0)
        if u in widziane:
            continue
        widziane.add(u)
        try:
            kod, xml, _, _ = pobierz_strone(u, timeout=15, max_bajtow=8_000_000)
        except Exception:  # noqa: BLE001
            continue
        pobrane += 1
        if "<urlset" not in xml and "<sitemapindex" not in xml:
            continue
        if "<sitemapindex" in xml:
            dzieci = re.findall(r"<sitemap>\s*<loc>\s*([^<\s]+)", xml)
            # strony i wpisy najpierw, obrazki i tagi na końcu
            dzieci.sort(key=lambda d: (bool(re.search(r"image|tag|author|categor", d)), d))
            kolejka = dzieci[:5] + kolejka
            continue
        for blok in re.findall(r"<url>(.*?)</url>", xml, re.S)[:5000]:
            loc = re.search(r"<loc>\s*([^<\s]+)", blok)
            if not loc:
                continue
            sciezka = urllib.parse.urlparse(loc.group(1)).path.rstrip("/") or "/"
            lm = re.search(r"<lastmod>\s*([^<\s]+)", blok)
            wpisy[sciezka] = _iso(lm.group(1)) if lm else None
        if len(wpisy) >= 5000:
            break
    if not wpisy:
        return None
    daty = [d for d in wpisy.values() if d]
    najczestsza = max(set(daty), key=daty.count) if daty else None
    # Gdy jedna data obejmuje większość adresów, CMS stempluje wszystko naraz - daty nic nie znaczą.
    daty_ok = bool(daty) and daty.count(najczestsza) / len(daty) < 0.6
    return {"sciezki": sorted(wpisy)[:5000], "lastmod": {k: v for k, v in wpisy.items() if v} if daty_ok else {},
            "daty_wiarygodne": daty_ok}


def _archiwum(url: str, dzis: date) -> tuple[dict | None, str | None]:
    """Wersja strony sprzed ~60-120 dni z archiwum internetu (Wayback Machine, darmowe)."""
    od = (dzis - timedelta(days=120)).strftime("%Y%m%d")
    do = (dzis - timedelta(days=60)).strftime("%Y%m%d")
    cdx = ("https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(
        {"url": domena(url), "from": od, "to": do, "output": "json", "limit": "-1",
         "filter": "statuscode:200", "fl": "timestamp,original"}))
    try:
        _, txt, _ = pobierz(cdx, timeout=20)
        wiersze = json.loads(txt)
        if len(wiersze) < 2:
            return None, None
        ts, oryg = wiersze[-1][0], wiersze[-1][1]
        _, stary_html, fin, _ = pobierz_strone(f"https://web.archive.org/web/{ts}id_/{oryg}", timeout=30)
    except Exception:  # noqa: BLE001 - archiwum bywa przeciążone, wtedy po prostu bez porównania
        return None, None
    return _parsuj(stary_html, fin or oryg), f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


def _porownaj_strony(stary: dict, nowy: dict, od_kiedy: str | None = None) -> list[dict]:
    zmiany = []
    dopisek = f" (od {od_kiedy})" if od_kiedy else ""
    nowe = sorted(set(nowy["sciezki"]) - set(stary.get("sciezki", [])))
    if nowe and len(nowe) <= max(30, len(nowy["sciezki"]) // 2):
        zmiany.append({"typ": "nowe_podstrony", "rodzina": "zmiana",
                       "opis": f"Nowe podstrony{dopisek} ({len(nowe)}): " + ", ".join(nowe[:12]),
                       "sciezki": nowe[:25]})
    for slowo in sorted(set(nowy["slowa"]) - set(stary.get("slowa", []))):
        zmiany.append({"typ": f"watek_{slug(slowo)}", "rodzina": SLOWO_RODZINA[slowo],
                       "opis": f"Na stronie pojawił się wątek: {slowo}{dopisek}"})
    grupy = {n: g for n, _, g in NARZEDZIA}
    for n in sorted(set(nowy.get("narzedzia", [])) - set(stary.get("narzedzia", []))):
        g = grupy.get(n)
        if g in NARZEDZIE_RODZINA:
            rodz, wzor = NARZEDZIE_RODZINA[g]
            zmiany.append({"typ": f"narzedzie_{slug(n)}", "rodzina": rodz, "opis": wzor.format(n=n) + dopisek})
    for n in sorted(set(stary.get("narzedzia", [])) - set(nowy.get("narzedzia", []))):
        if grupy.get(n) in ("reklamy", "analityka"):
            zmiany.append({"typ": f"usuniete_{slug(n)}", "rodzina": "zmiana",
                           "opis": f"Ze strony zniknął {n}{dopisek}"})
    if nowy["hash"] != stary.get("hash") and not zmiany:
        podob = difflib.SequenceMatcher(None, stary.get("tekst", "")[:20000], nowy["tekst"][:20000]).ratio()
        if podob < 0.8:
            zmiany.append({"typ": "tresc", "rodzina": "zmiana",
                           "opis": f"Treść strony głównej mocno się zmieniła{dopisek} (podobieństwo {podob:.0%})"})
    return zmiany


def sonda_strona(m: Magazyn, f: dict, dzis: date) -> dict:
    url = f["strona"] if "://" in f["strona"] else "https://" + f["strona"]
    try:
        kod, txt, finalny, problem_ssl = pobierz_strone(url)
    except urllib.error.HTTPError as e:
        return {"skipped": "[do reki]", "powod": f"strona HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return {"skipped": "[do reki]", "powod": f"strona nie odpowiada: {e}"}
    nowy = _parsuj(txt, finalny)
    nowy["url"], nowy["problem_ssl"] = finalny, problem_ssl
    mapa = _sitemap(finalny)
    nowy["sitemap"] = mapa

    # Ogłoszenia z danych strukturalnych: strona główna + jedna podstrona kariery.
    jsonld = list(nowy.pop("jsonld"))
    sciezki_wszystkie = (mapa or {}).get("sciezki") or nowy["sciezki"]
    kariera = next((s for s in sciezki_wszystkie if KARIERA.search(s) and s.count("/") <= 2), None)
    url_kariery = None
    if kariera:
        pu = urllib.parse.urlparse(finalny)
        url_kariery = f"{pu.scheme}://{pu.netloc}{kariera}"
        try:
            _, ktxt, kfin, _ = pobierz_strone(url_kariery, timeout=20)
            jsonld += _parsuj(ktxt, kfin)["jsonld"]
        except Exception:  # noqa: BLE001
            pass
    ogloszenia = _ogloszenia_jsonld(jsonld, url_kariery or finalny)
    nowy["ma_kariera"] = bool(kariera)

    pelny = m.stan(f["id"])
    stary = pelny.get("strona")
    zmiany, archiwum_z = [], None
    if stary:
        porownaj_z = dict(stary)
        if mapa and stary.get("sitemap"):  # sitemapa jest dokładniejsza niż linki ze strony głównej
            porownaj_z["sciezki"] = stary["sitemap"]["sciezki"]
            nowy_cmp = {**nowy, "sciezki": mapa["sciezki"]}
        else:
            nowy_cmp = nowy
        zmiany = _porownaj_strony(porownaj_z, nowy_cmp)
    else:
        if m.ust.get("archiwum_strony", True):
            stara_wersja, archiwum_z = _archiwum(finalny, dzis)
            if stara_wersja:
                zmiany = _porownaj_strony(stara_wersja, nowy, archiwum_z)
        if mapa and mapa["daty_wiarygodne"]:
            swieze = sorted(s for s, d in mapa["lastmod"].items() if (dni_od(d, dzis) or 10**6) <= 30)
            if swieze and len(swieze) <= max(20, len(mapa["sciezki"]) // 3):
                zmiany.append({"typ": "swieze_podstrony", "rodzina": "zmiana",
                               "opis": f"W ostatnich 30 dniach doszło albo zmieniło się {len(swieze)} podstron (sitemapa): "
                                       + ", ".join(swieze[:10]), "sciezki": swieze[:25]})
    for z in zmiany:
        z.setdefault("data", dzis.isoformat())
        z.setdefault("zrodlo_url", finalny)
    pelny["strona"] = nowy
    m.zapisz_stan(f["id"], pelny)

    # Ogłoszenia z danych strukturalnych idą przez tę samą pamięć co sonda praca.
    zmiany_praca = []
    if ogloszenia:
        zmiany_praca, _ = _obserwuj(m, f, "praca", ogloszenia, dzis)
        f["sondy"]["praca"] = dzis.isoformat()
        for z in zmiany_praca:
            z["zrodlo"] = "dane strukturalne strony"
    stan = {k: nowy[k] for k in ("tytul", "slowa", "ma_formularz", "rok_stopki", "ma_kariera",
                                 "problem_ssl", "narzedzia")}
    stan.update({"liczba_podstron": len(sciezki_wszystkie), "sitemap": bool(mapa),
                 "ogloszenia_w_kodzie": len(ogloszenia), "porownanie_z_archiwum": archiwum_z,
                 "ma_piksel_reklamowy": any(n in nowy["narzedzia"] for n in
                                            ("piksel Meta", "Google Ads", "piksel TikTok", "LinkedIn Insight"))})
    return {"zmiany": zmiany + zmiany_praca, "pierwszy_odczyt": stary is None, "stan": stan}


# --- sondy płatne: opinie (Apify), instagram (Apify), reklamy (Meta) ---------


def _apify(aktor: str, wejscie: dict, tok: str, timeout: int = 180) -> list:
    url = f"https://api.apify.com/v2/acts/{aktor}/run-sync-get-dataset-items?token={tok}"
    _, txt, _ = pobierz(url, dane=json.dumps(wejscie).encode("utf-8"),
                        naglowki={"Content-Type": "application/json"}, timeout=timeout,
                        max_bajtow=20_000_000)
    out = json.loads(txt)
    if not isinstance(out, list):
        raise ValueError("nieoczekiwany ksztalt odpowiedzi Apify")
    return out


def sonda_opinie(m: Magazyn, f: dict, dzis: date) -> dict:
    tok = token("APIFY_TOKEN", "APIFY_API_TOKEN")
    if not tok:
        return {"skipped": "[do reki]", "powod": "brak APIFY_TOKEN"}
    pelny = m.stan(f["id"])
    stary = pelny.get("opinie") or {}
    od = stary.get("sprawdzone_do")
    # Link do miejsca z samymi współrzędnymi potrafi zwrócić zero wyników. Link wyszukiwania
    # (nazwa + miasto) działa pewnie, więc jest zapasem i wyjściem, gdy nie ma linku w ogóle.
    szukaj = ("https://www.google.com/maps/search/?api=1&query="
              + urllib.parse.quote(" ".join(x for x in (f["nazwa"], f.get("miasto") or "") if x)))
    adresy = [f["google_maps"], szukaj] if f.get("google_maps") else [szukaj]
    items = []
    for adres in adresy:
        wejscie = {"startUrls": [{"url": adres}], "reviewsSort": "newest", "language": "pl",
                   "maxReviews": int(m.ust.get("opinie_max_na_firme", 30)), "personalData": False}
        if od:
            wejscie["reviewsStartDate"] = od
        try:
            items = _apify("compass~google-maps-reviews-scraper", wejscie, tok)
        except urllib.error.HTTPError as e:
            return {"skipped": "[do reki]", "powod": f"Apify HTTP {e.code}"}
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as e:
            return {"skipped": "[do reki]", "powod": f"Apify: {e}"}
        if items or od:  # przy kolejnych skanach pusto = po prostu brak nowych opinii
            break
    opinie = []
    for it in items:
        if not isinstance(it, dict):
            continue
        d = str(it.get("publishedAtDate") or "")[:10]
        if od and d and d < od:
            continue
        opinie.append({"data": d, "gwiazdki": it.get("stars"), "tekst": (it.get("text") or "")[:220],
                       "url": it.get("reviewUrl") or it.get("url") or f.get("google_maps") or szukaj})
    miejsce = next((it for it in items if isinstance(it, dict)), {})
    negatywne = [o for o in opinie if isinstance(o["gwiazdki"], (int, float)) and o["gwiazdki"] <= 2]
    ost30 = [o for o in negatywne if (dni_od(o["data"], dzis) or 999) <= 30]
    zmiany = []
    if len(ost30) >= 3:  # daty są w opiniach, więc liczy się już przy pierwszym odczycie
        zmiany.append({"typ": "zle_opinie", "rodzina": "bol",
                       "opis": f"{len(ost30)} opinii 1-2 gwiazdki w ostatnich 30 dniach (Google)",
                       "data": max(o["data"] for o in ost30), "zrodlo_url": f.get("google_maps") or szukaj,
                       "fragmenty": [o["tekst"] for o in ost30[:3]]})
    pelny["opinie"] = {"sprawdzone_do": dzis.isoformat(),
                       "ocena": miejsce.get("totalScore") or stary.get("ocena"),
                       "liczba": miejsce.get("reviewsCount") or stary.get("liczba"),
                       "miejsce": miejsce.get("title") or stary.get("miejsce"),
                       "adres": miejsce.get("address") or stary.get("adres")}
    m.zapisz_stan(f["id"], pelny)
    return {"zmiany": zmiany, "pierwszy_odczyt": not stary,
            "stan": {"nowe_opinie": len(opinie), "negatywne_nowe": len(negatywne),
                     "ocena": pelny["opinie"]["ocena"], "liczba_opinii": pelny["opinie"]["liczba"],
                     "dopasowane_miejsce": pelny["opinie"]["miejsce"], "adres": pelny["opinie"]["adres"],
                     "z_wyszukiwania": not f.get("google_maps")},
            "uwaga": ("fragmenty opinii sa do interpretacji, nigdy do cytowania w mailu. "
                      "Przy pierwszym odczycie potwierdz, ze dopasowane_miejsce to ta firma.")}


def _apify_ig():
    p = Path(__file__).resolve().parents[2] / "research" / "solutions" / "apify_ig.py"
    spec = importlib.util.spec_from_file_location("apify_ig", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sonda_instagram(m: Magazyn, f: dict, dzis: date) -> dict:
    tok = token("APIFY_TOKEN", "APIFY_API_TOKEN")
    if not tok:
        return {"skipped": "[do reki]", "powod": "brak APIFY_TOKEN"}
    try:
        nowy = _apify_ig().fetch(str(f["instagram"]).lstrip("@").strip("/").split("/")[-1], tok)
    except Exception as e:  # noqa: BLE001 - sieć i kształt odpowiedzi Apify są nieprzewidywalne
        return {"skipped": "[do reki]", "powod": f"Apify IG: {e}"}
    if nowy.get("skipped"):
        return nowy
    pelny = m.stan(f["id"])
    stary = pelny.get("instagram")
    zmiany = []
    dni = nowy.get("days_since_last_post")
    if stary and dni is not None:
        bylo = stary.get("days_since_last_post")
        if dni >= 30 and (bylo is None or bylo < 30):
            zmiany.append({"typ": "ig_zamarl", "rodzina": "bol",
                           "opis": f"Instagram bez posta od {int(dni)} dni (wcześniej był aktywny)"})
        if bylo is not None and bylo >= 30 and dni < 7:
            zmiany.append({"typ": "ig_ozyl", "rodzina": "zmiana", "opis": "Instagram znów aktywny po przerwie"})
    for z in zmiany:
        z.update({"data": dzis.isoformat(), "zrodlo_url": f"https://www.instagram.com/{nowy.get('username')}/"})
    pelny["instagram"] = nowy
    m.zapisz_stan(f["id"], pelny)
    return {"zmiany": zmiany, "pierwszy_odczyt": stary is None, "stan": nowy}


def sonda_reklamy(m: Magazyn, f: dict, dzis: date) -> dict:
    link = ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=PL&q="
            + urllib.parse.quote(f["nazwa"]))
    tok = token("META_ADLIB_TOKEN")
    if not tok:
        return {"skipped": "[do reki]", "powod": "brak META_ADLIB_TOKEN - sprawdz biblioteke reklam recznie",
                "link": link}
    wersja = token("META_API_VERSION") or "v21.0"
    params = {"access_token": tok, "ad_reached_countries": '["PL"]', "search_terms": f["nazwa"],
              "ad_active_status": "ACTIVE", "ad_type": "ALL", "limit": "100",
              "fields": "id,page_name,ad_delivery_start_time"}
    url = f"https://graph.facebook.com/{wersja}/ads_archive?" + urllib.parse.urlencode(params)
    try:
        _, txt, _ = pobierz(url)
        dane = json.loads(txt).get("data", [])
    except urllib.error.HTTPError as e:
        return {"skipped": "[do reki]", "powod": f"Meta HTTP {e.code} - sprawdz token i weryfikacje tozsamosci",
                "link": link}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return {"skipped": "[do reki]", "powod": f"Meta: {e}", "link": link}
    rdzen = [w for w in slug(f["nazwa"]).split("-") if len(w) > 2][:3]
    trafione = [a for a in dane if all(w in slug(a.get("page_name", "")) for w in rdzen)]
    swieze = [a for a in trafione if (dni_od(_iso(a.get("ad_delivery_start_time")), dzis) or 10**6) <= 30]
    nowy = {"aktywne": len(trafione), "ids": sorted(a["id"] for a in trafione)[:200],
            "strony": sorted({a.get("page_name", "") for a in trafione}), "ruszyly_w_30_dni": len(swieze)}
    pelny = m.stan(f["id"])
    stary = pelny.get("reklamy")
    zmiany = []
    if stary:
        if stary.get("aktywne", 0) == 0 and nowy["aktywne"] > 0:
            zmiany.append({"typ": "start_reklam", "rodzina": "wzrost",
                           "opis": f"Ruszyły reklamy w Meta ({nowy['aktywne']} aktywnych)"})
        elif stary.get("aktywne", 0) > 0 and nowy["aktywne"] == 0:
            zmiany.append({"typ": "stop_reklam", "rodzina": "zmiana",
                           "opis": "Reklamy w Meta zniknęły (wcześniej aktywne)"})
        elif len(set(nowy["ids"]) - set(stary.get("ids", []))) >= 3:
            zmiany.append({"typ": "nowa_kampania", "rodzina": "wzrost", "opis": "Nowa partia reklam w Meta"})
    elif swieze:  # pierwszy odczyt: daty startu reklam mówią, czy kampania jest świeża
        zmiany.append({"typ": "nowa_kampania", "rodzina": "wzrost",
                       "opis": f"{len(swieze)} reklam w Meta wystartowało w ostatnich 30 dniach"})
    for z in zmiany:
        z.update({"data": dzis.isoformat(), "zrodlo_url": link})
    pelny["reklamy"] = nowy
    m.zapisz_stan(f["id"], pelny)
    return {"zmiany": zmiany, "pierwszy_odczyt": stary is None, "stan": nowy}


SONDY = {"krs": sonda_krs, "strona": sonda_strona, "opinie": sonda_opinie,
         "instagram": sonda_instagram, "reklamy": sonda_reklamy}
WYMAGANE = {"krs": "krs", "strona": "strona", "instagram": "instagram"}


def k_sonda(m: Magazyn, args, dzis) -> int:
    f = m.firma(args[0])
    if not f:
        return pomin("nie ma takiej firmy", id=args[0])
    nazwa = args[1]
    if nazwa not in SONDY:
        return pomin(f"sonda {nazwa} nie jest skryptowa - zbierz ja i uzyj komendy obserwacja",
                     skryptowe=sorted(SONDY))
    pole = WYMAGANE.get(nazwa)
    if pole and not f.get(pole):
        return pomin(f"brak pola {pole} - uzupelnij komenda uzupelnij", id=f["id"])
    wynik = SONDY[nazwa](m, f, dzis)
    if not wynik.get("skipped"):
        f["sondy"][nazwa] = dzis.isoformat()
        f["ostatni_skan"] = dzis.isoformat()
        m.policz_uruchomienie(nazwa, dzis)
    m.zapisz()
    for z in wynik.get("zmiany", []):
        z.setdefault("sonda", nazwa)
    return wypisz({"id": f["id"], "nazwa": f["nazwa"], "sonda": nazwa, **wynik})


# --- obserwacje przyniesione przez model ------------------------------------


def _klucz_elementu(e: dict) -> str:
    return slug(str(e.get("tytul") or e.get("url") or ""))[:80]


ROD_OBS = {"praca": {"nowe": "wzrost", "wraca": "bol", "wisi": "bol"},
           "baza": {"nowe": "intencja", "wraca": "intencja", "wisi": "intencja"},
           "linkedin": {"nowe": "zmiana", "wraca": "zmiana", "wisi": "zmiana"}}


def _obserwuj(m: Magazyn, f: dict, rodzaj: str, elementy: list, dzis: date) -> tuple[list, bool]:
    pelny = m.stan(f["id"])
    pamiec = pelny.get(f"obs_{rodzaj}")
    pierwszy = pamiec is None
    pamiec = pamiec or {"widziane": {}, "ostatnio": []}
    widziane, poprzednio = pamiec["widziane"], set(pamiec.get("ostatnio", []))
    teraz, zmiany = [], []
    for e in elementy:
        if not isinstance(e, dict):
            continue
        k = _klucz_elementu(e)
        if not k or k in teraz:
            continue
        teraz.append(k)
        w = widziane.get(k)
        data_el = _iso(e.get("data"))
        if w is None:
            pierwsza_data = data_el if data_el and data_el < dzis.isoformat() else dzis.isoformat()
            widziane[k] = {"tytul": e.get("tytul"), "url": e.get("url"), "pierwszy": pierwsza_data,
                           "ostatni": dzis.isoformat(), "powroty": 0}
            wiek = dni_od(data_el, dzis)
            if pierwszy:
                # Pierwszy odczyt: "nowe" znaczy coś tylko z datą publikacji.
                if wiek is not None and wiek <= 14:
                    zmiany.append({"typ": "nowe", "element": e, "data": data_el})
                elif wiek is not None and wiek >= 45:
                    widziane[k]["zgloszone_wisi"] = True
                    zmiany.append({"typ": "wisi", "element": e, "od": data_el, "dni": wiek, "data": dzis.isoformat()})
            else:
                zmiany.append({"typ": "nowe", "element": e, "data": data_el or dzis.isoformat()})
        else:
            if k not in poprzednio:
                w["powroty"] = w.get("powroty", 0) + 1
                zmiany.append({"typ": "wraca", "element": e, "powrot_nr": w["powroty"],
                               "pierwszy_raz_widziane": w["pierwszy"], "data": dzis.isoformat()})
            elif (dni_od(w["pierwszy"], dzis) or 0) >= 45 and not w.get("zgloszone_wisi"):
                w["zgloszone_wisi"] = True
                zmiany.append({"typ": "wisi", "element": e, "od": w["pierwszy"],
                               "dni": dni_od(w["pierwszy"], dzis), "data": dzis.isoformat()})
            w["ostatni"] = dzis.isoformat()
    for z in zmiany:
        z["rodzina"] = ROD_OBS.get(rodzaj, {}).get(z["typ"], "zmiana")
        z["zrodlo_url"] = (z.get("element") or {}).get("url", "")
        z["sonda"] = rodzaj
        z["typ"] = f"{rodzaj}_{z['typ']}"
    pamiec["ostatnio"] = teraz
    pelny[f"obs_{rodzaj}"] = pamiec
    m.zapisz_stan(f["id"], pelny)
    m.policz_uruchomienie(rodzaj, dzis)
    return zmiany, pierwszy


def k_obserwacja(m: Magazyn, args, dzis) -> int:
    f = m.firma(args[0])
    if not f:
        return pomin("nie ma takiej firmy", id=args[0])
    rodzaj = args[1]
    wejscie = wczytaj_json_arg(args[2])
    elementy = wejscie.get("elementy", []) if isinstance(wejscie, dict) else wejscie
    zmiany, pierwszy = _obserwuj(m, f, rodzaj, elementy, dzis)
    f["sondy"][rodzaj] = dzis.isoformat()
    f["ostatni_skan"] = dzis.isoformat()
    m.zapisz()
    return wypisz({"id": f["id"], "rodzaj": rodzaj, "pierwszy_odczyt": pierwszy,
                   "widoczne_teraz": len(elementy), "zmiany": zmiany})


# --- kontakty i sieć z LinkedIna --------------------------------------------


def k_kontakt_dodaj(m: Magazyn, args, dzis) -> int:
    wejscie = wczytaj_json_arg(args[0])
    lista = wejscie if isinstance(wejscie, list) else [wejscie]
    dodane = []
    for c in lista:
        if not c.get("imie"):
            continue
        ident = "k-" + slug(c["imie"])
        if any(k["id"] == ident for k in m.dane["kontakty"]):
            continue
        m.dane["kontakty"].append({"id": ident, "imie": c["imie"], "linkedin": c.get("linkedin"),
                                   "firma": c.get("firma"), "stanowisko": c.get("stanowisko"),
                                   "relacja": c.get("relacja"), "dodano": dzis.isoformat(),
                                   "ostatni_skan": None, "historia": []})
        dodane.append(ident)
    m.zapisz()
    return wypisz({"dodane": dodane, "kontaktow": len(m.dane["kontakty"])})


def k_kontakt_obserwacja(m: Magazyn, args, dzis) -> int:
    c = next((k for k in m.dane["kontakty"] if k["id"] == args[0]), None)
    if not c:
        return pomin("nie ma takiego kontaktu", id=args[0])
    obs = wczytaj_json_arg(args[1])
    zmiana = None
    nowa_firma = (obs.get("firma") or "").strip()
    if nowa_firma and c.get("firma") and slug(nowa_firma) != slug(c["firma"]):
        zmiana = {"typ": "zmiana_pracy", "rodzina": "zmiana",
                  "opis": f"{c['imie']}: {c['firma']} -> {nowa_firma}"
                          + (f" ({obs.get('stanowisko')})" if obs.get("stanowisko") else ""),
                  "data": dzis.isoformat(), "zrodlo_url": obs.get("url") or c.get("linkedin") or ""}
        c["historia"].append({"data": dzis.isoformat(), "z": c["firma"], "do": nowa_firma})
    if nowa_firma:
        c["firma"] = nowa_firma
    if obs.get("stanowisko"):
        c["stanowisko"] = obs["stanowisko"]
    c["ostatni_skan"] = dzis.isoformat()
    m.zapisz()
    return wypisz({"id": c["id"], "zmiana": zmiana, "firma_teraz": c.get("firma")})


DECYZYJNE = re.compile(r"prezes|ceo|founder|zalozyciel|wlasciciel|owner|dyrektor|director|head|kierownik|"
                       r"manager|menedzer|cmo|coo|cto|partner|vp|szef|lead", re.I)


def k_linkedin_import(m: Magazyn, args, dzis) -> int:
    """Eksport Connections.csv z LinkedIna -> zmiany pracy w sieci. Bez scrapowania, bez maili."""
    p = Path(args[0])
    if not p.is_file():
        return pomin("nie ma takiego pliku", plik=str(p))
    linie = p.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    start = next((i for i, l in enumerate(linie) if l.lower().startswith("first name")), None)
    if start is None:
        return pomin("to nie wyglada na Connections.csv z LinkedIna (brak naglowka First Name)")
    stara = m.dane["siec"]
    nowa, zmiany = {}, []
    kontakty = {slug(c["imie"]): c for c in m.dane["kontakty"]}
    for r in csv.DictReader(linie[start:]):
        imie = " ".join(x for x in ((r.get("First Name") or "").strip(), (r.get("Last Name") or "").strip()) if x)
        if not imie:
            continue
        klucz = (r.get("URL") or "").strip().rstrip("/") or slug(imie)
        firma = (r.get("Company") or "").strip()
        stan = (r.get("Position") or "").strip()
        nowa[klucz] = {"imie": imie, "firma": firma, "stanowisko": stan, "url": r.get("URL") or ""}
        byl = stara.get(klucz)
        c = kontakty.get(slug(imie))
        poprzednia = (byl or {}).get("firma") or (c or {}).get("firma")
        if firma and poprzednia and slug(firma) != slug(poprzednia):
            zmiany.append({"imie": imie, "z": poprzednia, "do": firma, "stanowisko": stan,
                           "url": r.get("URL") or "", "decyzyjne": bool(DECYZYJNE.search(slug(stan).replace("-", " "))),
                           "kontakt_z_projektu": c is not None})
            if c is not None:
                c.setdefault("historia", []).append({"data": dzis.isoformat(), "z": c.get("firma"), "do": firma})
        if c is not None and firma:  # kontakt z projektu sprawdzony za darmo, bez wyszukiwania
            c.update({"firma": firma, "stanowisko": stan or c.get("stanowisko"),
                      "linkedin": c.get("linkedin") or r.get("URL"), "ostatni_skan": dzis.isoformat()})
    pierwszy = not stara
    m.dane["siec"] = nowa
    m.dane["siec_import_poprzedni"] = m.dane.get("siec_import")
    m.dane["siec_import"] = dzis.isoformat()
    m.zapisz()
    zmiany.sort(key=lambda z: (not z["kontakt_z_projektu"], not z["decyzyjne"], z["imie"]))
    return wypisz({"osob_w_pliku": len(nowa), "pierwszy_import": pierwszy,
                   "poprzedni_import": m.dane["siec_import_poprzedni"],
                   "zmiany_pracy": len(zmiany), "zmiany": zmiany[:60],
                   "uwaga": ("pierwszy import to punkt odniesienia - zmiany pracy pojawia sie przy nastepnym"
                             if pierwszy else "lista posortowana: kontakty z projektow, potem stanowiska decyzyjne")})


# --- panel: firmy z priorytetem do lejka ------------------------------------


def k_panel(m: Magazyn, args, dzis) -> int:
    plik = Path(args[0])
    if not plik.is_file():
        return pomin("nie ma pliku lejka - panel nie jest postawiony albo inna sciezka", plik=str(plik))
    tresc = plik.read_text(encoding="utf-8")
    linie = tresc.splitlines()
    naglowki = [(i, l[3:].strip()) for i, l in enumerate(linie) if l.startswith("## ")]
    if not naglowki:
        return pomin("w pliku lejka nie ma etapow (naglowkow ##)")
    etap = opcja(args, "--etap") or naglowki[0][1]
    idx = next((i for i, n in naglowki if slug(n) == slug(etap)), None)
    if idx is None:
        return pomin(f"nie ma etapu {etap}", etapy=[n for _, n in naglowki])
    mnozniki = _mnozniki(m)
    dodane, zaktualizowane, pominiete = [], [], []
    for f in m.dane["firmy"]:
        if f["status"] != "obserwuj":
            continue
        o = _ocen_firme(m, f, dzis, mnozniki)
        if not o or not o["priorytet"]:
            continue
        s = o["sygnaly"][0]
        nazwa = f"[[{f['notatka']}|{f['nazwa']}]]" if f.get("notatka") else f["nazwa"]
        wpis = f"- {nazwa} - sygnał {s['data']}: {s['sygnal'].replace(',', ';')}, follow-up: {dzis.isoformat()}"
        klucz = slug(f["nazwa"])
        gdzie = next((i for i, l in enumerate(linie)
                      if l.lstrip().startswith(("- ", "* ")) and klucz and klucz in slug(l)), None)
        if gdzie is None:
            koniec = next((i for i, _ in naglowki if i > idx), len(linie))
            while koniec > idx + 1 and not linie[koniec - 1].strip():
                koniec -= 1
            linie.insert(koniec, wpis)
            naglowki = [(i + (1 if i >= koniec else 0), n) for i, n in naglowki]
            dodane.append(f["nazwa"])
        else:
            wczesniejsze = [n for i, n in naglowki if i < gdzie]
            etap_firmy = wczesniejsze[-1] if wczesniejsze else ""
            if slug(etap_firmy) == slug(etap) and "sygnał" in linie[gdzie]:
                linie[gdzie] = wpis
                zaktualizowane.append(f["nazwa"])
            else:
                pominiete.append({"firma": f["nazwa"], "etap": etap_firmy,
                                  "powod": "juz w lejku na innym etapie albo wpisana recznie - nie ruszam"})
    if dodane or zaktualizowane:
        kopia = m.dir / ".kopie" / f"{plik.stem}-{dzis.isoformat()}.md"
        kopia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(plik, kopia)
        zapisz_atomowo(plik, "\n".join(linie) + ("\n" if tresc.endswith("\n") else ""))
    return wypisz({"etap": etap, "dodane": dodane, "zaktualizowane": zaktualizowane, "pominiete": pominiete})


# --- widok w sejfie ----------------------------------------------------------


def _komorka(t) -> str:
    return str(t if t not in (None, "") else "-").replace("|", "/").replace("\n", " ")


def k_render(m: Magazyn, args, dzis) -> int:
    waz = m.ust["waznosc_sygnalu_dni"]
    mnozniki = _mnozniki(m)

    def nazwa(f):
        return f"[[{f['notatka']}|{f['nazwa']}]]" if f.get("notatka") else f["nazwa"]

    def wiersz(f, punkty=None):
        akt = [s for s in _aktywne(f, dzis, waz) if s["rodzina"] != "nie"]
        ost = max(akt, key=lambda s: s["data"]) if akt else None
        opis = f"{ost['data']}: {ost['sygnal']}" if ost else "-"
        return (f"| {_komorka(nazwa(f))} | {f['dodano']} | {_komorka(f.get('ostatni_skan'))} | "
                f"{len(akt)} | {_komorka(punkty)} | {_komorka(opis)} |")

    grupy = {g: [] for g in ("priorytet", "obserwuj", "nie-teraz", "napisano", "porzucona", "skreslona")}
    punkty = {}
    for f in m.dane["firmy"]:
        o = _ocen_firme(m, f, dzis, mnozniki) if f["status"] == "obserwuj" else None
        if o:
            punkty[f["id"]] = o["punkty"]
        if o and o["priorytet"]:
            grupy["priorytet"].append(f)
        else:
            grupy.setdefault(f["status"], []).append(f)
    naglowek = ("| Firma | Dodano | Ostatni skan | Aktywne sygnały | Punkty | Ostatni sygnał |\n"
                "|---|---|---|---|---|---|")
    tytuly = {"priorytet": "Do napisania teraz", "obserwuj": "Obserwowane",
              "nie-teraz": "Nie teraz (wracają same w wyznaczonym dniu)", "napisano": "Napisano",
              "porzucona": "Porzucone (bez sygnałów, poszła zwykła wiadomość)", "skreslona": "Skreślone"}
    czesci = [
        "---", f"aktualizacja: {dzis.isoformat()}", "skill: bfc/sygnaly", "---", "",
        "# Obserwowane firmy", "",
        "Ten plik generuje `/bfc:sygnaly` przy każdym skanie. Zmiany (dodaj, nie teraz, porzuć) rób "
        "przez skill - ręczne edycje tego pliku zostaną nadpisane. Pełna historia jest w `obserwowane.json`.", "",
    ]
    for g in tytuly:
        if not grupy.get(g):
            continue
        czesci += [f"## {tytuly[g]}", "", naglowek]
        for f in sorted(grupy[g], key=lambda x: (-punkty.get(x["id"], 0), x["dodano"])):
            czesci.append(wiersz(f, punkty.get(f["id"]))
                          + (f" do {f['status_do']}" if g == "nie-teraz" and f.get("status_do") else ""))
        czesci.append("")
    if m.dane["kontakty"]:
        czesci += ["## Kontakty z dawnych projektów", "", "| Kto | Firma teraz | Ostatnio sprawdzone |",
                   "|---|---|---|"]
        for c in m.dane["kontakty"]:
            czesci.append(f"| {_komorka(c['imie'])} | {_komorka(c.get('firma'))} | {_komorka(c.get('ostatni_skan'))} |")
        czesci.append("")
    st = _statystyka_wysylek(m)
    if st["razem"][0]:
        def pr(p):
            return f"{p[1]}/{p[0]} ({round(100 * p[1] / p[0])}%)" if p[0] else "-"
        czesci += ["## Co działa u Ciebie", "",
                   f"- Odpowiedzi po wiadomości z sygnałem: {pr(st['z_sygnalem'])}",
                   f"- Odpowiedzi po zwykłej wiadomości: {pr(st['bez_sygnalu'])}", ""]
    plik = m.dir / "Obserwowane.md"
    zapisz_atomowo(plik, "\n".join(czesci))
    return wypisz({"zapisano": str(plik), "firm": len(m.dane["firmy"])})


KOMENDY = {
    "init": (k_init, 0), "dodaj": (k_dodaj, 1), "lista": (k_lista, 0), "plan": (k_plan, 0),
    "status": (k_status, 2), "wynik": (k_wynik, 2), "skutecznosc": (k_skutecznosc, 0),
    "sygnal": (k_sygnal, 2), "ocena": (k_ocena, 0), "sonda": (k_sonda, 2),
    "obserwacja": (k_obserwacja, 3), "uzupelnij": (k_uzupelnij, 2), "kontakt-dodaj": (k_kontakt_dodaj, 1),
    "kontakt-obserwacja": (k_kontakt_obserwacja, 2), "linkedin-import": (k_linkedin_import, 1),
    "panel": (k_panel, 1), "render": (k_render, 0),
}


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in KOMENDY:
        return pomin("uzycie: sygnaly.py <komenda> <katalog> ...", komendy=sorted(KOMENDY))
    fn, ile = KOMENDY[argv[1]]
    reszta = argv[3:]
    poz = pozycyjne(reszta)
    if len(poz) < ile:
        return pomin(f"komenda {argv[1]} potrzebuje {ile} argumentow po katalogu")
    try:
        return fn(Magazyn(argv[2]), poz + [a for a in reszta if a not in poz], dzis_z(reszta))
    except (json.JSONDecodeError, ValueError) as e:
        return pomin(f"zle wejscie: {e}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
