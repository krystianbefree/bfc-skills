---
name: sygnaly
description: Obserwuje firmy z Twojej listy i pokazuje, która właśnie ma powód, żeby kupić - zmiana w zarządzie w KRS, ogłoszenie o pracę, które wraca, nowe podstrony, piksel reklamowy na stronie, reklamy, fala złych opinii, zapytanie ofertowe z dotacji, były klient w nowej firmie. Sygnały dobiera pod Twoją usługę z krótkiego wywiadu, firmy dokłada z researchu (za Twoją zgodą), szuka też nowych firm z sygnałem, uczy się, które sygnały dają Ci odpowiedzi, a co 90 dni pyta, co zrobić z firmami, które milczą. Odpalasz na komendę, oszczędza tokeny. Użyj gdy ktoś mówi "sygnały", "skan sygnałów", "kto ma teraz powód kupić", "obserwuj tę firmę", "dodaj do obserwacji", "sprawdź moje firmy", "prospecting na sygnałach", "co się zmieniło u moich prospektów", "znajdź firmy z sygnałem", "odpisali mi", "co działa".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite, Skill, mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot, mcp__playwright__browser_evaluate
---

# Sygnały

Pilnujesz listy firm i mówisz człowiekowi, **która właśnie ma powód odpisać** i dlaczego. Lista firm mówi, do kogo pisać. Sygnał mówi, kiedy. Firm bez sygnału nie skreślasz: co 90 dni pytasz, czy obserwować dalej, czy napisać do nich zwykłą wiadomość.

Skill działa **tylko na komendę** i jest oszczędny z założenia. Skrypt sam sprawdza tanie źródła (KRS z historią, strona z sitemapą, narzędziami i ogłoszeniami w kodzie, archiwum strony), porównuje z tym, co widział, i oddaje Ci wyłącznie zmiany. Przy pierwszym odczycie firmy sięga w przeszłość, więc sygnały widać od razu. Brak zmian oznacza zero pracy modelu.

Silnik: `${CLAUDE_PLUGIN_ROOT}/skills/sygnaly/solutions/sygnaly.py`. Uruchamiaj łańcuchem `python3` -> `python` -> `py -3`, zawsze pełną ścieżką. Niżej skrót `S <komenda>` oznacza:

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/sygnaly/solutions/sygnaly.py" <komenda> "<sejf>/BFC Skille/sygnaly" ...
```

Dane wejściowe w JSON zapisuj do pliku w `<sejf>/BFC Skille/sygnaly/.tmp/` i podawaj ścieżkę (cudzysłowy w powłoce Windows psują JSON). Każda komenda zwraca jeden obiekt JSON.

## Krok 0 - fundament, ustawienia, mapa sygnałów

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Fundament w `<sejf>/BFC Skille/`: `Oferta.md`, `Grupa docelowa.md`, `Metoda prospectingu.md`. **Brak któregoś -> „Najpierw odpal `/bfc:start`, żeby zbudować fundament. Bez niego nie wiem, który sygnał jest Twój, a który to szum."**
3. Brak `<sejf>/BFC Skille/sygnaly/Config.md` albo są w nim `TODO:` -> wywiad z `wywiad.md` (mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`). Zapisuje `Config.md` (z `config.template.md`) i `Mapa sygnałów.md` (kształt: `blueprints/mapa-sygnalow.md`). Pierwszy raz po wywiadzie -> walidacja na żywo na jednej firmie (koniec `wywiad.md`).
4. `S init`, potem przepisz ustawienia z `Config.md` do `ustawienia.json` (format w `config.template.md`). Przy każdym uruchomieniu, bo człowiek mógł poprawić Config ręcznie.

## Wybór trybu

| Tryb | Kiedy | Co robisz |
|---|---|---|
| skan | „sygnały", „sprawdź moje firmy", sama komenda | Kroki 1-6. Lekki albo pełny, niżej |
| szukaj | „znajdź firmy z sygnałem", „kto teraz szuka X" | `blueprints/szukaj.md` |
| dodaj | „obserwuj X", lista firm | `blueprints/obserwowane.md`, Dodawanie |
| kontakty | „byli klienci", „wrzucam eksport z LinkedIna" | `blueprints/obserwowane.md`, Kontakty i eksport LinkedIna |
| wynik | „odpisali", „mam spotkanie z X", „cisza" | `S wynik <id> odpisali|spotkanie|klient|cisza`, jedno zdanie potwierdzenia |
| co działa | „co działa", „które sygnały dają odpowiedzi" | `blueprints/uczenie.md` |
| lista | „kogo obserwuję" | `S lista` + `S render`, krótki skrót |
| ustawienia | „zmień sygnały", „podepnę klucz" | popraw `Config.md` albo `Mapa sygnałów.md` jednym pytaniem |

**Skan lekki czy pełny.** Lekki: tylko sondy skryptowe (KRS, strona, reklamy z kluczem), zero wyszukiwań modelu i zero Apify. Pełny: wszystko. Domyślnie `auto`: pełny co tyle dni, ile w `Config.md` (domyślnie 28), pomiędzy lekki. Człowiek mówi „pełny" albo „lekki" -> `--tryb pelny|lekki`.

## Krok 1 - plan

`S plan [--tryb ...]`. Dostajesz: tryb, firmy i sondy na dziś, koszty, przegląd 90-dniowy, firmy po terminie „nie teraz", kontakty do sprawdzenia, propozycje wyłączenia sond, datę ostatniego importu z LinkedIna.

- Lista pusta -> powiedz, jak dodać firmy (ręcznie, z `/bfc:research` albo trybem szukaj), i zakończ.
- Plan jednym zdaniem: tryb, ile firm, ile sond darmowych, płatnych, wyszukiwań modelu, ile czeka przez limit.
- **Pytaj o zgodę tylko**, gdy są sondy płatne albo więcej niż 10 wyszukiwań modelu.
- `propozycje_wylaczenia_sond` -> po skanie zapytaj (Krok 6), nie przed.
- Import z LinkedIna starszy niż 30 dni, a człowiek go używa -> przypomnij jednym zdaniem na końcu.

## Krok 2 - przegląd firm bez sygnałów

Jest coś w `przeglad` -> przeprowadź go wg `blueprints/przeglad.md`, zanim zaczniesz skanować.

## Krok 3 - sondy

Katalog źródeł, kosztów i sposobu wykonania: `blueprints/zrodla.md`.

1. **Skryptowe** (`krs`, `strona`, `opinie`, `instagram`, `reklamy`) -> `S sonda <id> <sonda>`. Czytasz tylko `zmiany` i `stan`. `skipped` -> lista `[do ręki]`, nie ponawiaj. Sonda strony sama czyta ogłoszenia zapisane w kodzie strony; jeśli je znalazła, sonda `praca` znika z planu dla tej firmy.
2. **Modelowe** (`praca`, `baza`, `linkedin`, `reklamy` bez klucza) -> tylko w skanie pełnym, najtańszą drogą z `blueprints/zrodla.md`, wynik przez `S obserwacja <id> <rodzaj> <plik.json>`.
3. **Kalendarz** -> z `Mapa sygnałów.md`, bez wyszukiwania.
4. **Kontakty** z planu -> `blueprints/obserwowane.md`. Kontakty sprawdzone eksportem z LinkedIna nie pojawiają się w planie.

Pierwszy odczyt nie jest pusty: skrypt zwraca zmiany z historii KRS, z porównania z archiwum strony, ze świeżych podstron w sitemapie, z dat opinii, ogłoszeń i startu reklam. Traktuj je jak każde inne zmiany.

## Krok 4 - interpretacja i zapis

Każdą zmianę przepuszczasz przez `Mapa sygnałów.md` i `blueprints/interpretacja.md`: czy to sygnał dla **tej usługi** (test jednego zdania), z której rodziny, czy jest niespójność (pola `stan` z różnych sond), czy to sygnał na „nie". Zmiana, która nie przechodzi testu, nie jest zapisywana.

Potwierdzone -> `S sygnal <id> <plik.json>`, zawsze z polami `typ` i `sonda` przepisanymi ze zmiany (z nich liczy się uczenie i sygnały branżowe) oraz z `waga`, jeśli mapa daje temu sygnałowi inną wagę niż domyślna. Każdy sygnał ma `zrodlo_url` (poza kalendarzem) i datę zdarzenia.

## Krok 5 - ocena, raport, panel

1. `S ocena` -> firmy z punktami i flagą `priorytet` (suma wag sygnałów w oknie, uczona na wynikach człowieka), sygnały na „nie", `sygnaly_branzowe`.
2. `S render` -> `Obserwowane.md`.
3. Raport, notatki firm, sygnały branżowe: `blueprints/raport.md`.
4. Panel: jest `/bfc:panel` (znajdź plik `Pozyskiwanie.md` w sejfie narzędziem Glob) -> `S panel "<ścieżka do Pozyskiwanie.md>"`. Firmy z priorytetem trafiają do pierwszego etapu lejka z przypomnieniem na dziś, więc pojawią się w zakładce Dziś. Firm na dalszych etapach skrypt nie rusza.
5. Sygnał na „nie" -> `AskUserQuestion`: nie teraz (z datą) / skreśl / zostaw, potem `S status`.

## Krok 6 - co dalej

W czacie krótko: firmy priorytetowe (co się zmieniło, hipoteza, pierwsze zdanie), sygnały branżowe, ile firm z jednym sygnałem czeka, `[do ręki]`. Zaproponuj `/bfc:cold-mail` dla najmocniejszej. Po wysłaniu: `S status <id> napisano`. Gdy człowiek później powie, że odpisali albo była cisza: `S wynik`.

Na końcu, jeśli są: propozycje wyłączenia sond (`AskUserQuestion`, przy zgodzie popraw tabelę sond w `Config.md`) i jedno zdanie o brakującym kluczu (jak podpiąć: `wywiad.md`, pole `klucze`).

## Oszczędność (twarde)

- **Skrypt najpierw.** Model czyta tylko `zmiany` i `stan`. Nie otwieraj `obserwowane.json` ani plików w `stan/`.
- **Skan lekki domyślnie**, pełny co kilka tygodni albo na prośbę.
- **Jedno wyszukiwanie na sondę modelową.** Stronę otwierasz, gdy zmiana ma wejść jako sygnał i brakuje linku.
- **Reklamy bez klucza** przeglądarką tylko u firm z innym sygnałem.
- **Limit firm na skan** i **kadencje sond** z `Config.md`. Sondy, które nic nie dają, skrypt zgłasza do wyłączenia.
- **Nie skanuj od razu po dodaniu firm**, chyba że człowiek prosi.

## Ton

Do człowieka krótko i konkretnie. Każdy fakt o firmie z linkiem, bo to jego nazwisko pójdzie pod wiadomością. Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.
