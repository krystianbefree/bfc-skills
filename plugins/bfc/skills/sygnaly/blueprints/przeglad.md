# Przegląd firm bez sygnałów

Uruchamiany w Kroku 2 skanu, gdy `S plan` zwraca listę `przeglad`: firmy obserwowane od co najmniej
tylu dni, ile ustawiono w `Config.md` (domyślnie 90), które przez ten czas nie dały żadnego sygnału.
Najstarsze idą pierwsze, najwyżej 10 na raz.

Po co: sygnały łapią firmy gotowe teraz, a to mała część rynku. Firma bez sygnału nie jest
skreślona. Jest po prostu w większości, do której pisze się zwykłą wiadomość o jej problemach.
Przegląd pilnuje, żeby lista nie rosła w nieskończoność i żeby każdy skan nie kosztował coraz więcej.

## Jak pytasz

`AskUserQuestion`, jedna firma na pytanie, maksymalnie 4 pytania na turę. Przed pytaniami jedno
zdanie: „Te firmy obserwujesz od 90+ dni i nie dały sygnału. Co z nimi?". W opisie każdej firmy:
od kiedy obserwowana i score z researchu, jeśli jest.

Opcje (w tej kolejności):

| Opcja | Co robisz |
|---|---|
| Napisz zwykłą wiadomość | `S status <id> porzucona --powod "bez sygnalu, zwykla wiadomosc"`. Firmę dodajesz do listy „do napisania bez sygnału" na koniec skanu i proponujesz `/bfc:cold-mail` (oprze się na haczyku z audytu, nie udaje sygnału). |
| Obserwuj dalej | `S status <id> obserwuj`. Firma wraca do przeglądu dopiero po kolejnym okresie. |
| Nie teraz (wróci za 3 miesiące) | `S status <id> nie-teraz --do <dziś + 90 dni>`. Nie jest skanowana do tej daty, potem wraca sama. |
| Odpuść | `S status <id> skreslona --powod "<krótko od człowieka, jeśli podał>"`. |

Więcej niż 4 firmy -> pierwsza tura to 4 najstarsze, potem zapytaj, czy przejść resztę teraz, czy
przy następnym skanie. „Przy następnym" jest w porządku: nic nie przepada.

## Po przeglądzie

Jedno zdanie podsumowania (ile do zwykłej wiadomości, ile dalej, ile odłożonych, ile odpuszczonych)
i dopiero potem skan. Firmy do zwykłej wiadomości wypisz jeszcze raz w Kroku 6, obok firm z
priorytetem, żeby człowiek widział całą robotę na dziś.
