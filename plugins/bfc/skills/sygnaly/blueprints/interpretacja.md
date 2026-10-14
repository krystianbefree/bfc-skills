# Interpretacja - kiedy zmiana jest sygnałem

Skrypt zgłasza zmiany. Ty decydujesz, które z nich są sygnałem dla usługi człowieka. Narzędzie
znajdzie zmianę, ale jej nie przeczyta. To jest jedyne miejsce w skanie, gdzie praca modelu
naprawdę coś daje, więc tu się nie spiesz.

## Test jednego zdania

Dokończ: **„Ta zmiana sprawia, że usługa z `Oferta.md` jest im teraz bardziej potrzebna, bo…"**.
Nie umiesz dokończyć konkretnie -> to był news, nie sygnał. Nie zapisuj go.

Ten sam fakt bywa sygnałem dla jednej usługi i szumem dla innej. Rozstrzyga `Mapa sygnałów.md`.

## Ten sam sygnał, kilka historii

Przykład: gabinet szuka osoby do marketingu. Może znaczyć, że mają budżet i chcą rosnąć. Może, że
postanowili robić to u siebie i jest za późno. Może, że szukają od dawna i potrzebują kogoś na czas
rekrutacji. Rozstrzyga **drugi sygnał**: jak długo wisi ogłoszenie (sonda praca, typ `wisi`/`wraca`),
czy działają reklamy, co dzieje się na profilu.

Dlatego priorytet daje dopiero zestaw. Każdy sygnał ma wagę (domyślnie 1, intencja i niespójność 1,5,
kalendarz 0,5, zmiana pracy dawnego kontaktu 2), a priorytet zaczyna się od 2 punktów w oknie 21 dni.
Jeden zwykły sygnał zapisujesz, ale firma czeka na drugi. Zapytanie ofertowe z rekrutacją albo zmiana
pracy kontaktu wystarczą same.

Wagi zmienia mapa (pole `waga` przy sygnale, gdy człowiek uznał coś za mocniejsze) i uczenie na wynikach
(`uczenie.md`): rodzina, po której ten człowiek dostaje odpowiedzi, z czasem waży więcej.

## Niespójność

Dwie publiczne rzeczy, które do siebie nie pasują, od razu dają hipotezę. Szukaj ich w polach `stan`
z różnych sond tej samej firmy (lista domyślnych w `mapa-sygnalow.md`). Najczęstsze źródło to sonda strony:
`narzedzia`, `ma_piksel_reklamowy`, `ma_formularz`, `rok_stopki`, `problem_ssl` zestawione z reklamami,
opiniami albo Instagramem. Niespójność zapisujesz jako jeden sygnał rodziny `niespojnosc`, `typ`
opisujący parę (np. `reklamy_bez_piksela`), z linkiem do obu źródeł w opisie. Sama w sobie daje priorytet.

## Ciche i głośne

Głośny sygnał (post o dotacji, nagroda, otwarcie ogłoszone w social mediach) widzą wszyscy. Ciche
(zmiana w KRS, ogłoszenie odświeżone trzeci raz, reklamy, które zniknęły) widzi mało kto. Głośne
zapisuj tylko, jeśli mapa ich nie wyklucza, i nie traktuj ich jako silniejszych.

## Termin ważności

Sygnał ma datę zdarzenia, nie skanu. Starszy niż okres ważności z `Config.md` (domyślnie 90 dni)
skrypt przestaje liczyć. Nie zapisuj sygnału, którego zdarzenie było dawno, tylko dlatego, że
dopiero teraz go zauważyłeś. Zmiana pracy kontaktu i nowa osoba w zarządzie są najmocniejsze
w pierwszych tygodniach.

## Sygnały na „nie"

- **Nie teraz** (odkładasz z datą, firma wraca sama): zmiana właściciela albo przejęcie w toku,
  nowy szef, który dopiero zaczął, środek sezonu.
- **Skreśl**: otwarta likwidacja albo upadłość w KRS, świeżo obsadzone stanowisko, którego dotyczy
  usługa, dwie pełne sekwencje bez reakcji.

Zapisujesz je jako rodzinę `nie`. Skrypt zdejmuje wtedy priorytet, a Ty pytasz człowieka o status.

## Jak opisać sygnał w zapisie

```json
{"rodzina": "zmiana", "sygnal": "Nowa osoba w zarządzie", "data": "2026-10-08",
 "opis": "KRS: doszła 1 osoba, odeszła 1 (CZŁONEK ZARZĄDU). Dla mnie: nowy szef porządkuje procesy.",
 "zrodlo_url": "https://...", "sonda": "krs", "typ": "zarzad"}
```

- `sygnal` krótko, jak nagłówek. To widać w `Obserwowane.md`.
- `opis` to fakt + co znaczy dla usługi (z mapy). Bez przymiotników.
- `sonda` i `typ` przepisujesz ze zmiany zwróconej przez skrypt. Z nich liczy się uczenie i sygnały
  branżowe, więc ten sam rodzaj zmiany ma zawsze ten sam typ.
- `waga` tylko wtedy, gdy mapa daje temu sygnałowi inną wagę niż domyślna dla rodziny.
- Rodziny: `wzrost`, `zmiana`, `bol`, `intencja`, `kalendarz`, `niespojnosc`, `nie`.

## Jak sygnał wchodzi do wiadomości (dla raportu i cold-maila)

- Piszesz o tym, co firma **zrobiła publicznie i zawodowo**: „widzę, że od sierpnia szukacie drugiej
  osoby na recepcję", „gratuluję otwarcia w Gdańsku".
- Nie piszesz o tym, co firmie się przytrafiło („widziałem, że zwolniliście ludzi") ani o tym, co
  podejrzałeś („byłeś na mojej stronie"). Nic z życia prywatnego.
- Sygnał to pierwsze zdanie, nie cała wiadomość. Hipotezę formułujesz jako przypuszczenie
  („zakładam, że…"), bo nią jest.
- Zła opinia nigdy nie jest cytowana. Najwyżej jako ogólny wątek („obsługa zapytań").
