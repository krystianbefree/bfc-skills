# Uczenie - które sygnały dają odpowiedzi temu człowiekowi

Ten sam sygnał działa różnie u różnych ludzi. Dla jednego zmiana w zarządzie otwiera rozmowy, dla innego
nie daje nic. Skill to liczy i sam przestawia wagi. Tego nie zrobi czat, który zapomina po zamknięciu okna.

## Jak zbierają się dane

1. Wiadomość poszła -> `S status <id> napisano`. Skrypt zapisuje, jakie sygnały firma miała w chwili
   wysyłki (albo że nie miała żadnych, gdy to zwykła wiadomość po przeglądzie).
2. Człowiek mówi, co się stało -> `S wynik <id> <wynik>`:
   - `odpisali` - jakakolwiek odpowiedź, która nie jest odmową z grzeczności,
   - `spotkanie` - umówiona rozmowa,
   - `klient` - podpisane zlecenie,
   - `cisza` - brak odpowiedzi po całej sekwencji przypomnień.

Kiedy pytać o wynik: gdy człowiek wraca po skan, a są firmy w statusie `napisano` sprzed 14+ dni bez wyniku
(`S skutecznosc` zwraca ich liczbę), zapytaj **raz**, zbiorczo, o maksymalnie 4 firmy (`AskUserQuestion`).
Nie wie -> zostaw, nie zgaduj.

## Jak skrypt z tego korzysta

- **Mnożniki wag:** rodzina sygnałów, po której człowiek dostaje więcej odpowiedzi niż średnio, liczy się
  mocniej (do 2 razy), a ta, która nie działa, słabiej (do 0,5). Działa od 5 wysłanych wiadomości z wynikiem
  w danej rodzinie. Wcześniej wszystkie mnożniki są 1.
- **Sygnał a zwykła wiadomość:** procent odpowiedzi po wiadomościach z sygnałem i bez. To najprostszy dowód,
  czy prospecting na sygnałach działa u tego człowieka. Widać go w `Obserwowane.md`, sekcja „Co działa u Ciebie".
- **Sondy bez efektu:** sonda, która przez 90 dni i co najmniej 10 uruchomień nie dała żadnego zapisanego
  sygnału, trafia do propozycji wyłączenia. Każdy skan robi się tańszy.

## Tryb „co działa" (na prośbę)

`S skutecznosc` i pokaż krótko:

1. Odpowiedzi z sygnałem kontra bez sygnału (procent i liczby).
2. Trzy rodziny albo typy sygnałów, które działają najlepiej, i jedna, która nie działa.
3. Obecne mnożniki wag.
4. Jedno zdanie wniosku, np. „u Ciebie najlepiej działają ogłoszenia, które wracają - przy nich warto pisać
   od razu" albo „za mało danych, wróćmy po kolejnych 10 wiadomościach".

Mało danych (poniżej 10 wiadomości z wynikiem) -> powiedz to wprost i nie wyciągaj wniosków.
