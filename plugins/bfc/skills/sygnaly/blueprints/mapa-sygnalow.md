# Mapa sygnałów - kształt notatki

Notatka `<sejf>/BFC Skille/sygnaly/Mapa sygnałów.md` powstaje z wywiadu i jest czytana przy każdym
skanie w Kroku 4. To ona rozstrzyga, czy zmiana u firmy jest sygnałem dla **tej** usługi.

Zasady zapisu:

- Przy każdym sygnale piszesz, **co on znaczy dla usługi człowieka**, jednym zdaniem. Bez tego
  interpretacja przy skanie zgaduje.
- Przy każdym sygnale podajesz sondę, która go łapie (nazwy z `zrodla.md`). Sygnał bez sondy
  to sygnał, którego nikt nie sprawdzi - oznacz go `[ręcznie]`.
- Czego nie ustaliłeś, zostawiasz pustą sekcję z krótką notką. Nie dopisujesz sygnałów od siebie.

```markdown
---
utworzone: RRRR-MM-DD
skill: bfc/sygnaly
---

# Mapa sygnałów

## Zanim klient mnie potrzebuje
<odpowiedź z wywiadu, jako zdarzenie w czasie>

## Sygnały, na które reaguję

Przy sygnale, który człowiek uważa za wyraźnie mocniejszy albo słabszy od reszty, dopisz `waga: <liczba>`
(domyślnie 1, intencja i niespójność 1,5, kalendarz 0,5, zmiana pracy kontaktu 2).

### Wzrost
- <sygnał> - dla mnie znaczy: <...> - sonda: <praca / strona / krs / reklamy>

### Zmiana
- <sygnał> - dla mnie znaczy: <...> - sonda: <krs / strona / kontakty>

### Ból
- <sygnał> - dla mnie znaczy: <...> - sonda: <praca / opinie / instagram / reklamy>

### Intencja
- <sygnał> - dla mnie znaczy: <...> - sonda: <baza / strona>

### Kalendarz
- <wydarzenie> - kiedy: <okres albo data> - kogo dotyczy: <segment> - dla mnie znaczy: <...>

## Niespójności, które biorę
Dwie publiczne rzeczy, które do siebie nie pasują. Od razu dają hipotezę.
- <A> + <B> -> hipoteza: <...>

## Sygnały na „nie"
- Nie teraz (odkładam z datą): <np. zmiana właściciela w toku, środek sezonu>
- Skreślam: <np. otwarta likwidacja, świeżo obsadzone stanowisko, którego dotyczy moja usługa>

## Czego nie biorę
Głośne albo nie moje: <np. nagrody branżowe, posty o dotacji widziane przez wszystkich>
```

## Domyślne niespójności (zaproponuj te, które pasują do usługi)

| Co widać | Hipoteza |
|---|---|
| Reklamy aktywne, Instagram bez posta od 30+ dni | Ruch z reklamy trafia na pusty profil |
| Dużo dobrych opinii, stopka strony sprzed kilku lat | Polecenia nadrabiają to, co gubi strona |
| Rekrutacja handlowców, na stronie brak formularza | Handlowcy będą szukać klientów bez wsparcia strony |
| Logo dotacji na stronie, brak ogłoszeń w Bazie Konkurencyjności | Zapytania ofertowe są dopiero przed nimi |
| Problem z certyfikatem strony przy aktywnych reklamach | Część ruchu widzi ostrzeżenie przeglądarki |
| Reklamy aktywne, na stronie brak piksela reklamowego | Płacą za ruch i nie mierzą, co z niego wychodzi |
| Piksel reklamowy jest, analityki brak | Reklamy optymalizują się, ale nikt nie widzi całej ścieżki |
| Rezerwacje przez telefon, złe opinie o dodzwanianiu się, brak rezerwacji online | Obsługa zapytań się nie wyrabia |
