# Lista obserwowanych firm i kontaktów

Lista żyje w `<sejf>/BFC Skille/sygnaly/obserwowane.json` (prowadzi ją skrypt) i jest pokazywana
w `Obserwowane.md`. Zmiany zawsze przez komendy, nigdy edycją pliku.

## Dodawanie

Skąd biorą się firmy:

1. **Z researchu** - `/bfc:research` na końcu przebiegu proponuje firmy do obserwacji i pyta o zgodę.
2. **Z trybu szukaj** - firmy znalezione po sygnale (`szukaj.md`), dodawane razem z sygnałem.
3. **Ręcznie** - człowiek podaje nazwę, stronę albo link, może wskazać notatkę z researchu.

Co zbierasz o firmie (tylko to, co łatwo dostępne, bez osobnego researchu):

| Pole | Skąd | Wymagane |
|---|---|---|
| `nazwa` | od człowieka albo z notatki | tak |
| `strona` | od człowieka, z notatki, ze stopki | nie, ale bez niej nie działa sonda strony |
| `miasto`, `branza`, `segment` | notatka researchu albo strona | nie, ale segment jest potrzebny do sygnałów branżowych |
| `krs` | notatka, stopka strony („KRS"), jedno wyszukiwanie | nie, tylko spółki |
| `instagram` | stopka strony | nie |
| `google_maps` | notatka researchu | nie (opinie zadziałają też po nazwie i mieście) |
| `notatka` | nazwa pliku notatki z researchu, bez `.md` | nie |
| `score` | z notatki researchu | nie |
| `zrodlo` | `research`, `szukaj` albo `recznie` | tak |

Zapisz listę do pliku JSON i `S dodaj <plik.json>`. Skrypt pomija duplikaty (domena, KRS, NIP, nazwa)
i mówi, które firmy już są i z jakim statusem. Firma porzucona albo skreślona wcześniej -> zapytaj,
czy przywrócić (`S status <id> obserwuj`).

Po dodaniu: jedno zdanie, ile dodane, ile pominięte. Nie skanuj od razu, chyba że człowiek prosi.
Najbliższy skan pokaże sygnały z historii (KRS, archiwum strony, daty opinii), nie trzeba czekać tygodnia.

## Statusy

| Status | Znaczy | Skąd |
|---|---|---|
| `obserwuj` | skanowana wg kadencji | domyślny po dodaniu |
| `nie-teraz` | odłożona do daty, potem wraca sama | przegląd albo sygnał na „nie" |
| `napisano` | poszła wiadomość, czeka na wynik (`S wynik`) | po `/bfc:cold-mail` |
| `porzucona` | bez sygnału, poszła zwykła wiadomość | przegląd |
| `skreslona` | nie jest klientem | przegląd albo sygnał na „nie" |

## Kontakty z dawnych projektów

Ludzie, z którymi człowiek już pracował. Zmiana ich pracy to najmocniejszy sygnał: znają go, a nowa firma
nie zna jeszcze jego konkurencji. Dwie drogi, można łączyć.

### Droga 1 - eksport z LinkedIna (zalecana, darmowa, cała sieć naraz)

Instrukcja dla człowieka (podaj ją, gdy chce z tego korzystać):

1. LinkedIn w przeglądarce, kliknij swoje zdjęcie w prawym górnym rogu -> **Ustawienia i prywatność**.
2. Po lewej **Prywatność danych** -> **Pobierz kopię swoich danych**.
3. Wybierz opcję z konkretnymi plikami i zaznacz tylko **Kontakty** (w angielskiej wersji „Connections").
   Kliknij **Poproś o archiwum**. LinkedIn może poprosić o hasło.
4. Po kilku minutach (czasem do doby) przychodzi mail z linkiem. Pobierz plik ZIP, rozpakuj go i weź plik
   `Connections.csv`.
5. Wrzuć go do `<sejf>/BFC Skille/sygnaly/linkedin/` i napisz „wrzuciłem eksport z LinkedIna".
6. Powtarzaj raz w miesiącu. Każdy kolejny plik skill porówna z poprzednim.

Nazwy przycisków LinkedIn czasem zmienia. Jeśli człowiek nie widzi któregoś, niech szuka w ustawieniach
hasła „Pobierz kopię swoich danych".

Co robisz z plikiem: `S linkedin-import "<ścieżka do Connections.csv>"`. Skrypt zapisuje tylko imię, firmę,
stanowisko i link (bez e-maili). Pierwszy import to punkt odniesienia. Kontakty z listy dawnych projektów
porównuje od razu i aktualizuje im firmę, więc nie trzeba ich szukać. Wynik: lista zmian pracy,
posortowana: najpierw kontakty z projektów, potem stanowiska decyzyjne.

### Droga 2 - ręczna lista (gdy ktoś nie chce eksportu)

1. Poproś o listę: imię i nazwisko, ostatnia znana firma, link do LinkedIn, jeśli jest, i jednym słowem
   relacja (np. klient, wspólny projekt). Bez numerów telefonów i prywatnych danych.
2. `S kontakt-dodaj <plik.json>`.
3. Przy pełnym skanie (plan zwraca `kontakty_do_sprawdzenia`, domyślnie co 30 dni): jedno wyszukiwanie
   `"<imię nazwisko>" "<ostatnia firma>" linkedin`. Obecną firmę i stanowisko bierzesz z opisu wyniku.
   `S kontakt-obserwacja <id> <plik.json>` z `{"firma": "...", "stanowisko": "...", "url": "..."}`.
   Niepewne dopasowanie (inna osoba o tym samym nazwisku) -> nie przekazuj.

### Co robisz ze zmianą pracy

W raporcie osobna sekcja „Kontakty w nowych firmach": kto, skąd, dokąd, link, propozycja pierwszej wiadomości
(gratulacje i jedno pytanie o to, z czym się teraz mierzą, bez oferty). Zapytaj, czy dodać nową firmę do
obserwowanych. Przy dodaniu zapisz od razu sygnał rodziny `zmiana`, typ `kontakt_zmiana_pracy`, waga 2
(to najmocniejszy sygnał, sam w sobie daje priorytet).
