# Silnik wywiadu

Wspólna mechanika dla wszystkich skilli BFC. Skill nie wymyśla własnego sposobu zadawania pytań,
tylko wykonuje tę procedurę na swoim pliku `wywiad.md`.

Cel: człowiek odpowiada raz, krótko, i dostaje narzędzie działające pod siebie.
Wywiad, który męczy, jest gorszy niż brak wywiadu.

## Format specyfikacji pytań

Plik `wywiad.md` każdego skilla to lista pól w tym formacie:

```
### <id_pola> | <typ> | <partia>
**Pytanie:** Treść pytania zadawana człowiekowi.
**Po co:** Jedno zdanie, co to zmienia w wyniku. Mówisz to tylko, gdy ktoś dopyta.
**Opcje:** Opcja A :: opis | Opcja B :: opis | Opcja C :: opis
**Domyślnie:** Wartość używana, gdy ktoś powie "nie wiem" albo "wszystko jedno".
**Wnioskuj z:** Gdzie szukać odpowiedzi, zanim zapytasz (Profil.md, konkretne miejsce w sejfie).
**Walidacja:** Warunek, który odpowiedź musi spełnić.
```

Typy: `wybor` (jedna opcja), `wybor-wielu`, `tekst` (krótka odpowiedź), `tekst-dlugi` (kilka zdań),
`liczba`, `sciezka`.

`partia` to numer grupy. Pola z tej samej partii zadajemy w jednym pytaniu do użytkownika.
Pola bez `**Opcje:**` idą jako pytanie tekstowe.

## Procedura

### 1. Zbierz, czego już nie musisz pytać

Zanim zadasz pierwsze pytanie:

- Przeczytaj `Profil.md` z sejfu. Wszystko, co tam jest, jest już odpowiedziane.
- Dla każdego pola z `**Wnioskuj z:**` sprawdź wskazane miejsce. Znalazłeś kandydata ->
  nie pytaj "podaj X", tylko **pokaż propozycję do potwierdzenia**. To różnica między
  wywiadem, który irytuje, a takim, po którym człowiek myśli "o, ono mnie zna".
- Istnieje już `Config.md` tego skilla -> pytaj **wyłącznie** o pola oznaczone `TODO:`.
  Reszty nie ruszaj.

### 2. Powiedz, na co się piszą

Przed pierwszym pytaniem, jedno zdanie, konkretnie:

> Zadam Ci `<N>` pytań w `<M>` turach, to jakieś `<X>` minut. Wszystko zapiszę w sejfie
> w `BFC Skille/<skill>/Config.md`, więc potem możesz to poprawiać ręcznie, bez powtarzania wywiadu.

Bez wstępów, bez tłumaczenia się, bez "zanim zaczniemy, chciałbym...".

### 3. Pytaj partiami

Jedna partia = jedno wywołanie `AskUserQuestion`, maksymalnie 4 pytania naraz.

Reguły:

- **Zawsze dawaj konkretne opcje**, jeśli da się je sensownie wypisać. "Jaki masz pricing?"
  to złe pytanie. "Jak rozliczasz projekty?" z opcjami "za projekt / miesięczny retainer /
  za godzinę / mieszanie" to dobre pytanie. Człowiek zawsze może dopisać swoje.
- **Pierwsza opcja to najczęstszy wybór** w danej grupie. Ludzie klikają pierwsze sensowne.
- W `description` opcji pisz, **co ta opcja zmienia w wyniku**, a nie czym jest.
  Nie: "Retainer to stała miesięczna opłata". Tak: "Oferta będzie prowadzić do stałej współpracy,
  z zakresem miesięcznym zamiast listy zadań".
- Pytania otwarte (`tekst-dlugi`) zadawaj **osobno, tekstem**, nie upychaj ich w opcje.
  Maksymalnie 2 takie na cały wywiad. Więcej i człowiek się wyłącza.
- Nigdy nie zadawaj pytania, na które odpowiedź już masz.

### 4. Kiedy ktoś nie wie

"Nie wiem", "wszystko jedno", "zrób jak uważasz" -> weź `**Domyślnie:**`, zapisz je i **powiedz wprost**,
co przyjąłeś i gdzie to zmienić. Nie drąż, nie tłumacz, dlaczego to ważne. Idziemy dalej.

Wartość domyślna to normalna wartość, nie `TODO:`. Skill ma po niej działać.

### 5. Kiedy odpowiedź nie przechodzi walidacji

Dopytaj **raz**, konkretnie o to, czego brakuje. Druga próba nieudana -> zapisz to, co masz,
oznacz pole jako `TODO:` i leć dalej. Nie blokuj całego wywiadu jednym polem.

### 6. Zapisz

- Weź `config.template.md` skilla, wypełnij zebranymi wartościami.
- Pola, o których nie udało się zapytać albo które człowiek pominął -> zostają jako
  `TODO: <o co chodzi>`. To one wywołają dopytanie przy następnym uruchomieniu.
- Zapisz do `<sejf>/BFC Skille/<skill>/Config.md`.
- Plik już istniał -> nadpisz tylko pola `TODO:`, resztę zostaw nietkniętą.
  Człowiek mógł ręcznie poprawić coś, czego nie chcemy skasować.

### 7. Zamknij

Pokaż krótkie podsumowanie: co zapisane, gdzie leży plik, jak go zmienić.
Potem **od razu rób to, po co człowiek przyszedł**. Wywiad nie jest celem.

Jeśli zostały pola `TODO:`, wymień je jednym zdaniem i powiedz, na co wpłyną.

## Czego nie robimy

- Nie pytamy o rzeczy, które da się wywnioskować z sejfu albo z tego, co człowiek już napisał.
- Nie pytamy "na wszelki wypadek". Każde pytanie musi zmieniać wynik. Pole, które niczego nie zmienia,
  wypada ze specyfikacji.
- Nie zadajemy więcej niż 4 pytań w jednej turze i nie robimy więcej niż 4 tur.
  Wywiad dłuższy niż 4 tury to znak, że skill robi za dużo i trzeba go podzielić.
- Nie tłumaczymy metodologii. Człowiek chce ofertę, nie wykład o tym, jak działa personalizacja.
- Nie zaczynamy wywiadu od nowa, gdy `Config.md` już istnieje. Dopytujemy wyłącznie o `TODO:`.
