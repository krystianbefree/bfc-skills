# Format oferty

Zależny od pola `format_pliku` w `Config.md`. Treść jest ta sama, zmienia się opakowanie.

## Szkielet dokumentu

```markdown
---
utworzone: RRRR-MM-DD
skill: bfc/oferta
klient: <Nazwa firmy>
---

# Propozycja współpracy - <Nazwa firmy>

## W skrócie

- **Wyzwanie:** <jedno zdanie>
- **Rozwiązanie:** <jedno zdanie>
- **Efekt:** <co się zmienia>
- **Inwestycja:** <kwota, netto czy brutto>
- **Czas:** <ile potrwa>
- **Następny krok:** <jedna czynność>

## <Haczyk jako nagłówek albo pierwsze zdanie akapitu>

<Diagnoza: fakt plus co oznacza dla ich biznesu. Dwa, trzy zdania.>

<Wizja: jak wygląda ich sytuacja po robocie. Trzeci poziom "i co z tego".>

## Jak to zrobimy

### Faza 1: <nazwa>
<Cel fazy.>
- <działanie>
- <działanie>
- <działanie>

**Dostajesz:** <materialny rezultat>
**Czas:** <ile>

### Faza 2: <nazwa>
...

## Zakres i cena

<Jeden pakiet albo trzy, ze wskazaniem rekomendowanego. Zasady: blueprints/pricing.md>

## Warunki

<Tylko te zaznaczone w Config.md: termin, płatność, poprawki, co po stronie klienta.>

## Co dalej

<Jedno pytanie zamknięte i jedna czynność.>
```

## Wersja do maila

Gdy `format_pliku` to "Notatka plus wersja do wklejenia w maila", dopisz pod ofertą,
w osobnym bloku, mail przewodni:

- maksymalnie osiem zdań
- pierwsze zdanie to haczyk, ten sam co w ofercie
- **jedna** rzecz z diagnozy, nie wszystkie
- kwota albo widełki, żeby nie było zaskoczenia po otwarciu załącznika
- jedno pytanie zamknięte na końcu

Mail nie streszcza oferty. Mail ma sprawić, że ktoś ją otworzy.

## Wersja do wydruku albo PDF

Gdy `format_pliku` to dokument do wydruku:

- podziel treść znacznikami `---` na strony, tak żeby każda faza mieściła się w całości
- streszczenie zawsze na pierwszej stronie, samo
- cena nie może przypadać na złamaniu strony
- na końcu dane kontaktowe z `Profil.md`
- powiedz człowiekowi, że eksport do PDF robi w Obsidianie przez `Eksportuj do PDF`,
  i że warto wcześniej zerknąć na podgląd

## Nazewnictwo i zapis

Plik: `Oferta - <Nazwa klienta> - <RRRR-MM-DD>.md` w folderze z `Config.md`.

Oferta dla tego klienta już istnieje -> nie nadpisuj. Pokaż poprzednią wersję,
zapytaj, czy to poprawka (wtedy nowa data w nazwie) czy zupełnie inna propozycja.

Zalinkuj wikilinkiem do notatki o kliencie, jeśli taka jest w sejfie.
Nie twórz linków do notatek, których nie ma.

## Co pokazać w czacie

Całą ofertę. To jest tekst do wysłania, człowiek musi go przeczytać, zanim wyśle.

Pod nią, osobno i krótko:

- pola `TODO:` do uzupełnienia przed wysłaniem
- jedno zdanie: który argument w tej ofercie jest najmocniejszy
- czego zabrakło w danych, przez co oferta jest słabsza niż mogłaby być
