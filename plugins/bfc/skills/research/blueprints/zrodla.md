# Źródła firm

Katalog miejsc, z których bierzemy prospektów. **Które źródła i gdzie szukać opinii - z fundamentu:**
`Grupa docelowa.md` (pole `SEGMENT` + „gdzie szukać opinii per segment"). Segment steruje doborem, nie Config.

Przed użyciem sprawdź stan świata: te serwisy zmieniają się z miesiąca na miesiąc.
Coś nie działa jak opisano -> zanotuj to w wyniku i weź kolejne źródło, nie kombinuj w kółko.
Masz Firecrawl -> `firecrawl-search`/`firecrawl-scrape` (radzi sobie ze stronami JS i listingami).
Bez niego -> `WebSearch`/`WebFetch`.

## Dobór źródeł wg segmentu (z `Grupa docelowa.md`)

Segment mówi, gdzie są firmy i gdzie ich klienci zostawiają opinie. Domyślne (do potwierdzenia w wywiadzie):

| Segment | Gdzie szukać firm | Gdzie opinie klientów |
|---|---|---|
| lokalna usługa | Google Maps, katalogi (panoramafirm.pl) | Google Maps, gowork.pl |
| beauty / uroda | booksy.com, Google Maps | booksy.com, Google Maps |
| medycyna / gabinety | znanylekarz.pl, Google Maps | znanylekarz.pl |
| e-commerce | katalogi kategorii, Allegro, Ceneo | opineo.pl, ceneo.pl, Allegro, Empik (wg kategorii) |
| restauracje / gastronomia | Google Maps | Google Maps, gowork.pl |
| B2B / produkcja | aleo.com, panoramafirm.pl, LinkedIn | LinkedIn, aleo.com |
| doradztwo / usługi B2B | LinkedIn | LinkedIn |

Człowiek wskazał w `Grupa docelowa.md` inne źródło opinii dla swojej niszy -> użyj jego, nie domyślnego.
Serwis z listy blokuje automat (patrz niżej) -> `WebSearch` albo `[do ręki]`.

## Które strony blokują automat

Sprawdzone: `rejestr.io`, `pracuj.pl`, `gowork.pl` i biblioteka reklam Meta odrzucają zwykłe
pobranie strony (odpowiadają błędem 403). Nie znaczy to, że serwis nie działa - znaczy,
że nie wejdziesz tam przez `WebFetch`.

Co robić:

- Szukaj przez `WebSearch` i czytaj to, co widać w wynikach wyszukiwania.
- Masz Firecrawl -> użyj go, radzi sobie z częścią takich stron.
- Nadal nic -> zapisz w notatce link i `do sprawdzenia ręcznie`. Człowiek kliknie sam
  w 10 sekund. To lepsze niż zmyślona treść.

Bez problemu pobierają się: `aleo.com`, `panoramafirm.pl`, `opineo.pl`, `nofluffjobs.com`,
`justjoin.it`, `znanylekarz.pl`, `booksy.com`.

---

## Google i Google Maps

Najszersze źródło. Dobre do wszystkiego, co ma fizyczny adres albo lokalną obsługę.

Jak szukać:

```
<branża> <miasto>
<branża> <miasto> -oferty -praca -allegro
site:<domena katalogu> <branża> <miasto>
```

Co dostajesz: nazwę, stronę, adres, telefon, liczbę i średnią opinii.

Na co uważać:

- Wyniki mieszają firmy z ogłoszeniami i portalami. Odsiewaj wszystko, co nie jest stroną firmy.
- Sieciówki i franczyzy mają zwykle centralny marketing. Jeśli są na liście dyskwalifikatorów,
  wyrzuć je od razu.
- Liczba opinii to najlepszy szybki wskaźnik wielkości firmy w usługach lokalnych.

## LinkedIn

Do B2B i do znalezienia osoby decyzyjnej.

Jak szukać: przez `WebSearch`, nie przez wchodzenie na LinkedIn.

```
site:linkedin.com/company <branża> <miasto>
site:linkedin.com/in <stanowisko> <nazwa firmy>
```

Co dostajesz: nazwę firmy, wielkość zespołu, kto pracuje na stanowiskach decyzyjnych,
czasem ogłoszenia o pracę.

Na co uważać: profile prywatnych osób bierzemy **tylko** po to, żeby wiedzieć, kto pełni
jaką rolę. Nie zbieramy prywatnych danych kontaktowych. Do kontaktu używamy adresu firmowego.

## Katalogi branżowe

Dokładniejsze niż Google w wąskich niszach, bo firmy same się tam opisują.

Ogólne, polskie: `aleo.com`, `panoramafirm.pl`.
Branżowe: poszukaj `katalog firm <branża> Polska` - w większości nisz taki istnieje.
Usługowe z rezerwacją: `booksy.com` (uroda, barber, fizjoterapia), `znanylekarz.pl` (medycyna).

Co dostajesz: opis usług słowami samej firmy, dane kontaktowe, czasem cennik.
Opis usług to najlepszy materiał na pierwszą wiadomość, bo widać, jak firma sama o sobie mówi.

## Biblioteka reklam Meta

Publiczny rejestr reklam na Facebooku i Instagramie. Najlepszy dowód, że firma **ma budżet**
i już kupuje usługi marketingowe.

Adres: `facebook.com/ads/library`. Blokuje automatyczne pobieranie, więc:
szukaj przez `WebSearch` po nazwie firmy plus "ads library", a jak trzeba pewności -
zostaw link do sprawdzenia ręcznego.

Co z tego wyciągasz: czy w ogóle reklamuje, od kiedy, ile kreacji, jakiej jakości.
Firma z jedną reklamą sprzed roku to inna rozmowa niż firma z dwudziestoma aktywnymi.

## Ogłoszenia o pracę

Najbardziej niedoceniany sygnał. Firma, która rekrutuje, rośnie i ma pieniądze.
Firma, która od pół roku szuka specjalisty od czegoś, w czym Ty jesteś dobry,
właśnie powiedziała Ci, czego jej brakuje.

Gdzie: `nofluffjobs.com` i `justjoin.it` pobierają się bez problemu. `pracuj.pl` blokuje,
więc szukaj go przez `WebSearch`.

```
site:nofluffjobs.com <nazwa firmy>
<nazwa firmy> praca <stanowisko>
```

## Opinie klientów

Do znalezienia bólu, którym można otworzyć rozmowę.

Gdzie: opinie Google (widoczne w wynikach wyszukiwania), `opineo.pl` dla sklepów,
`znanylekarz.pl` dla gabinetów, `gowork.pl` dla opinii pracowników (blokuje automat,
szukaj przez `WebSearch`).

Jak czytać: interesują Cię **powtarzające się** zarzuty, nie pojedyncza zła opinia.
Trzy razy "nie odbierają telefonu" to problem operacyjny. Jeden wściekły komentarz to szum.

Twarda zasada: negatywnej opinii **nigdy nie cytujemy w pierwszej wiadomości**.
Wykorzystujemy wniosek z niej, nie sam cytat. Nikt nie lubi, gdy obcy człowiek zaczyna
rozmowę od pokazania mu najgorszej recenzji.
