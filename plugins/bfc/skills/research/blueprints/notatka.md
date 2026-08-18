# Notatka per firma + tabela zbiorcza

Wynik researchu to notatki, z których cold-mail bierze pierwsze zdanie, a panel - lejek.
Notatka bez linku przy sygnale jest bezwartościowa: to nazwisko człowieka idzie pod mailem,
więc musi móc sprawdzić każdy fakt, zanim wyśle.

## Notatka firmy: `<folder_wynikow>/<Nazwa firmy>.md`

```markdown
---
utworzone: RRRR-MM-DD
skill: bfc/research
score: 84
segment: lokalna
etap: prospekt
---

# <Nazwa firmy>

**Score: 84/100** · dopasowanie ICP: <wysokie/średnie/niskie> · dominujący problem: <klasa>

- **Strona:** <url>
- **Branża / miasto / wielkość:** <...> (na jakiej podstawie)
- **Kontakt:** <mail/tel albo „nie znalazłem">
- **Decyduje:** <imię + rola albo „nie znalazłem">

## Dominujący problem -> Twoja usługa

**<klasa>** (severity <N>/10) -> **<usługa z Oferta.md>** (<cena/widełki z Oferta.md>).
Dlaczego dominuje: najwyższy severity razem z priorytetem Twojej oferty.

## Dowody-sygnały (każdy z linkiem)

- **<sygnał>:** <konkretna liczba/fakt> - źródło: <link albo narzędzie>
- **Budżet:** <Meta Ads aktywne / rekrutacja albo „brak sygnałów">
- **Ból (opinie):** <powtarzalny zarzut albo „-"> (nigdy cytatu do maila)

## Haczyk na pierwsze zdanie maila

> <jedno zdanie oparte na dominującym sygnale + konkretna liczba/fakt>

## [Do ręki] - czego automat nie sprawdził

- <punkt z Metoda prospectingu.md oznaczony [do ręki]>
- <sonda pominięta z braku narzędzia - do sprawdzenia ręcznego>

## Problemy poboczne (na rozmowę, nie do maila)

- <secondary 1>, <secondary 2>

## Ocena

<jedno zdanie: czemu to jest albo nie jest Twój klient - z faktów, nie wrażenia>

## Kontakt

<pusto - historia rozmów; tu dopisujesz Ty albo cold-mail, kiedy pisałeś i co odpowiedzieli>
```

## Jak wypełniasz z wyniku `score.py`

- **`score`** i **`dominujący problem`** wprost z JSON-a. `dopasowanie ICP`: `icp_fit >= 0.8` -> wysokie,
  `>= 0.5` -> średnie, niżej -> niskie.
- **`Dominujący problem -> usługa`**: `dominant.klasa`, `dominant.usluga`, `dominant.cena`, `dominant.severity`.
- **Haczyk**: zbuduj JEDNO zdanie z `hook_material` (sygnał + wartość + gdzie), z konkretną liczbą, w tonie
  obserwacji o nich, NIE ataku. Przykład z `hook_material {sygnal: lighthouse.performance, wartosc: 34}`:
  „Wasza strona ładuje się na telefonie w kilka sekund (Lighthouse: 34/100 wydajności) - przy płatnym ruchu
  to zwykle znaczy, że część kliknięć nie dochodzi do formularza." Obowiązuje `wspolne/jakosc-pl.md`
  (zero em-dashy, zero fraz spalonych, pierwsze zdanie o nich). Głosu klubowicza tu jeszcze nie ma -
  dołoży go cold-mail (FAZA 2) z `Głos.md`; tu ma być tylko konkret i fakt.
- **`hook_material: null`** (score bez konkretnej liczby) -> haczyk oprzyj na dominującym problemie
  opisowo, bez zmyślania liczby.
- **`[Do ręki]`**: przepisz punkty `[do ręki]` z `Metoda prospectingu.md` + pola, które w audycie wpadły
  jako `[do ręki]` z braku narzędzia. To jest checklist dla człowieka, nie porażka.
- **`gate: 0`** (firma odpadła) -> NIE zakładaj pełnej notatki. Dopisz firmę do tabeli zbiorczej z powodem
  odpadnięcia (`powod` z JSON-a), żeby nie szukać jej drugi raz.

## Tabela zbiorcza: `Prospekty <RRRR-MM-DD>.md`

Sortuj malejąco po score. Odpadłe na dole.

```markdown
# Prospekty <RRRR-MM-DD>

| Score | Firma | Dominujący problem | Twoja usługa | Notatka |
|---|---|---|---|---|
| 96 | [[Gabinet Uśmiech]] | wolna strona mobilna | optymalizacja + landing | ✅ |
| 71 | [[Klinika Dent]] | martwy Instagram | prowadzenie IG | ✅ |
| 0 | Sieciówka XYZ | - | - | odpada: zły segment |
```

## Na koniec (w czacie, nie do pliku)

Skrót: ile firm sprawdzone, ile się kwalifikuje (score > próg, np. 60), **top 3 z jednozdaniowym
uzasadnieniem i score**, gdzie leżą pliki. Nie wklejaj całej tabeli. Propozycja: napisać do najlepszej
(`/bfc:cold-mail` - weźmie haczyk i dominujący problem z tej notatki).
