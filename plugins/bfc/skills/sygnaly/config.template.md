---
utworzone: {{DATA}}
skill: bfc/sygnaly
---

# Konfiguracja: sygnały

Jakich sygnałów szukasz i co znaczą dla Twojej usługi, jest w `Mapa sygnałów.md` obok.
Tu są tylko ustawienia skanu. Możesz je zmieniać ręcznie - skill przepisze je do
`ustawienia.json` przy następnym uruchomieniu.

## Skan

- **Firm na jeden skan:** {{limit_na_skan}}
- **Tryb skanu:** auto (lekki, a pełny co tyle dni, ile niżej)
- **Pełny skan co (dni):** {{pelny_co_dni}}
- **Przegląd firm bez sygnałów po (dni):** {{przeglad_po_dniach}}
- **Priorytet od (punktów w oknie):** 2
- **Okno priorytetu (dni):** 21
- **Sygnał ważny przez (dni):** 90
- **Opinii Google na firmę w jednym skanie (max):** 30
- **Porównanie z archiwum strony przy pierwszym odczycie:** tak
- **Sygnał branżowy od (firm w segmencie):** 3
- **Proponuj wyłączenie sondy bez efektu po (dni / uruchomień):** 90 / 10

## Wagi sygnałów

Punkty za sygnał w oknie priorytetu. Uczenie na Twoich wynikach mnoży je od 0,5 do 2.

| Rodzina | Waga |
|---|---|
| wzrost | 1 |
| zmiana | 1 |
| bol | 1 |
| intencja | 1.5 |
| niespojnosc | 1.5 |
| kalendarz | 0.5 |

## Sondy

Włączona sonda ma kadencję w dniach. Skrypt pomija ją, dopóki termin nie minie.

| Sonda | Włączona | Co ile dni | Koszt |
|---|---|---|---|
| krs | tak | 7 | darmowa (API KRS) |
| strona | tak | 7 | darmowa (skrypt) |
| praca | {{sonda_praca}} | 14 | jedno wyszukiwanie modelu |
| reklamy | tak | 14 | darmowa z kluczem Meta, bez klucza ręcznie i tylko przy innym sygnale |
| opinie | {{sonda_opinie}} | 30 | Apify, ułamki grosza za opinię |
| instagram | {{sonda_instagram}} | 30 | Apify |
| baza | {{sonda_baza}} | 30 | jedno wyszukiwanie modelu |
| linkedin | nie | 30 | wyszukiwanie modelu, tylko gdy włączysz |

## Klucze

Wartości kluczy nigdy tu nie trafiają. Tylko nazwy zmiennych w pliku `.env` i stan.

- Apify (`APIFY_TOKEN` albo `APIFY_API_TOKEN`): {{klucz_apify}}
- Meta Ad Library (`META_ADLIB_TOKEN`): {{klucz_meta}}

## Kontakty z dawnych projektów

- Pilnować zmian pracy: {{kontakty}}
- Sposób: {{kontakty_sposob}} (eksport z LinkedIna raz w miesiącu albo wyszukiwanie co 30 dni)

<!--
Format ustawienia.json (skill zapisuje go z tej notatki, skrypt go czyta):
{
  "limit_na_skan": 15,
  "tryb_domyslny": "auto",
  "pelny_co_dni": 28,
  "przeglad_po_dniach": 90,
  "prog_priorytetu": 2.0,
  "okno_priorytetu_dni": 21,
  "waznosc_sygnalu_dni": 90,
  "opinie_max_na_firme": 30,
  "kontakty_co_dni": 30,
  "archiwum_strony": true,
  "branzowy_min_firm": 3,
  "wylaczanie_po_dniach": 90,
  "wylaczanie_min_uruchomien": 10,
  "wagi": {"wzrost": 1.0, "zmiana": 1.0, "bol": 1.0, "intencja": 1.5, "niespojnosc": 1.5, "kalendarz": 0.5},
  "sondy": {
    "krs": {"wlaczona": true, "co_dni": 7},
    "strona": {"wlaczona": true, "co_dni": 7},
    "praca": {"wlaczona": true, "co_dni": 14},
    "reklamy": {"wlaczona": true, "co_dni": 14},
    "opinie": {"wlaczona": false, "co_dni": 30},
    "instagram": {"wlaczona": false, "co_dni": 30},
    "baza": {"wlaczona": true, "co_dni": 30},
    "linkedin": {"wlaczona": false, "co_dni": 30}
  }
}
-->
