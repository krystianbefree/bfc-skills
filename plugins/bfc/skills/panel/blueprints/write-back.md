# Write-back - jak Claude aktualizuje panel z rozmowy

To jest różnica między panelem-obrazkiem a panelem, który żyje. Człowiek i tak rozmawia z Claude. Kiedy w rozmowie padnie fakt zmieniający stan biznesu, dopisz go do właściwego pliku MD. Panel odświeży się sam.

## Zasada zaufania

- **Jedna zmieniona linia na jeden fakt.** Nie przepisujesz całego pliku.
- **Kopia przed zapisem.** Zanim edytujesz plik w sejfie, zrób jego kopię (adapter/silnik robi to automatycznie, ale przy ręcznej edycji przez Claude - też).
- **Nie wymyślaj danych.** Brak kwoty to "brak danych", nie zero. Jak człowiek nie podał liczby, nie wpisuj szacunku jako faktu.
- **Potwierdź niejednoznaczne.** "Zamknąłem projekt" przy dwóch projektach tego klienta -> dopytaj który, nie zgaduj.
- Nie rób write-backu z rzeczy powiedzianych hipotetycznie ("chyba wyślę ofertę"). Tylko fakty dokonane.

## Mapowanie zdań na pliki

| Człowiek mówi | Plik | Zmiana |
|---|---|---|
| "znalazłem/dodałem firmę X" | `Pozyskiwanie.md` | nowa linia w etapie Prospekt, z datą |
| "napisałem/zadzwoniłem do X" | `Pozyskiwanie.md` | przesuń X do Kontakt/Rozmowa, ustaw `follow-up:` |
| "wysłałem ofertę X za 4k" | `Pozyskiwanie.md` | przesuń X do Oferta, dopisz `wartość: 4000 zł` |
| "X podpisał / został klientem" | `Pozyskiwanie.md` + `Klienci/X.md` | usuń z lejka, załóż plik klienta ze stawką |
| "X zapłacił / faktura X" | `Klienci/X.md` | zaktualizuj kasę/status, zdejmij sygnał faktury |
| "gadałem z klientem X, ustaliliśmy Y" | `Klienci/X.md` | `ostatni_kontakt:` = dziś, dopisz w `## Kontakt` |
| "skończyłem projekt Y dla X" | `Klienci/X.md` | etap projektu -> zrobione albo usuń z `## Projekty` |
| "muszę zrobić Z dla X" | `Klienci/X.md` | nowe `- [ ] Z` w `## Do zrobienia` |
| "zrobiłem Z" | odpowiedni plik | odhacz `- [x] Z` |
| "nowy pomysł/projekt na własny biznes" | `Biznes/<nazwa>.md` | załóż plik z etapem pomysł |
| "pracuję nad własną ofertą/stroną" | `Biznes/...` | dopisz to-do albo zaktualizuj etap |

## Dwa tryby: pasywny i na żądanie

**Pasywny (domyślny).** Kiedy w zwykłej rozmowie padnie fakt zmieniający stan biznesu, nie milcz. **Zaproponuj zapis**: "Zapisać to do panelu? Przesunę Kowalskiego do Oferty, wartość 4000 zł." Człowiek potwierdza, wtedy zapisujesz. Fakt jednoznaczny i dokonany możesz zapisać od razu i zaraportować - ale nigdy nie pomijaj go po cichu.

**Na żądanie ("/bfc:panel zapisz", "zapisz to do panelu").** Świadomie przejrzyj **bieżącą rozmowę** pod kątem faktów biznesowych i zastosuj write-back do wszystkich, które znajdziesz. Czego szukasz:

- wysłana oferta (i kwota, jeśli padła) -> lejek, etap Oferta,
- rozmowa/kontakt z prospektem albo klientem -> przesunięcie etapu lub `ostatni_kontakt:`,
- płatność/faktura -> plik klienta,
- nowy lead (znaleziona firma) -> lejek, etap Prospekt,
- zrobione zadanie -> odhaczenie `- [x]`.

Zbierz je, zapisz wg tabeli wyżej, potwierdź niejednoznaczne przed zapisem, na końcu raportuj **jedną linią na zmianę**. Nic więcej z rozmowy nie ruszasz.

## Po zapisie

Powiedz krótko, co dopisałeś i gdzie ("Przesunąłem Kowalskiego do Oferty, wartość 4000 zł, w `Pozyskiwanie.md`"). Człowiek ma widzieć, że panel się zmienił, i móc to cofnąć, jeśli źle zrozumiałeś. Nie rób z tego raportu - jedno zdanie na zmianę.
