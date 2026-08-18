#!/usr/bin/env python3
"""
Score prospekta 1-100 + dominujący problem. Deterministyczny, powtarzalny.

To jedyny kawałek researchu, który MUSI być twardym kodem: te same wejścia dają
ten sam wynik i te same tiebreakery. LLM liczący score „na oko" dryfuje między
przebiegami. Czysty stdlib (json, re, sys) - działa identycznie na macOS, Linux
i Windows, zero basha.

Uruchamianie (użyj łańcucha: python3 -> python -> py -3, zależnie od systemu):
  python3 score.py raw-signals.json Taksonomia.json icp.json

Wejście:
  1. raw-signals.json  - goły kolektor jednej firmy (audyt, bez klasyfikacji)
  2. Taksonomia.json   - skompilowana z Oferta.md + Metoda prospectingu.md (klubowicza)
  3. icp.json          - zserializowane pola z Grupa docelowa.md
Wyjście: JSON na stdout - {score, gate, icp_fit, dominant, secondary, hook_material, powod}.

FORMUŁA (gdyby zabrakło Pythona, policz ręcznie wg tego):
  gate = 0 gdy: domena martwa (NXDOMAIN) LUB segment != segment ICP LUB trafiony dyskwalifikator
              (dopasowanie po granicy słowa, tylko po polach tożsamości: name/branza/miasto/industry).
  gate = 0  ->  score = 0, „odpada", nie audytuj dalej.
  ICP_fit = 0.4*branza + 0.3*miasto + 0.3*wielkosc   (każdy wymiar 0 / 0.5 / 1, dopasowanie po słowie)
  severity per klasa z Taksonomii:
     prog (kierunek 'ponizej'): reading < prog_krytyczny -> sev_krytyczny;
                                 reading < prog_sredni    -> sev_sredni; inaczej 0.
     prog (kierunek 'powyzej'): reading > prog_krytyczny -> sev_krytyczny; itd.
     incydent: bool przy zrodle == true -> sev_incydent.
     warunek (opcjonalny): jeśli 'warunek_pole' < 'warunek_min' -> sev 0 (np. engagement liczymy
             tylko gdy followers >= 500).
     brak odczytu / '[do reki]' -> sev 0 (nie karzemy braku narzędzia).
     klasa social (kategoria=='social' albo 'social' w nazwie) pomijana, gdy social_relevant == false.
  dominujący = sort findings po (severity malejąco, priorytet_z_oferty rosnąco). Pierwszy.
  pain_norm = dominant.severity / 10
  offer_bonus = +8 gdy dominujący sygnał ma konkretną liczbę (gotowy haczyk), inaczej 0.
  SCORE = clamp( round( 100*gate*(0.4*ICP_fit + 0.6*pain_norm) + offer_bonus ), 1, 100 ).
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _dig(obj: Any, dotted: str) -> Any:
    """Odczyt po ścieżce z kropkami, np. 'lighthouse.performance'. None gdy brak."""
    node = obj
    for part in str(dotted).split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def _is_missing(value: Any) -> bool:
    """Brak odczytu albo znacznik ręcznego sprawdzenia."""
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, str) and value.strip().lower() in ("[do reki]", "[do ręki]", "brak", "n/a", ""):
        return True
    return False


def _num(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _word_match(term: str, text: str) -> bool:
    """Dopasowanie po granicy słowa (Unicode), nie gołe 'in'. 'it' NIE trafi w 'fitness',
    ale 'dentysta' trafi w 'dentysta dzieciecy'. Pusty term -> False."""
    term = (term or "").strip().lower()
    text = (text or "").lower()
    if not term or not text:
        return False
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None


# ── dopasowanie do ICP ─────────────────────────────────────────────────────
def _match_level(value: Optional[str], glowne: List[str], pokrewne: List[str]) -> float:
    """1.0 gdy trafia w główne, 0.5 w pokrewne, 0.0 poza. Po granicy słowa."""
    v = (value or "").strip().lower()
    if not v:
        return 0.0
    if any(_word_match(g, v) for g in glowne):
        return 1.0
    if any(_word_match(p, v) for p in pokrewne):
        return 0.5
    return 0.0


def _icp_fit(raw: Dict[str, Any], icp: Dict[str, Any]) -> float:
    branza = _match_level(raw.get("branza"),
                          icp.get("branze_glowne", []), icp.get("branze_pokrewne", []))
    zasieg = (icp.get("zasieg") or "").strip().lower()
    if zasieg in ("cała polska", "cala polska", "online", "ogólnopolski", "ogolnopolski"):
        miasto = 1.0
    else:
        miasta = icp.get("miasta", [])
        firm_miasto = (raw.get("miasto") or "").strip().lower()
        miasto = 1.0 if firm_miasto and any(_word_match(m, firm_miasto) for m in miasta) else 0.0
    wielkosc = _match_level(raw.get("wielkosc"),
                            icp.get("wielkosc", []), icp.get("wielkosc_sasiednia", []))
    return round(0.4 * branza + 0.3 * miasto + 0.3 * wielkosc, 3)


# ── severity per wpis taksonomii ───────────────────────────────────────────
def _is_social(entry: Dict[str, Any]) -> bool:
    if entry.get("kategoria") == "social":
        return True
    return "social" in str(entry.get("klasa", "")).lower()


def _severity(entry: Dict[str, Any], raw: Dict[str, Any], social_relevant: bool) -> Tuple[int, Any, bool]:
    """Zwraca (severity, wartosc_odczytu, ma_konkret). severity 0 = nie liczy się."""
    if _is_social(entry) and not social_relevant:
        return 0, None, False

    sygnal = entry.get("sygnal", {})

    # Warunek dodatkowy (np. engagement liczymy tylko gdy followers >= 500).
    warunek_pole = sygnal.get("warunek_pole")
    if warunek_pole:
        wart = _num(_dig(raw, warunek_pole))
        prog_min = _num(sygnal.get("warunek_min"))
        if wart is None or (prog_min is not None and wart < prog_min):
            return 0, None, False

    zrodlo = sygnal.get("zrodlo")
    odczyt = _dig(raw, zrodlo) if zrodlo else None
    if _is_missing(odczyt):
        return 0, None, False

    if sygnal.get("typ") == "incydent":
        sev = int(sygnal.get("sev_incydent", 0))
        return (sev, True, False) if (bool(odczyt) and sev > 0) else (0, None, False)

    liczba = _num(odczyt)
    if liczba is None:
        return 0, None, False

    kierunek = sygnal.get("kierunek", "ponizej")
    prog_k = _num(sygnal.get("prog_krytyczny"))
    prog_s = _num(sygnal.get("prog_sredni"))
    sev_k = int(sygnal.get("sev_krytyczny", 8))
    sev_s = int(sygnal.get("sev_sredni", 5))

    def worse_than(border: Optional[float]) -> bool:
        if border is None:
            return False
        return liczba < border if kierunek == "ponizej" else liczba > border

    if worse_than(prog_k):
        return sev_k, liczba, True
    if worse_than(prog_s):
        return sev_s, liczba, True
    return 0, liczba, True


# ── bramka ─────────────────────────────────────────────────────────────────
_IDENTITY_FIELDS = ("name", "branza", "miasto", "industry", "city", "opis")


def _gate(raw: Dict[str, Any], icp: Dict[str, Any]) -> Tuple[int, str]:
    if raw.get("domena_martwa"):
        return 0, "domena nie istnieje (NXDOMAIN)"
    seg_icp = (icp.get("segment") or "").strip().lower()
    seg_firm = (raw.get("segment") or "").strip().lower()
    if seg_icp and seg_firm and seg_icp != seg_firm:
        return 0, f"segment nie pasuje ({seg_firm} != {seg_icp})"
    # Dyskwalifikatory tylko po polach tożsamości (nie po liczbach/boolach) i po granicy słowa.
    hay = " ".join(str(raw.get(f, "")) for f in _IDENTITY_FIELDS if isinstance(raw.get(f), str))
    for dq in icp.get("dyskwalifikatory", []):
        if _word_match(str(dq), hay):
            return 0, f"dyskwalifikator: {dq}"
    return 1, ""


def _clamp(x: float, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(x)))


def score(raw: Dict[str, Any], tax: Dict[str, Any], icp: Dict[str, Any]) -> Dict[str, Any]:
    gate, powod = _gate(raw, icp)
    if gate == 0:
        return {"score": 0, "gate": 0, "powod": powod, "icp_fit": None,
                "dominant": None, "secondary": [], "hook_material": None}

    social_relevant = bool(icp.get("social_relevant", True))
    findings: List[Dict[str, Any]] = []
    for entry in tax.get("klasy", []):
        sev, wartosc, ma_konkret = _severity(entry, raw, social_relevant)
        if sev > 0:
            findings.append({
                "klasa": entry.get("klasa"),
                "usluga": entry.get("usluga"),
                "cena": entry.get("cena"),
                "gdzie": entry.get("gdzie"),
                "priorytet": int(entry.get("priorytet", 99)),
                "severity": sev,
                "sygnal_zrodlo": entry.get("sygnal", {}).get("zrodlo"),
                "wartosc": wartosc,
                "ma_konkret": ma_konkret,
            })

    icp_fit = _icp_fit(raw, icp)

    if not findings:
        s = _clamp(round(100 * (0.4 * icp_fit)), 1, 100)
        return {"score": s, "gate": 1, "powod": "brak widocznego problemu z Twojej działki",
                "icp_fit": icp_fit, "dominant": None, "secondary": [], "hook_material": None}

    findings.sort(key=lambda f: (-f["severity"], f["priorytet"]))
    dominant = findings[0]
    secondary = findings[1:]

    pain_norm = dominant["severity"] / 10.0
    offer_bonus = 8 if dominant["ma_konkret"] else 0
    s = _clamp(round(100 * (0.4 * icp_fit + 0.6 * pain_norm) + offer_bonus), 1, 100)

    hook_material = None
    if dominant["ma_konkret"] and dominant["wartosc"] is not None:
        hook_material = {"sygnal": dominant["sygnal_zrodlo"], "wartosc": dominant["wartosc"],
                         "gdzie": dominant["gdzie"], "klasa": dominant["klasa"]}

    return {
        "score": s, "gate": 1, "powod": "",
        "icp_fit": icp_fit,
        "dominant": {k: dominant[k] for k in ("klasa", "usluga", "cena", "gdzie", "severity", "wartosc")},
        "secondary": [{"klasa": f["klasa"], "usluga": f["usluga"]} for f in secondary],
        "hook_material": hook_material,
    }


def main(argv: List[str]) -> int:
    if len(argv) < 4:
        sys.stderr.write("użycie: score.py raw-signals.json Taksonomia.json icp.json\n")
        return 2
    result = score(_read_json(argv[1]), _read_json(argv[2]), _read_json(argv[3]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
