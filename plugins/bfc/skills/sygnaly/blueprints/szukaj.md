# Tryb szukaj - nowe firmy, które mają sygnał już teraz

Zwykły skan pilnuje listy. Ten tryb robi odwrotnie: szuka w segmencie człowieka firm, u których sygnał
jest **teraz**, i dokłada je do listy razem z sygnałem. Prospekt przychodzi od razu z powodem do napisania.

Kosztuje więcej tokenów niż skan (to wyszukiwania modelu), więc uruchamiasz go osobną komendą i z limitem.

## Krok 1 - co i gdzie

1. Z `Mapa sygnałów.md` weź sygnały, które da się wyszukać od strony rynku (nie od strony konkretnej firmy):
   - **rekrutacje** na stanowisko z mapy (np. „recepcja", „handlowiec", „specjalista marketingu"),
   - **zapytania ofertowe** w Bazie Konkurencyjności w kategorii usług człowieka,
   - **sezon i terminy** z sekcji Kalendarz (firmy, których to dotyczy teraz).
2. Z `Grupa docelowa.md` weź branżę, miasto albo zasięg i dyskwalifikatory.
3. Zapytaj jednym pytaniem (`AskUserQuestion`), który sygnał przeszukać i ile firm najwyżej dodać
   (opcje: 5 / 10 / 20, domyślnie 10). Jeden sygnał na przebieg.

## Krok 2 - wyszukiwanie (limit: 3 zapytania)

- **Rekrutacje:** `"<stanowisko>" <miasto> site:pracuj.pl` (albo inny portal branży). Z wyników bierzesz
  nazwę pracodawcy, tytuł ogłoszenia, link i datę. Ogłoszenia agencji pośrednictwa pomijasz.
- **Baza Konkurencyjności:** wyszukiwarka serwisu po słowach usługi człowieka (np. „szkolenie z obsługi
  klienta", „strona internetowa", „kampania reklamowa"), ostatnie 30 dni. Bierzesz zamawiającego,
  przedmiot, termin składania ofert, link.
- **Kalendarz:** wyszukiwanie firm z segmentu, których dotyczy wydarzenie (np. lista wystawców targów).

Każda firma musi mieć link do źródła sygnału. Bez linku nie wchodzi.

## Krok 3 - filtr i dopisanie

1. Odrzuć firmy z dyskwalifikatorów `Grupa docelowa.md` i te, które już są na liście (`S lista`).
2. Zapisz plik JSON: firmy z polami jak przy dodawaniu (`obserwowane.md`), `zrodlo: szukaj`, a do każdej
   pole `sygnaly` z jednym sygnałem (rodzina, `sygnal`, `typ`, `sonda`, `zrodlo_url`, `data`). Przykład:

   ```json
   [{"nazwa": "Gabinet Uśmiech", "miasto": "Poznań", "zrodlo": "szukaj",
     "sygnaly": [{"rodzina": "wzrost", "sygnal": "Szukają drugiej osoby na recepcję", "typ": "praca_nowe",
                  "sonda": "praca", "zrodlo_url": "https://...", "data": "2026-10-10"}]}]
   ```
3. Pokaż listę (nazwa, sygnał, link) i zapytaj o zgodę (`AskUserQuestion` z `multiSelect`, do 4 firm na
   pytanie). Dodajesz tylko zaznaczone: `S dodaj <plik.json>`.
4. Zaproponuj `/bfc:research` na dodanych firmach (score, dominujący problem, haczyk) albo od razu
   `/bfc:cold-mail` na najmocniejszej, jeśli sygnał jest intencją (zapytanie ofertowe ma termin).

## Czego nie robimy

- Nie dobieramy firm bez sygnału, żeby dobić do liczby.
- Nie zgadujemy nazwy pracodawcy z ogłoszenia anonimowego.
- Nie przekraczamy 3 zapytań bez pytania człowieka.
