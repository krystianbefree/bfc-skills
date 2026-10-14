# Źródła sygnałów - katalog sond

Każda sonda ma koszt. Zasada: najpierw to, co sprawdza skrypt za darmo, potem to, co kosztuje
grosze, a na końcu to, co wymaga pracy modelu. Model nigdy nie czyta źródła „na wszelki wypadek".

## Która sonda łapie który sygnał

| Sygnał z mapy | Sonda |
|---|---|
| Rekrutacje, ogłoszenie wraca albo wisi | strona (ogłoszenia w kodzie, wątek rekrutacji), a gdy ich nie ma: praca |
| Nowa lokalizacja, nowa oferta, rebranding, nowe podstrony | strona (sitemapa, archiwum) |
| Piksel reklamowy, analityka, rezerwacje online, czat, zmiana platformy | strona (narzędzia w kodzie) |
| Zmiana w zarządzie, wspólników, kapitał, oddziały, adres, PKD, likwidacja | krs |
| Ruszyły albo zniknęły reklamy | reklamy |
| Skupisko złych opinii | opinie |
| Instagram zamarł albo ożył | instagram |
| Zapytania ofertowe z dotacji, logo dotacji | baza, strona |
| Zmiana pracy dawnego kontaktu | eksport LinkedIna (za darmo) albo kontakty (wyszukiwanie) |
| Sezon, targi, przepisy, nabory | kalendarz (z mapy, bez sondy) |

## Tryb skanu

- **Lekki**: tylko sondy z kosztem `darmowa` (krs, strona, reklamy z kluczem Meta). Zero wyszukiwań
  modelu, zero Apify. Domyślny między pełnymi skanami.
- **Pełny**: wszystkie włączone sondy. Domyślnie co 28 dni (ustawienie `pelny_co_dni`) albo na prośbę.

Sondy, których termin minął w skanie lekkim, czekają do najbliższego pełnego. Nic nie przepada.

## Sondy skryptowe (`S sonda <id> <nazwa>`)

### krs - darmowa
Oficjalne API Ministerstwa Sprawiedliwości (`api-krs.ms.gov.pl`), bez klucza.

- **Pierwszy odczyt:** skrypt pobiera pełny odpis z historią wpisów i zwraca zmiany z ostatnich 90 dni
  (zarząd, wspólnicy, kapitał, oddziały, adres, nazwa, PKD, dział 6) z datą wpisu. Wpisy o złożeniu
  sprawozdań finansowych pomija, bo są co roku u każdego.
- **Kolejne odczyty:** porównanie numeru ostatniego wpisu, przy zmianie rozpisanie, co się zmieniło.
- Nazwiska w API są zamaskowane, więc sygnał brzmi „zmiana w zarządzie", szczegóły w odpisie.
- Wymaga numeru KRS. Tylko spółki, fundacje, stowarzyszenia. Jednoosobowe działalności są w CEIDG
  i ta sonda ich nie obejmuje.
- Brak numeru -> znajdź go **raz**: jedno wyszukiwanie `"<nazwa firmy>" KRS` (rejestr.io, krs-online,
  aleo pokazują numer w opisie wyniku). Zapisz `S uzupelnij <id> <plik.json>` z `{"krs": "..."}`.
  Nie znalazłeś w jednym wyszukiwaniu -> zostaw.

### strona - darmowa
Jedno pobranie strony głównej daje kilka rzeczy naraz:

- **Tekst i wątki** (rekrutacja, nowa lokalizacja, nowa oferta, dofinansowanie). Przed porównaniem skrypt
  usuwa to, co zmienia się samo (baner cookies, stopka, daty, liczniki), więc nie ma fałszywych alarmów.
- **Sitemapa** (`sitemap.xml` albo adres z `robots.txt`): pełna lista podstron z datami zmian. Dokładniejsza
  niż linki ze strony głównej i działa też na stronach budowanych skryptami. Strona nie ma sitemapy ->
  skrypt porównuje linki ze strony głównej, tak jak wcześniej.
- **Narzędzia w kodzie**: piksel Meta, Google Ads, piksel TikTok, LinkedIn Insight, GA4, Tag Manager,
  Hotjar, Clarity, rezerwacje (Booksy, ZnanyLekarz, Calendly), czat, platforma (WordPress, Shopify,
  WooCommerce, PrestaShop, Shoper, Wix, Webflow), newsletter. Nowy piksel reklamowy to zwykle zapowiedź
  reklam. W `stan` jest pole `ma_piksel_reklamowy` do niespójności.
- **Ogłoszenia o pracę zapisane w kodzie** (dane strukturalne `JobPosting`) na stronie głównej i na jednej
  podstronie kariery. Gdy są, trafiają do tej samej pamięci co sonda `praca` i model nie musi ich szukać.
- **Pierwszy odczyt:** porównanie z wersją z archiwum internetu sprzed 60-120 dni (Wayback Machine,
  darmowe) oraz podstrony, które według sitemapy zmieniły się w ostatnich 30 dniach. Archiwum bywa
  przeciążone albo nie ma danej strony - wtedy po prostu bez tego porównania.
- `stan` oddaje też: formularz, rok w stopce, zakładka kariera, problem z certyfikatem.
- Strona za ochroną przed botami (np. kod 403) -> `[do ręki]`, nie ponawiaj.

### opinie - płatna (Apify)
Opinie z Google Maps, najnowsze, a przy kolejnych skanach tylko nowsze niż poprzedni skan, więc płacisz
za nowe. Skupisko złych opinii (3+ opinie 1-2 gwiazdki w 30 dni) liczy się już przy pierwszym odczycie,
bo opinie mają daty. Fragmenty opinii są do interpretacji, **nigdy do cytowania w wiadomości**.

- Działa z linkiem do Google Maps albo z nazwą i miastem. Przy pierwszym odczycie sprawdź
  `dopasowane_miejsce` i `adres`. To nie ta firma -> podaj właściwy link przez `S uzupelnij`.

### instagram - płatna (Apify)
Dni od ostatniego posta i obserwujący. Zgłasza zamarcie (30+ dni bez posta po okresie aktywności)
i powrót. Wymaga nazwy profilu (zwykle w stopce strony).

### reklamy - darmowa z kluczem Meta
Z `META_ADLIB_TOKEN` skrypt odpytuje Meta Ad Library API (reklamy wyświetlane w Polsce): ruszyły,
zniknęły, nowa partia. Przy pierwszym odczycie zgłasza reklamy, które wystartowały w ostatnich 30 dniach.
Sprawdź pole `strony`, czy to profil tej firmy.

Bez klucza skrypt zwraca `skipped` z linkiem do biblioteki reklam. Wtedy sprawdzasz przeglądarką
(Playwright: wejdź na link, odczytaj, czy są aktywne reklamy) **tylko u firm z innym sygnałem**. Wynik
przekaż `S obserwacja <id> inne` z elementem `{"tytul": "reklamy aktywne: tak/nie", "url": "<link>"}`.

## Sondy modelowe (`S obserwacja <id> <rodzaj> <plik.json>`) - tylko w skanie pełnym

Model zbiera, skrypt pamięta. Plik:

```json
{"elementy": [{"tytul": "Handlowiec B2B", "url": "https://...", "data": "RRRR-MM-DD"}]}
```

Podawaj `data` publikacji, gdy ją widać: przy pierwszym odczycie ogłoszenie z ostatnich 14 dni wychodzi
jako nowe, a starsze niż 45 dni jako wiszące. Pusta lista też jest wynikiem.

### praca - jedno wyszukiwanie
Tylko gdy sonda strony nie znalazła ogłoszeń w kodzie (wtedy plan już jej nie proponuje). Zapytanie:
`"<nazwa firmy>" praca` z ograniczeniem do portali, na których szuka ta branża (np. `site:pracuj.pl OR
site:olx.pl/praca OR site:justjoin.it OR site:nofluffjobs.com`).

- `tytul` = stanowisko, bez miasta i nazwy firmy (żeby to samo ogłoszenie dało ten sam klucz).
- Skrypt zwraca nowe (wzrost), powracające (ból: nie mogą kogoś znaleźć) i wiszące 45+ dni (ból).
- Ogłoszenie innej firmy o podobnej nazwie -> nie przekazuj.

### baza - jedno wyszukiwanie, rzadko
Baza Konkurencyjności (bazakonkurencyjnosci.funduszeeuropejskie.gov.pl): firmy z dotacją UE, które
muszą stosować zasadę konkurencyjności, publikują tam zapytania ofertowe. Publicznego API nie ma.

- Uruchamiaj u firm, u których sonda strony widzi wątek dofinansowania, albo gdy mapa każe sprawdzać zawsze.
- Sposób: wyszukiwarka serwisu po nazwie firmy (Playwright albo Firecrawl). Nie da się -> jedno wyszukiwanie
  `site:bazakonkurencyjnosci.funduszeeuropejskie.gov.pl "<nazwa>"`.
- `tytul` = przedmiot zapytania. Nowe zapytanie to sygnał intencji: pieniądze są i muszą wybrać wykonawcę.

### linkedin - wyłączona domyślnie
Bez logowania i bez scrapowania kont. Jedno wyszukiwanie `site:linkedin.com/company "<nazwa>"` albo
strona firmy na LinkedIn przez Firecrawl. Szukasz nowej osoby na stanowisku decyzyjnym. Mało pewne -
przekazuj tylko to, co ma link. Zmiany pracy ludzi z własnej sieci bierze się z eksportu (niżej).

## Eksport kontaktów z LinkedIna - darmowy

Człowiek raz w miesiącu pobiera z LinkedIna plik `Connections.csv` (instrukcja w `obserwowane.md`).
`S linkedin-import <plik>` porównuje go z poprzednim i zwraca zmiany pracy w całej sieci: najpierw kontakty
z dawnych projektów, potem stanowiska decyzyjne. Zero wyszukiwań, zero API, zgodne z regulaminem.
Pierwszy import to punkt odniesienia; kontakty z listy dawnych projektów porównuje od razu.

## Kalendarz (bez sondy)

Z `Mapa sygnałów.md`, sekcja Kalendarz. Wydarzenie, którego okres zaczyna się w ciągu 6 tygodni, daje
sygnał rodziny `kalendarz` firmom z pasującego segmentu, raz na wydarzenie i firmę. Terminy przepisów
i naborów sprawdź u źródła, zanim pójdą do wiadomości.

## Czego nie robimy

- Nie logujemy się nigdzie i nie omijamy zabezpieczeń stron.
- Nie zbieramy danych osobowych ponad to, co firma sama publikuje. Z eksportu LinkedIna skrypt zapisuje
  tylko imię, firmę, stanowisko i link, bez adresów e-mail.
- Nie wklejamy kluczy do poleceń w czacie. Skrypt czyta je z `.env`.
