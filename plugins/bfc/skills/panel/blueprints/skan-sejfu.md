# Skan sejfu - jak złożyć panel z tego, co człowiek już ma

Cel: zanim zadasz jedno pytanie, poznać biznes człowieka na tyle, żeby przynieść mu **gotową propozycję panelu**, a nie pustą ankietę. Panel ma się złożyć z jego bazy wiedzy.

## Zasada prywatności (nienegocjowalna)

Nie indeksujesz całego sejfu i nie czytasz wszystkiego "na wszelki wypadek". **Pomijasz foldery, które wyglądają na prywatne**: dziennik, finanse osobiste, zdrowie, prywatne, journal, osobiste. Jeśli nie masz pewności, czy folder jest biznesowy - nie wchodzisz do środka, tylko odnotowujesz jego istnienie i ewentualnie pytasz.

## Krok 1 - mapa struktury (tanio, bez czytania treści)

```
find "<sejf>" -maxdepth 3 -type d 2>/dev/null      # foldery
find "<sejf>" -maxdepth 2 -iname "*.md" 2>/dev/null # pliki na wierzchu
```

Szukasz nazw, które coś zdradzają: `Klienci`, `Prospekty`, `CRM`, `Sprzedaż`, `Projekty`, `Oferty`, `Faktury`, `Rolki`, `Treści`, `Content`, `Biznes`, `Marketing`.

## Krok 2 - czytaj tylko notatki, które coś wnoszą

Nie więcej niż kilkanaście plików. Priorytet:

- `BFC Skille/Profil.md` (masz go już z Kroku 0)
- Wyniki `research` i `cold-mail` (`BFC Skille/research/`, pliki `Prospekty *.md`, cold-maile)
- 3-5 plików z folderu, który wygląda na klientów - żeby poznać, jak człowiek opisuje klienta (pola, stawki, statusy)
- 1-2 pliki z folderu projektów albo własnego biznesu
- `grep -rl` po słowach `stawka`, `deadline`, `oferta`, `faktura`, żeby zobaczyć, gdzie żyją takie dane

## Krok 3 - wywnioskuj propozycję

Zbierz odpowiedzi na pytania z `wywiad.md` **z tego, co widzisz**, zamiast pytać:

| Sygnał w sejfie | Wniosek do configu |
|---|---|
| Folder z plikami firm, stawki, statusy | ma klientów -> zasil zakładkę Klienci, `folder_klienci` = ten folder |
| Notatki o własnej ofercie, stronie, systemach | zasil Biznes, `folder_biznes` = ten folder |
| Folder Rolki/Treści/Content z notatkami | `publikuje_tresci` = regularnie |
| Sekcje w notatkach o prospektach (np. "wysłany", "czeka") | z nich zbuduj `etapy_lejka` |
| Klucz Stripe w `.env`, pliki faktur | zaproponuj `zrodlo_kasy` |
| Wyniki research/cold-mail obecne | `wpina_research` = Tak |

## Krok 4 - pokaż szkic, nie ankietę

Zamiast lecieć pytaniami, pokaż, co ustaliłeś, jednym akapitem:

> "Przejrzałem Twój sejf. Widzę 8 klientów w folderze `Klienci/`, prowadzisz lejek w `Prospekty 2026-08.md`, publikujesz rolki (folder `Treści/`). Złożę panel tak: zakładki Dziś, Pozyskiwanie (z Twojego lejka), Klienci (te 8 firm z ich projektami), Biznes, Kasa (na razie ręcznie - nie widzę klucza do fakturowania), Treści. Zgadza się? Dopytam tylko o dwie rzeczy, których nie znalazłem."

## Krok 5 - dopytaj TYLKO o luki

Wejdź w `wywiad.md`, ale odpuść każde pole, które skan rozstrzygnął. Realnie zostają zwykle 1-3 pytania: nazwy etapów jeśli niejasne, źródło kasy jeśli niewykryte, i "co Cię zaskoczyło za późno" (tego nie da się wywnioskować z plików).

Nie udawaj, że nie widziałeś tego, co widziałeś. Człowiek ma poczuć, że panel zna jego biznes.
