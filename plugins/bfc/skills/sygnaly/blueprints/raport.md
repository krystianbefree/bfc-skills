# Raport ze skanu

Wynik skanu trafia w trzy miejsca. Każde ma inną robotę.

## 1. `Obserwowane.md` (generuje skrypt)

`S render`. Widok listy w sejfie: na górze firmy do napisania teraz, potem obserwowane, nie teraz,
napisane, porzucone, kontakty. Nie edytujesz go ręcznie - następny skan go nadpisze.

## 2. Raport dnia: `<sejf>/BFC Skille/sygnaly/Raport sygnałów RRRR-MM-DD.md`

Zapisujesz tylko wtedy, gdy skan dał co najmniej jeden nowy sygnał albo przegląd zmienił statusy.
Pusty skan nie produkuje pliku.

```markdown
---
utworzone: RRRR-MM-DD
skill: bfc/sygnaly
---

# Raport sygnałów RRRR-MM-DD

Sprawdzone: <N> firm, <sondy>. Nowe sygnały: <M>. Do napisania teraz: <K>.

## Do napisania teraz

### <Nazwa firmy> ([[notatka z researchu]], jeśli jest)
- **<data> · <rodzina>:** <sygnał> - [źródło](<link>)
- **<data> · <rodzina>:** <sygnał> - [źródło](<link>)
- **Hipoteza:** zakładam, że <...> (z mapy sygnałów, jako przypuszczenie)
- **Pierwsze zdanie:** <jedno zdanie oparte na najświeższym sygnale, fakt publiczny, bez oceny>

## Sygnał w całym segmencie
- <segment>: <typ zmiany> u <N> firm (<lista>). Propozycja: jedna wiadomość do całego segmentu
  o tym, co ta zmiana zwykle oznacza, zamiast osobnych wiadomości.

## Kontakty w nowych firmach
- <imię>: <skąd> -> <dokąd> (<stanowisko>) - [profil](<link>). Pierwsza wiadomość: gratulacje i jedno
  pytanie, bez oferty.

## Nowe sygnały u pozostałych
- <Nazwa firmy>: <sygnał> (<data>) - czeka na drugi sygnał

## Przegląd
- <Nazwa firmy>: <decyzja człowieka>

## [Do ręki]
- <firma>: <czego skan nie sprawdził i dlaczego>
```

Pierwsze zdanie w raporcie jest **surowe**: fakt i obserwacja, bez głosu człowieka. Głos nakłada
`/bfc:cold-mail` z `Głos.md`.

## 3. Notatka firmy z researchu (jeśli istnieje)

Firma ma pole `notatka` w liście albo Grep po nazwie znajduje notatkę z `skill: bfc/research`.
Dopisz na końcu sekcję `## Sygnały` (albo dopisz wiersze do istniejącej), po jednej linii na sygnał:

```markdown
## Sygnały
- RRRR-MM-DD · zmiana: Nowa osoba w zarządzie (KRS) - [źródło](<link>)
```

Nie przepisuj reszty notatki. Z tej sekcji korzysta `/bfc:cold-mail`: świeży sygnał staje się
pierwszym zdaniem, a haczyk z audytu hipotezą problemu.

## 4. Lejek w panelu (jeśli człowiek ma `/bfc:panel`)

`S panel "<ścieżka do Pozyskiwanie.md>"`. Firmy z priorytetem dostają linię w pierwszym etapie lejka:
`- <firma> - sygnał <data>: <sygnał>, follow-up: <dziś>`. Przypomnienie na dziś wrzuca je do zakładki Dziś.
Firm, które człowiek przesunął dalej albo wpisał ręcznie, skrypt nie rusza. Przed zapisem robi kopię
w `sygnaly/.kopie/`.

## Sygnały branżowe

`S ocena` zwraca `sygnaly_branzowe`, gdy ten sam typ zmiany pojawia się w oknie u co najmniej 3 firm
z jednego segmentu (np. pięć gabinetów zaczęło rekrutować). To sygnał rynkowy: w raporcie proponujesz
jedną wiadomość do całego segmentu (co ta zmiana zwykle znaczy i jak pomagasz), napisaną później przez
`/bfc:cold-mail` dla każdej firmy z tym samym rdzeniem. Wymaga pola `segment` albo `branza` przy firmach.

## W czacie (krótko)

1. Jedno zdanie: tryb skanu, ile firm, ile nowych sygnałów, ile do napisania teraz.
2. Firmy do napisania teraz: po jednej linii (co się zmieniło + pierwsze zdanie).
3. Sygnały branżowe i kontakty w nowych firmach, jeśli są.
4. Ile firm z jednym sygnałem czeka na drugi.
5. `[Do ręki]` jednym zdaniem.
6. Propozycja: `/bfc:cold-mail` dla najmocniejszej. Pliki: gdzie leżą. Czy trafiło do panelu.

Nie wklejaj całego raportu do czatu.
