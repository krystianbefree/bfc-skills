# Pliki w sejfie - formaty, które panel czyta i zapisuje

Markdown jest źródłem prawdy. Panel go czyta, a przy write-back punktowo aktualizuje (jedna linia, kopia przed zapisem). Te formaty są celowo proste, żeby człowiek mógł je edytować ręcznie w Obsidianie i żeby adapter parsował je bez zgadywania.

Jeśli w sejfie istnieją już odpowiedniki (folder klientów, notatki projektowe) - **używaj ich formatu**, nie narzucaj swojego. Poniższe to wzorce zakładane dopiero, gdy czegoś nie ma.

## Pozyskiwanie.md (lejek, źródło prawdy)

Jeden nagłówek `##` na etap z configu. Jedna linia na prospekt. Data ostatniego ruchu obowiązkowa.

```markdown
# Pozyskiwanie

## Prospekt
- [[Firma A]] - dodana 2026-08-10, źródło: research
- Firma B - 2026-08-12

## Kontakt
- [[Firma C]] - cold mail 2026-08-11, follow-up: 2026-08-15

## Rozmowa
- [[Firma D]] - call 2026-08-09, wartość: ~6000 zł

## Oferta
- [[Firma E]] - oferta 4000 zł, wysłana 2026-08-08
```

Adapter czyta: liczba pozycji per etap, `wartość: <kwota>` do wartości lejka, `follow-up: <data>` do sygnałów. Etap "Klient" nie mieszka tu - klient przechodzi do `Klienci/`.

## Klienci/<Nazwa>.md (jeden plik na klienta)

```markdown
---
status: aktywny            # aktywny | pauza | zakończony
stawka: 4000 zł/mc
ostatni_kontakt: 2026-08-10
---

# Kowalski sp. z o.o.

## Projekty
- Strona firmowa - etap: wdrożenie - deadline: 2026-08-20
- Kampania Meta - etap: brief - deadline: 2026-09-01

## Do zrobienia
- [ ] wysłać makietę strony (do 2026-08-14)
- [x] podpisać umowę

## Kontakt
Notatki z rozmów, ustalenia, linki.
```

Adapter czyta: frontmatter do statusu i kasy, `## Projekty` do listy deliverables (etap + deadline), `## Do zrobienia` do to-do. `(do <data>)` przy zadaniu to jego termin.

## Biznes/<Nazwa>.md (własny biznes, jeden plik na inicjatywę)

Ten sam szkielet co klient, bez pól klienckich.

```markdown
---
etap: w toku               # pomysł | w toku | wstrzymane | zrobione
deadline: 2026-08-30       # opcjonalne
---

# Nowa oferta AI

## Do zrobienia
- [ ] rozpisać pakiety
- [ ] zrobić stronę oferty
```

## Kasa.md (ledger realnej gotówki, tryb kasy „faktury")

Opcjonalny plik dla trybu `sources.kasa.zrodlo: faktury`. Jedna linia = jedna faktura/wpłata. Panel sumuje tylko pozycje ze statusem `oplacona` z okna `window_days` - to jest REALNA gotówka, w odróżnieniu od szacunku ze stawek.

```markdown
# Kasa

- 2026-08-10 | 4000 zł | Kowalski | oplacona
- 2026-08-08 | 2500 zł | Nowak | oplacona
- 2026-08-05 | 6000 zł | Delta Consulting | oczekuje
- 2026-07-01 | 3000 zł | Stary projekt | oplacona
```

Format linii: `- <data RRRR-MM-DD> | <kwota> zł | <kto/za co> | <status>`.

Adapter czyta: `oplacona` (albo „opłacona"/„zaplacona"/„paid") = wliczone do przychodu; inne statusy (np. `oczekuje`) pomijane. Pozycje starsze niż `window_days` nie liczą się do okna. Kwota bez liczby albo linia bez daty jest po cichu pomijana - plik zostaje czytelny dla człowieka. Nazwa pliku bierze się z `sources.kasa.ledger_file` (domyślnie `Kasa.md`).

## Zasięgi.md (statystyki treści, tryb `statystyki` on)

Opcjonalny plik dla publikujących (zakładka Zasięgi). Jeden `##` na post, pod nim liczby. Człowiek wpisuje ręcznie albo mówi Claude, on dopisuje.

```markdown
# Zasięgi

## Jak zdobyłem pierwszego klienta B2B w 30 dni
data: 2026-08-15
zasieg: 24800
polubienia: 1120
komentarze: 143
udostepnienia: 96
zapisy: 512
link: https://www.instagram.com/reel/XXXX/
```

Adapter czyta: `zasieg` (metryka główna), reszta metryk do zaangażowania, `data` do okna i trendu, `link` do podglądu. Synonimy pól działają (zasięg/reach/wyświetlenia, polubienia/lajki itd.). Post bez `zasieg` po prostu nie wchodzi do rankingu. Nazwa pliku z `sources.statystyki.file`.

## Outputy/ (archiwum efektów skończonych zadań)

Folder na gotowe deliverable'y, które powstały w rozmowie i mają wartość później:
cenniki, oferty, scenariusze, teksty. Zapisuje je Claude przy zamykaniu zadania
(reguły: `zadania-lifecycle.md`), a zakładka **Archiwum** je pokazuje. Podfolder =
typ, plik = jeden efekt. Read-only dla panelu - tylko Claude tu pisze, przez Write.

```
Outputy/
├── Wyceny/       cenniki, wyceny, kalkulacje stawek
├── Oferty/       oferty handlowe, propozycje współpracy
├── Treści/       skrypty rolek, posty, artykuły, newslettery
├── Scenariusze/  scenariusze automatyzacji, opisy procesów
├── Maile/        cold maile, follow-upy, sekwencje
├── Strategie/    strategie, plany, briefy
└── Inne/         reszta
```

Nazwa pliku: `RRRR-MM-DD Tytuł.md` (data dzisiejsza + krótki tytuł, z klientem gdy
dotyczy). Zawartość - frontmatter plus **sam deliverable** do wklejenia, bez
komentarzy:

```markdown
---
typ: wycena
zadanie: "rozpisać 3 pakiety cenowe"
klient: Salon Uroda        # albo projekt: <nazwa> przy własnym biznesie
data: 2026-08-18
zrodlo: Klienci/Salon Uroda.md
---

# Cennik - Salon Uroda

<sam cennik, gotowy do wysłania>
```

W pliku zadania (`zrodlo`) odhaczony punkt dostaje odnośnik do efektu:
`- [x] rozpisać 3 pakiety cenowe (output: [[Outputy/Wyceny/2026-08-18 Cennik - Salon Uroda]])`.

Adapter czyta: podfolder -> typ, nagłówek `#` -> tytuł, frontmatter -> klient/data,
pierwsza linia treści -> podgląd na karcie. Folder może nie istnieć na start (pusty
= zakładka pusta, nie błąd).

## Zasady wspólne

- Daty w formacie `RRRR-MM-DD`. To po nich liczą się sygnały terminowe.
- Kwoty jako tekst z "zł" - adapter wyciąga liczbę, resztę zostawia człowiekowi.
- Zadanie `- [ ]` otwarte, `- [x]` zamknięte. Panel odhacza punktowo, nie przepisuje listy.
- Nie zakładaj folderów na zapas. Klienci/ i Biznes/ zakładaj, gdy pojawia się pierwszy wpis.
