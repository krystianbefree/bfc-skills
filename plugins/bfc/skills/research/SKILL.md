---
name: research
description: Znajduje firmy pasujące do Twojego profilu klienta i robi z nich notatki w sejfie Obsidian - kontakt, sygnały budżetu, widoczne problemy, kto decyduje. Przy pierwszym użyciu pyta o Twoją branżę, źródła i to, jakie dane Cię interesują. Użyj gdy ktoś mówi "znajdź mi klientów", "research firm", "zrób listę prospektów", "poszukaj firm z branży X", "kogo mogę zaczepić", "lead gen", "sprawdź tę firmę przed rozmową".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite, Skill
---

# Research firm

Znajdujesz firmy, sprawdzasz je i zostawiasz w sejfie notatki, z których da się od razu napisać
maila albo wejść na rozmowę. Nie robisz raportu dla samego raportu.

## Krok 0 - konfiguracja

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Brak `<sejf>/BFC Skille/Profil.md` -> przeprowadź wywiad profilowy
   (`${CLAUDE_PLUGIN_ROOT}/wspolne/profil.wywiad.md`), zapisz, wróć tutaj.
3. Przeczytaj `Profil.md`.
4. Brak `<sejf>/BFC Skille/research/Config.md` albo są w nim pola `TODO:` -> przeprowadź wywiad
   z `wywiad.md` (mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`), zapisz z
   `config.template.md`. Przy istniejącym pliku pytaj **tylko** o `TODO:`.
5. Wykryj narzędzia: `bash "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-narzedzia.sh"`.
   Zasady użycia: `${CLAUDE_PLUGIN_ROOT}/wspolne/narzedzia.md`.

Nie zapowiadaj kroku 0. Człowiek ma zobaczyć pytania, a potem wynik.

## Krok 1 - ustal zakres tego przebiegu

Config mówi, jakich firm szukasz **ogólnie**. Ten przebieg może być węższy.

- Człowiek podał konkretną firmę ("sprawdź mi X") -> pomiń krok 2, leć od razu do kroku 3
  na tej jednej firmie.
- Człowiek podał segment ("dentyści w Poznaniu") -> użyj go zamiast domyślnego z configu.
- Człowiek nie podał nic -> weź domyślny profil z configu i **powiedz jednym zdaniem**,
  czego szukasz, zanim zaczniesz. Ktoś może chcieć to zawęzić.

Ustal liczbę firm. Domyślnie z configu. Powyżej 20 firm w jednym przebiegu ostrzeż,
że to potrwa, i zaproponuj podział na tury.

## Krok 2 - discovery

Cel: lista firm z nazwą i adresem strony.

1. Wybierz źródła z configu. Katalog źródeł i sposób ich użycia:
   `blueprints/zrodla.md`.
2. Zbierz kandydatów. Odrzuć duplikaty i firmy, które już są w sejfie
   (`grep -ril "<nazwa>" "<sejf>"`) - powiedz, które pominąłeś i dlaczego.
3. Zastosuj dyskwalifikatory z configu **od razu**, zanim zaczniesz zbierać dane.
   Nie ma sensu audytować firmy, która i tak odpadnie.

Nie znalazłeś wystarczająco dużo firm -> powiedz, ile znalazłeś i z jakiego źródła,
i zaproponuj konkretne rozszerzenie (inne miasto, sąsiednia branża, inne źródło).
Nie dobieraj przypadkowych firm, żeby dobić do liczby.

## Krok 3 - zbierz dane

Dla każdej firmy zbierz **tylko te pola, które są w configu**. Nie zbieraj wszystkiego,
co się da - to jest różnica między notatką, którą się czyta, a raportem, który leży.

Co gdzie sprawdzić i jak czytać sygnały: `blueprints/dane-i-sygnaly.md`.

Twarde zasady:

- **Każde twierdzenie ma źródło.** Przy każdej informacji zostaw link albo napisz,
  skąd pochodzi. Bez tego człowiek nie może tego użyć w mailu, bo nie wie, czy to prawda.
- **Nie znalazłeś -> napisz `nie znalazłem`.** Nigdy nie wypełniaj luki prawdopodobną
  odpowiedzią. Zmyślony numer telefonu albo zmyślone imię decydenta to realna wtopa
  przy pierwszym kontakcie.
- **Nazwiska i kontakty tylko z publicznych, firmowych źródeł** (strona firmy, wizytówka,
  oficjalny profil). Nie zbieraj prywatnych danych osób.
- Strona nie odpowiada albo jest pusta -> zanotuj to jako fakt i idź dalej.
  Martwa strona sama w sobie jest sygnałem.

## Krok 4 - kwalifikacja

Dla każdej firmy zapisz jedno zdanie: **dlaczego to jest albo nie jest Twój klient**,
oparte na tym, co faktycznie znalazłeś, a nie na wrażeniu.

Posortuj wynik: najpierw firmy z najsilniejszym sygnałem, potem reszta.
Firmy, które odpadły, zostaw na dole z krótkim powodem. To oszczędza powtórnego szukania.

## Krok 5 - zapis

Zgodnie z `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`:

1. **Notatka per firma** w folderze z configu, nazwa `<Nazwa firmy>.md`.
   Zawiera: dane kontaktowe, co znalazłeś (z linkami), sygnały, jedno zdanie kwalifikacji,
   i pustą sekcję `## Kontakt` na późniejsze notatki z rozmów.
2. **Tabela zbiorcza** `Prospekty <RRRR-MM-DD>.md`: firma, strona, sygnał, ocena, link
   do notatki wikilinkiem.
3. Notatka o firmie już istnieje -> nie nadpisuj. Pokaż różnice i zapytaj,
   czy dopisać aktualizację z datą.

Na koniec pokaż w czacie **skrót**: ile firm, ile się kwalifikuje, trzy najlepsze z jednozdaniowym
uzasadnieniem, gdzie leżą pliki. Nie wklejaj całej tabeli do odpowiedzi.

Zaproponuj następny krok: napisać do najlepszej firmy (`/bfc:cold-mail`).

## Ton i jakość

Notatka ma być czytelna dla człowieka, który za tydzień do niej wróci.
Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.
