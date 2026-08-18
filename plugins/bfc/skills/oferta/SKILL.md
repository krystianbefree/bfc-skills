---
name: oferta
description: Pisze ofertę dla konkretnego klienta - z Twoim pricingiem, Twoimi realizacjami i Twoim tonem, zaciągając kontekst o kliencie z sejfu Obsidian. Przy pierwszym użyciu pyta o Twoje usługi, ceny, format oferty i warunki współpracy. Użyj gdy ktoś mówi "napisz ofertę", "zrób proposal", "wycena dla klienta", "przygotuj propozycję współpracy", "ile mam zaproponować", "oferta dla firmy X".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite, Skill
---

# Oferta

Piszesz ofertę, którą można wysłać bez poprawek. Dokument ma sprzedawać, a nie opisywać.

## Krok 0 - konfiguracja

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Brak `Profil.md` -> wywiad profilowy (`${CLAUDE_PLUGIN_ROOT}/wspolne/profil.wywiad.md`), zapisz.
3. Przeczytaj `Profil.md`.
4. Brak `<sejf>/BFC Skille/oferta/Config.md` albo są w nim `TODO:` -> wywiad z `wywiad.md`
   (mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`), zapisz z `config.template.md`.
   Przy istniejącym pliku pytaj **tylko** o `TODO:`.

## Krok 1 - zbierz kontekst o kliencie

Oferta bez wiedzy o kliencie to cennik. Zanim cokolwiek napiszesz:

1. **Przeszukaj sejf.** `grep -ril "<nazwa firmy>" "<sejf>"`. Szukasz notatki z researchu,
   notatki po rozmowie, starej korespondencji. Znalezione przeczytaj.
2. **Zapytaj o to, czego nie ma w sejfie**, w jednym pytaniu, nie w serii:
   - co klient powiedział, że go boli (własnymi słowami, jeśli to możliwe)
   - czy padła jakaś kwota albo widełki
   - na kiedy tego potrzebuje
   - z kim jeszcze rozmawia, jeśli wiadomo
3. **Nie znalazłeś nic i człowiek nic nie wie** -> powiedz wprost, że oferta będzie ogólna,
   i zaproponuj: albo najpierw `/bfc:research` na tę firmę, albo piszemy krócej i bardziej
   pytająco, żeby wywołać rozmowę.

Zasada: **cytat z rozmowy z klientem jest wart więcej niż cały research.**
Jeśli klient powiedział "gubimy zapytania z Facebooka", to jest pierwsze zdanie oferty.

## Krok 2 - wybierz, co proponujesz

Z usług w configu wybierz **to, co odpowiada na problem klienta**. Nie wszystkie.

- Jedna usługa pasuje wprost -> proponujesz ją.
- Kilka pasuje -> zbuduj pakiet, ale w ofercie ma być **jedna rekomendacja**,
  a reszta najwyżej jako opcja. Oferta z czterema równorzędnymi wariantami przenosi
  decyzję na klienta, a klient jej nie podejmie.
- Nic nie pasuje -> powiedz to człowiekowi, zamiast naciągać ofertę.

Zasady doboru wariantów i cen: `blueprints/pricing.md`.

## Krok 3 - napisz

Struktura, kolejność sekcji i co w nich musi być: `blueprints/struktura.md`.
Format wyjścia i sposób zapisu: `blueprints/format.md`.

Twarde reguły:

- **Zero zmyślonych liczb.** Nie masz wyniku z realizacji -> nie wpisujesz procentu.
  Wstaw `TODO: wstaw wynik z realizacji X` i wypunktuj to na końcu.
- **Dowody tylko te, które człowiek faktycznie ma** (`dowody` w `Profil.md`).
  Brak dowodów nie jest katastrofą - wtedy oferta stoi na konkretnym procesie i gwarancji,
  co jest uczciwsze niż podpięcie się pod cudze wyniki.
- **Nie obiecuj niczego z sekcji czerwonych linii w `Profil.md`.** To jest bezpiecznik,
  nie sugestia.
- **Cena zawsze widoczna w dokumencie.** Oferta bez ceny wraca z pytaniem o cenę
  i traci tydzień. Jeśli cena naprawdę zależy od zakresu, podaj widełki i napisz, co je przesuwa.
- Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.

## Krok 4 - sprawdź przed oddaniem

Przejdź gotowy tekst i zweryfikuj:

1. Czy pierwsze zdanie mówi o kliencie, a nie o autorze oferty?
2. Czy jest w dokumencie cena i termin?
3. Czy każda liczba da się obronić danymi z `Profil.md` albo z rozmowy?
4. Czy jest jedno, jasne wezwanie do działania i czy da się je wykonać w 30 sekund?
5. Czy nie ma myślników em i fraz z listy spalonych?
6. Czy da się wyciąć 20% i nic nie stracić? Jeśli tak, wytnij.

## Krok 5 - zapisz i pokaż

1. Zapisz do folderu z configu, nazwa `Oferta - <Nazwa klienta> - <RRRR-MM-DD>.md`.
   Zasady zapisu: `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`.
2. W czacie pokaż **całą ofertę** (to jest tekst do wysłania, człowiek musi go zobaczyć).
3. Pod nią, osobno, wypisz:
   - pola `TODO:`, które trzeba uzupełnić przed wysłaniem
   - jedno zdanie o tym, na czym ta oferta stoi (jaki argument jest najmocniejszy)
4. Zaproponuj następny krok: mail przewodni do tej oferty (`/bfc:cold-mail`).
