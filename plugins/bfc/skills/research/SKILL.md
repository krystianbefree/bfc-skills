---
name: research
description: Znajduje firmy pasujące do Twojego profilu klienta, AUDYTUJE każdą przez soczewkę Twojej usługi (strona, social, reklamy, opinie) i liczy score dopasowania 1-100 z dominującym problemem i gotowym haczykiem na pierwsze zdanie maila. Czyta fundament z /bfc:start, nie pyta od zera. Użyj gdy ktoś mówi "znajdź mi klientów", "research firm", "zrób listę prospektów", "poszukaj firm z branży X", "kogo mogę zaczepić", "lead gen", "sprawdź tę firmę przed rozmową", "zaudytuj tę firmę".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite, Skill, mcp__playwright__browser_navigate, mcp__playwright__browser_evaluate, mcp__playwright__browser_take_screenshot, mcp__chrome-devtools__lighthouse_audit, mcp__chrome-devtools__navigate_page
---

# Research firm

Znajdujesz firmy, audytujesz każdą pod kątem tego, co **Ty** sprzedajesz, i zostawiasz w sejfie notatkę ze score i gotowym haczykiem - taką, z której cold-mail od razu napisze pierwsze zdanie. Nie robisz raportu dla samego raportu.

## Krok 0 - fundament i narzędzia

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Sprawdź fundament w `<sejf>/BFC Skille/`: `Oferta.md`, `Grupa docelowa.md`, `Metoda prospectingu.md`. **Brak któregoś -> „Najpierw odpal `/bfc:start`, żeby zbudować fundament (kogo szukasz, co sprzedajesz, jak oceniasz firmę). Bez tego research znajdzie same nazwy."** Nie rób tu własnego wywiadu - fundament jest źródłem prawdy.
3. Wykryj narzędzia (cross-platform, uruchom łańcuchem `python3` -> `python` -> `py -3`): `python3 "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-narzedzia.py"`. Zasady i degradacja: `${CLAUDE_PLUGIN_ROOT}/wspolne/narzedzia.md`. Zakładamy, że masz Firecrawl/Apify/Playwright; jak nie, audyt degraduje uczciwie (patrz `blueprints/audyt.md`).

## Krok 0.5 - kompilacja taksonomii (raz, cache'owane)

Score musi być deterministyczny, więc nie czyta prozy. Skompiluj fundament w strukturę wg `blueprints/taksonomia.md`:

- `Oferta.md` (problem -> usługa -> sygnał) + `Metoda prospectingu.md` -> `<sejf>/BFC Skille/research/Taksonomia.json`.
- `Grupa docelowa.md` -> `<sejf>/BFC Skille/research/icp.json`.

Kompiluj na starcie przebiegu. Jest już `Taksonomia.json` i fundament się nie zmienił -> użyj go ponownie; w razie wątpliwości skompiluj od nowa (to tanie: 2 pliki wczytać, 2 zapisać). Nie polegaj na porównaniu `mtime` przez powłokę - nieprzenośne na Windows. Po kompilacji powiedz jednym zdaniem, co wyszło („z Twojej oferty 3 klasy problemów, segment lokalna").

## Krok 1 - zakres przebiegu

- Konkretna firma („sprawdź mi X") -> pomiń discovery, leć od razu do Kroku 3. **Najpierw ustal jej segment, branżę, miasto i wielkość** (zapytaj albo wywnioskuj ze strony) - bez tego bramka segmentu i dopasowanie ICP nie policzą się poprawnie.
- Segment („dentyści w Poznaniu") -> nadpisuje domyślny z `Grupa docelowa.md`.
- Nic -> domyślny profil z `Grupa docelowa.md`, powiedz jednym zdaniem, czego szukasz.

Ustal liczbę firm (domyślnie z `config.template.md`/Config). Powyżej ~15 na przebieg ostrzeż, że potrwa (każda to audyt), i zaproponuj tury.

## Krok 2 - discovery

Cel: lista firm z nazwą, stroną, segmentem. Źródła i dobór wg segmentu: `blueprints/zrodla.md` (napędzane `Grupa docelowa.md`).

1. Znajdź kandydatów z serwisów/katalogów pod segment (Firecrawl albo WebSearch).
2. Odrzuć duplikaty i firmy już w sejfie: użyj narzędzia **Grep** (`-i -l` po nazwie firmy w sejfie), nie literalnego `grep` z powłoki (nie ma go na Windows) - powiedz, co pominąłeś.
3. Zastosuj `dyskwalifikatory` z `Grupa docelowa.md` **od razu**, zanim zaczniesz audyt. Nie audytuj firmy, która i tak odpadnie.
4. Zapisz `<folder>/.audit/_prospekty.json`: `[{name, url, source, rating, review_count, city, industry, segment}]`.

Za mało firm -> powiedz ile i skąd, zaproponuj rozszerzenie (inne miasto, sąsiednia branża, inne źródło). Nie dobieraj losowych, żeby dobić liczbę.

## Krok 3 - audyt (per firma)

Pełna procedura: `blueprints/audyt.md`. Dla każdej firmy zbierz **goły kolektor** `raw-signals.json` - odpalaj TYLKO sondy, których `zrodlo` jest w `Taksonomia.json` (metoda człowieka steruje kolektorem). Interpretacja sygnałów: `blueprints/dane-i-sygnaly.md`.

Twarde: każdy sygnał ma źródło; nie znalazłeś -> `[do ręki]`, nigdy zmyślona liczba; brak narzędzia degraduje do `[do ręki]`, nie blokuje. Incydent (martwa domena/5xx) -> zapisz flagi i przerwij audyt tej firmy.

## Krok 4 - score (twardy skrypt)

Uruchom łańcuchem `python3` -> `python` -> `py -3` (na Windows nie ma `python3`), pełną ścieżką:

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/research/solutions/score.py" <raw-signals.json> <Taksonomia.json> <icp.json>
```

Zwraca deterministycznie: `score 1-100`, `dominant` (klasa+usługa+cena+severity), `secondary`, `hook_material`, `gate`. `gate=0` -> firma odpada, nie zakładaj pełnej notatki. Brak Pythona -> policz ręcznie wg formuły z docstringa `solutions/score.py` (jest tam jawnie).

## Krok 5 - zapis

Kształt notatki i tabeli: `blueprints/notatka.md`.

1. **Notatka per firma** w folderze z Config, nazwa `<Nazwa firmy>.md`: score, dominujący problem -> Twoja usługa, dowody-sygnały z linkami, haczyk, `[Do ręki]`, ocena, pusta `## Kontakt`.
2. **Tabela zbiorcza** `Prospekty <RRRR-MM-DD>.md`, sortuj po score, odpadłe na dole z powodem.
3. Notatka firmy już istnieje -> nie nadpisuj, pokaż różnice, zapytaj o aktualizację z datą.

Na koniec skrót w czacie: ile firm, ile się kwalifikuje (score > próg), top 3 ze score i jednozdaniowym uzasadnieniem, gdzie pliki. Nie wklejaj całej tabeli. Zaproponuj `/bfc:cold-mail` na najlepszą (weźmie haczyk i dominujący problem z notatki).

## Ton i jakość

Notatka czytelna dla człowieka, który wróci do niej za tydzień. Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.
