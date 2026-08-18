---
name: cold-mail
description: Pisze pierwszą wiadomość do firmy i sekwencję follow-upów, opartą na tym, co research faktycznie o niej znalazł. Przy pierwszym użyciu pyta o kanał, Twoją jedną ofertę na pierwszy kontakt, ton i wezwanie do działania. Użyj gdy ktoś mówi "napisz cold maila", "pierwsza wiadomość do klienta", "napisz do tej firmy", "wiadomość na LinkedIn", "follow-up", "co napisać żeby odpisali", "outreach".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite, Skill
---

# Cold mail

Piszesz wiadomość, na którą ktoś odpisze. Nie taką, która brzmi profesjonalnie.

## Krok 0 - konfiguracja

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Brak `Profil.md` -> wywiad profilowy (`${CLAUDE_PLUGIN_ROOT}/wspolne/profil.wywiad.md`), zapisz.
3. Przeczytaj `Profil.md`.
4. Brak `<sejf>/BFC Skille/cold-mail/Config.md` albo są w nim `TODO:` -> wywiad z `wywiad.md`
   (mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`), zapisz z `config.template.md`.
   Przy istniejącym pliku pytaj **tylko** o `TODO:`.

## Krok 1 - zdobądź materiał

Cold mail bez materiału o firmie to spam. Nie da się go uratować dobrym stylem.

1. **Przeszukaj sejf**: `grep -ril "<nazwa firmy>" "<sejf>"`. Notatka z researchu jest tu złotem.
2. **Nie ma notatki** -> zapytaj, czy zrobić research teraz (`/bfc:research` na tę jedną firmę).
   To zajmie chwilę, a różnica w odpowiedziach jest ogromna.
   Człowiek nie chce czekać -> zrób minimum: wejdź na stronę firmy i znajdź **jedną**
   konkretną rzecz, o której da się napisać.
3. **Absolutnie nic nie da się znaleźć** -> powiedz wprost, że to będzie wiadomość ogólna
   i że takie mają dużo słabszą odpowiedź. Napisz ją, ale krótszą i bardziej pytającą.

Najlepszy materiał, w kolejności siły:

1. Coś, co firma sama powiedziała (ogłoszenie o pracę, wpis, opis usług ich słowami)
2. Powtarzający się zarzut w opiniach klientów
3. Widoczny, sprawdzalny problem w Twojej działce
4. Fakt o firmie bez oceny (nowa lokalizacja, nowy produkt, rekrutacja)

## Krok 2 - wybierz JEDNĄ rzecz

To jest reguła, która decyduje o wszystkim.

**W pierwszej wiadomości proponujesz jedną rzecz.** Ten problem, który wygląda na najbardziej
palący, i ta usługa, która go rozwiązuje. Nie lista tego, co umiesz.

Widzisz u nich trzy problemy -> wybierasz najgorszy, a pozostałe zostawiasz **na rozmowę**.
Możesz je najwyżej zasygnalizować jednym półzdaniem ("przy okazji rzuciło mi się w oczy
jeszcze parę rzeczy, ale to temat na rozmowę").

Powód: wiadomość z trzema propozycjami wymaga od odbiorcy decyzji, a odbiorca w trybie
przeglądania skrzynki nie podejmuje decyzji. Jedna propozycja to pytanie tak albo nie.

## Krok 3 - napisz

Struktura i wzorce otwarć: `blueprints/struktura.md`.
Czego unikać: `blueprints/czego-nie-robic.md`.
Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.

Twarde reguły:

- **Pierwsze zdanie o nich.** Wiadomość zaczynająca się od "Nazywam się" jest kasowana.
- **Zero zmyślonych faktów o firmie.** Każde twierdzenie musi pochodzić z tego, co znalazłeś.
  Pomyłka w pierwszym zdaniu kończy rozmowę, zanim się zacznie.
- **Długość z `Config.md`.** Domyślnie krótko. Nikt nie czyta cold maila dłuższego niż ekran telefonu.
- **Jedno wezwanie do działania**, wykonalne w kilka sekund.
- **Nic z czerwonych linii w `Profil.md`.**

Kanał ma znaczenie. Wiadomość na LinkedIn i mail to nie ten sam tekst przeklejony.
Różnice: `blueprints/struktura.md`.

## Krok 4 - follow-upy

Domyślnie generujesz od razu całą sekwencję, nie tylko pierwszą wiadomość.
Liczba i odstępy z `Config.md`. Zasady: `blueprints/followup.md`.

Kluczowe: **każdy follow-up wnosi coś nowego.** "Chciałem się przypomnieć" to nie follow-up,
to prośba o zignorowanie.

## Krok 5 - sprawdź przed oddaniem

1. Czy pierwsze zdanie jest o odbiorcy?
2. Czy każdy fakt o firmie da się sprawdzić w notatce z researchu?
3. Czy jest **jedna** propozycja, nie trzy?
4. Czy wezwanie do działania da się wykonać w 30 sekund?
5. Czy mieści się na ekranie telefonu?
6. Czy nie ma myślników em i fraz z listy spalonych?
7. Czy dałoby się tę wiadomość wysłać do innej firmy w tej branży bez zmian?
   **Jeśli tak, jest za ogólna. Przepisz.** To jest najważniejszy test.

## Krok 6 - zapisz i pokaż

1. Zapisz do folderu z `Config.md`, nazwa `Kontakt - <Nazwa firmy> - <RRRR-MM-DD>.md`.
   Plik zawiera pierwszą wiadomość i całą sekwencję follow-upów z terminami.
2. Jeśli w sejfie jest notatka o tej firmie, dopisz do jej sekcji `## Kontakt` jedną linijkę:
   data i że wiadomość została przygotowana. Bez kopiowania całej treści.
3. W czacie pokaż wiadomość i follow-upy w całości, gotowe do skopiowania.
4. Pod spodem, krótko: na czym ta wiadomość stoi i czego brakowało w danych.
