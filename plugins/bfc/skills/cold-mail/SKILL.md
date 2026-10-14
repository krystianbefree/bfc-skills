---
name: cold-mail
description: Pisze pierwszą wiadomość do firmy i sekwencję follow-upów - w Twoim głosie, oparte na tym, co research o niej znalazł (dominujący problem, gotowy haczyk, dowody). Czyta fundament z /bfc:start (Głos, Oferta, Dowody), a gdy poprawiasz maila, uczy się Twoich reguł na przyszłość. Użyj gdy ktoś mówi "napisz cold maila", "pierwsza wiadomość do klienta", "napisz do tej firmy", "wiadomość na LinkedIn", "follow-up", "co napisać żeby odpisali", "outreach".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite, Skill
---

# Cold mail

Piszesz wiadomość, na którą ktoś odpisze, i brzmiącą jak **ten człowiek**, nie jak AI. Nie taką, która brzmi profesjonalnie. Materiał o firmie bierzesz z researchu, głos z fundamentu, a z każdej poprawki uczysz się reguły na przyszłość.

## Krok 0 - fundament i ustawienia

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Sprawdź i przeczytaj fundament z `<sejf>/BFC Skille/`: `Głos.md`, `Oferta.md`, `Dowody.md` (to z nich bierzesz styl, usługę z ceną i czym się podeprzeć). **Brak `Głos.md` albo `Oferta.md` -> „Najpierw odpal `/bfc:start`, żeby zbudować fundament (Twój głos, oferta, dowody). Bez tego mail brzmi jak każdy inny cold mail w skrzynce."** Nie rób tu własnego wywiadu o usługach ani stylu - fundament jest źródłem prawdy. `Dowody.md` brak -> pisz dalej, tylko bez podpierania się realizacją (powiedz to jednym zdaniem).
3. Przeczytaj `Profil.md` (ton, czerwone linie), jeśli istnieje.
4. Brak `<sejf>/BFC Skille/cold-mail/Config.md` albo są w nim `TODO:` -> wywiad z `wywiad.md` (mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`), zapisz z `config.template.md`. Przy istniejącym pliku pytaj **tylko** o `TODO:`.

## Krok 1 - materiał o firmie

Cold mail bez materiału o firmie to spam. Nie da się go uratować dobrym stylem ani głosem.

Najlepszym materiałem jest **notatka z researchu** - ma już policzony dominujący problem i gotowy haczyk.

1. **Znajdź notatkę researchu.** Użyj narzędzia **Grep** (`-i -l` po nazwie firmy w `<sejf>`), nie shellowego `grep` (nie ma go na Windows). Trafienie z `skill: bfc/research` we frontmatterze -> to jest złoto, czytaj je w całości. Upewnij się, że notatka jest **o tej firmie** (nazwa pliku/nagłówek), a nie tylko ją wspomina; tabela zbiorcza `Prospekty ...` to lista wielu firm, nie notatka jednej.
2. **Nie ma notatki** -> zapytaj, czy zrobić research teraz (`/bfc:research` na tę jedną firmę). To zajmie chwilę, a różnica w odpowiedziach jest ogromna. Człowiek nie chce czekać -> zrób minimum: wejdź na stronę firmy i znajdź **jedną** konkretną, sprawdzalną rzecz, o której da się napisać.
3. **Absolutnie nic nie da się znaleźć** -> powiedz wprost, że to będzie wiadomość ogólna i takie mają dużo słabszą odpowiedź. Napisz ją, ale krótszą i bardziej pytającą.

Co bierzesz z notatki researchu (rozpoznasz ją po nagłówkach):

- **`Haczyk na pierwsze zdanie maila`** - to jest surowy fakt + obserwacja, bez głosu. Twoja robota: przełożyć go na głos człowieka (Krok 3).
- **`Dominujący problem -> Twoja usługa`** - to jest ta jedna rzecz z Kroku 2.
- **`Dowody-sygnały`** (każdy z linkiem) - fakty, które możesz zacytować. Każdy jest sprawdzalny; niczego nie dokładaj od siebie.
- **`[Do ręki]`** - czego automat nie sprawdził. Nie zgaduj tego w mailu; jak potrzebujesz, sprawdź ręcznie albo zostaw.
- **`Problemy poboczne`** - NIE do pierwszej wiadomości. Najwyżej pół zdania „na rozmowę".
- **`## Sygnały`** (dopisuje `/bfc:sygnaly`) - jeśli jest wpis z ostatnich 90 dni, **pierwsze zdanie opierasz na najświeższym sygnale** (fakt publiczny i zawodowy, z linkiem), a haczyk z audytu idzie jako hipoteza problemu („zakładam, że…"). Nie piszesz o tym, co firmie się przytrafiło, ani o niczym prywatnym. Zasady: `${CLAUDE_PLUGIN_ROOT}/skills/sygnaly/blueprints/interpretacja.md`, sekcja o wiadomości. Firma trafiła do Ciebie z przeglądu bez sygnału -> zwykły haczyk z audytu, bez udawania, że coś się u nich zmieniło.

## Krok 2 - wybierz JEDNĄ rzecz

W pierwszej wiadomości proponujesz jedną rzecz: dominujący problem z notatki i usługa z `Oferta.md`, która go rozwiązuje. Nie listę tego, co umiesz.

Widzisz u nich trzy problemy -> bierzesz ten z najwyższym severity (notatka już go wskazała jako dominujący), resztę zostawiasz **na rozmowę**. Możesz je najwyżej zasygnalizować jednym półzdaniem.

Powód: wiadomość z trzema propozycjami wymaga od odbiorcy decyzji, a odbiorca w trybie przeglądania skrzynki decyzji nie podejmuje. Jedna propozycja to pytanie tak albo nie.

## Krok 3 - napisz w Twoim głosie

To jest sedno FAZA 2. Mail ma brzmieć jak ten człowiek.

1. **Przeczytaj `Głos.md`** - wzorzec stylu (forma Ty/Pan, rytm, jak otwiera, zwroty których używa, czego NIE robi) **oraz sekcję `## Reguły z pętli uczenia`** (to, czego nauczył Cię przy poprzednich mailach). Jak stosować głos w mailu i jak przełożyć surowy haczyk na jego kadencję: `blueprints/glos-w-mailu.md`.
2. **Struktura i wzorce otwarć:** `blueprints/struktura.md`. Czego unikać: `blueprints/czego-nie-robic.md`.
3. **Podłoga anty-AI** (dla wszystkich, pod głosem): `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.

Twarde reguły:

- **Pierwsze zdanie o nich** - przełożony na głos człowieka haczyk z notatki. Wiadomość zaczynająca się od „Nazywam się" jest kasowana.
- **Zero zmyślonych faktów o firmie.** Każde twierdzenie pochodzi z `Dowody-sygnały` notatki. Pomyłka w pierwszym zdaniu kończy rozmowę, zanim się zacznie.
- **Dowód tylko z `Dowody.md`** i tylko jeśli pasuje - w połowie zdania, nie w osobnym akapicie. Brak dowodu -> stoisz na procesie i pytaniu, nie zmyślasz liczby.
- **Długość z `Config.md`.** Domyślnie krótko. Nikt nie czyta cold maila dłuższego niż ekran telefonu.
- **Jedno wezwanie do działania**, wykonalne w kilka sekund.
- **Nic z czerwonych linii w `Profil.md`.**

Kanał ma znaczenie. Wiadomość na LinkedIn i mail to nie ten sam tekst przeklejony. Różnice: `blueprints/struktura.md`.

## Krok 4 - follow-upy

Domyślnie generujesz od razu całą sekwencję, nie tylko pierwszą wiadomość. Liczba i odstępy z `Config.md`. Zasady i format z datami: `blueprints/followup.md`. Follow-upy piszesz tym samym głosem co pierwszą wiadomość.

Kluczowe: **każdy follow-up wnosi coś nowego.** „Chciałem się przypomnieć" to nie follow-up, to prośba o zignorowanie.

## Krok 5 - sprawdź przed oddaniem

1. Czy pierwsze zdanie jest o odbiorcy?
2. Czy każdy fakt o firmie da się sprawdzić - w `Dowody-sygnały` notatki, a jak notatki nie było (Krok 1 pkt 2/3), w tym, co sam znalazłeś na stronie?
3. Czy jest **jedna** propozycja, nie trzy?
4. Czy wezwanie do działania da się wykonać w 30 sekund?
5. Czy mieści się na ekranie telefonu?
6. Czy nie ma myślników em i fraz z listy spalonych (floor anty-AI z Kroku 3)?
7. **Czy brzmi jak on?** Zestaw z `Głos.md`: forma, rytm, otwarcie, zwroty. Jak da się podmienić na dowolnego innego freelancera bez zmiany słowa - głos nie wszedł, przepisz.
8. Czy dałoby się tę wiadomość wysłać do innej firmy w tej branży bez zmian? **Jeśli tak, jest za ogólna. Przepisz.** To najważniejszy test.

## Krok 6 - zapisz i pokaż

1. Zapisz do folderu z `Config.md`, nazwa `Kontakt - <Nazwa firmy> - <RRRR-MM-DD>.md`. Plik zawiera pierwszą wiadomość i całą sekwencję follow-upów z terminami.
2. Jeśli w sejfie jest notatka researchu o tej firmie, dopisz do jej sekcji `## Kontakt` jedną linijkę: data i że wiadomość została przygotowana. Bez kopiowania całej treści.
   Firma jest na liście obserwowanych sygnałów -> po potwierdzeniu, że wiadomość poszła, ustaw jej status: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/sygnaly/solutions/sygnaly.py" status "<sejf>/BFC Skille/sygnaly" <id> napisano` (id z komendy `lista`). Skan przestanie ją sprawdzać, a skrypt zapamięta, na jakich sygnałach stała wiadomość.
   Gdy człowiek później powie, że odpisali, umówił spotkanie, podpisał zlecenie albo że była cisza -> ta sama ścieżka, komenda `wynik ... <id> odpisali|spotkanie|klient|cisza`. Z tego `/bfc:sygnaly` uczy się, które sygnały dają mu odpowiedzi.
3. W czacie pokaż wiadomość i follow-upy w całości, gotowe do skopiowania.
4. Pod spodem krótko: na czym ta wiadomość stoi i czego brakowało w danych.

## Krok 7 - pętla uczenia (tu profil głosu rośnie)

Człowiek prawie nigdy nie bierze pierwszej wersji bez zmian. Każda jego poprawka to darmowa lekcja jego stylu - jeśli ją zapamiętasz, następny mail piszesz bliżej niego. Ale zapamiętujesz **tylko to, co jest regułą**, nie każdy jednorazowy kaprys.

Pełna mechanika (co jest regułą, co nie, jak destylować, gdzie dopisać): `blueprints/glos-w-mailu.md`. W skrócie:

1. Poprawił maila (styl, forma, otwarcie, słowo, długość) -> **nanieś poprawkę od razu** na tę wiadomość.
2. Zapytaj **raz** (nie po każdej zmianie z osobna): „To jednorazowo, czy reguła na przyszłość?" (`AskUserQuestion`: „Reguła - stosuj zawsze" / „Tylko ten raz"). Kilka poprawek naraz -> pokaż je jako krótką listę destylowanych reguł i zapytaj zbiorczo, które zapisać.
3. „Reguła" -> zdestyluj poprawkę w jedno konkretne zdanie-regułę i **dopisz** do sekcji zaczynającej się od `## Reguły z pętli uczenia` w `Głos.md` (czytaj plik, dopisz na końcu sekcji - nie przepisuj całości). Reguła sprzeczna z już zapisaną -> podmień starą, nie dokładaj drugiej (`blueprints/glos-w-mailu.md`). Potwierdź jedną linią, co doszło.
4. Poprawka o **fakcie o firmie** (a nie o stylu) -> to nie jest reguła głosu. Popraw notatkę/dane, nie zaśmiecaj `Głos.md`.

To jest różnica między skillem a ChatGPT: on zapomina po zamknięciu okna, ten pamięta i pisze coraz bardziej jak Ty.
