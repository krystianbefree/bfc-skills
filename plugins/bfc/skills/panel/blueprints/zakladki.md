# Zakładki - co w której siedzi i czego nie robić

Zakładki są sterowane configiem. Domyślny zestaw freelance-first. Pusta zakładka uczy, że panel jest do oglądania - jeśli dana zakładka nie ma z czego żyć u tego człowieka, nie pokazuj jej.

## Dziś (zawsze, max 5 pozycji)

Agregat tego, co wymaga ruchu dzisiaj: sygnały z configu plus terminowe to-do zebrane od klientów i z Biznesu. Sortuj po pilności.

- Więcej niż 5 pozycji przestaje być listą na dziś. Jak jest więcej, pokaż 5 najpilniejszych i licznik "i 4 dalsze".
- Każda pozycja nazywa fakt i daje link do miejsca (plik klienta, lejek). Nie moralizuje, nie ustawia priorytetów za człowieka.

## Pozyskiwanie (rdzeń)

Lejek nowych klientów. Szczegóły: `pozyskiwanie.md`.

## Klienci (rdzeń)

Obecni klienci, jeden kafelek na klienta: status, ostatni kontakt, stawka. W rozwinięciu jego projekty (etap + deadline) i jego to-do. To jest praca **dla** klienta.

- Klient bez kontaktu dłużej niż próg z configu -> sygnał.
- Zakończony klient schodzi na dół, nie znika (historia i szansa na powrót).

## Biznes (rdzeń)

Twój własny biznes: własne projekty i to-do. Praca **nad** firmą, nie dla klienta (oferta, strona, systemy, marketing). Jeśli `publikuje_tresci` = "czasem", treści są tu jako jedna z inicjatyw.

- Własny projekt, który stoi bez ruchu miesiąc -> delikatny sygnał (info, nie alarm). To Twój wybór, nie zaległość wobec klienta.

## Kasa (jeśli `zrodlo_kasy` != "nie liczę")

Tylko liczby z `co_liczysz`. Źródło wg `zrodlo_kasy`. Brak danych pokazuj jako "brak danych", nie jako zero. Stary eksport z API pokazuj z jego wiekiem, nie udawaj świeżości.

## Treści (tylko jeśli `publikuje_tresci` = regularnie)

Prosty pipeline pomysł -> nagranie -> publikacja. Bez atrybucji sprzedaży do pojedynczej treści.

## To-do (zawsze, front-only)

Agregat wszystkich otwartych `- [ ]` od klientów i z Biznesu, pogrupowany (po terminie / zaplanowane / bez terminu / zrobione). Nie ma własnego źródła - liczy się z bloków klienci i biznes. Odhaczenie zapisuje do właściwego pliku.

## Archiwum (jeśli `sources.outputy` on)

Gotowe efekty skończonych zadań z `Outputy/`, pogrupowane po typie (Wyceny, Oferty, Treści...). Karta klikalna, w podglądzie przycisk „Kopiuj tekst" i ścieżka pliku. To jest pamięć długoterminowa panelu: cennik sprzed miesiąca da się znaleźć i wkleić, nie tonie w czacie. Zapis robi Claude przy zamykaniu zadania (`zadania-lifecycle.md`), panel tylko pokazuje.

## Kalendarz (zawsze, front-only)

Siatka miesiąca liczona we froncie z pozostałych bloków: deadline'y projektów, terminy zadań, follow-upy, wpłaty. Jest też jako widget w Dziś. Nie ma własnego źródła ani zapisu.

## Czas (jeśli `sources.timer` on)

Timer roboczy: pomodoro albo stoper, wybór długości, przerwa, sygnał dźwiękowy na koniec. Stan trzyma serwer (`timer_state.json` + log), front tyka lokalnie. „Nad czym pracujesz" bierze otwarte zadania z klientów i Biznesu.

## Połączenia (jeśli `sources.connectors` on)

Stan integracji na żywo: konektory claude.ai i serwery MCP z konfiguracji, klucze API sprawdzane lekkim zapytaniem. **Wartości kluczy nie opuszczają serwera** - pokazujemy tylko, czy działa. Cache kilka minut, żeby nie bić API.

## Zasięgi (jeśli `sources.statystyki` on - razem z Content)

Statystyki treści dla publikujących: kafelki (zasięg w oknie, średni zasięg, najlepszy post, liczba postów), prosty wykres zasięgu kolejnych postów, ranking najlepszych. Dane z `Zasięgi.md` (człowiek wpisuje liczby albo Claude dopisuje z rozmowy). Bez atrybucji sprzedaży do pojedynczego posta. Instagram na żywo to tryb do dołożenia - domyślnie ręcznie, jak reszta panelu.

## Samouczek (zawsze, front-only)

Ściąga: co która zakładka robi i czego potrzebuje, żeby zaczęła żyć. Każda pozycja ma status liczony na żywo: **działa** (jest źródło i dane), **czeka na Ciebie** (włączone, ale pusto - i konkret, co dorzucić), **wyłączone** (można włączyć w wywiadzie/configu). To jest pierwsze miejsce, do którego kierujesz człowieka po instalacji.

## Toolkit (zawsze)

Skróty do `/bfc:research`, `/bfc:oferta`, `/bfc:cold-mail` i narzędzi AI klubu. Status configów skilli (uzupełniony / ma TODO). Pod spodem stan świeżości źródeł.

## Auto-ukrywanie

Front pokazuje zakładkę opcjonalną (Content, Archiwum, Czas, Połączenia, Kasa i rdzeniowe źródła) tylko, gdy jej źródło jest w payloadzie `/api/data` (czyli `enabled: true` w configu). Wyłączone źródło = zakładka znika, zero pustych kafelków. Dziś, To-do, Kalendarz zostają zawsze.

## Poziomy sygnałów

`ok / info / warn / alarm`. **Alarm** rezerwuj na rzeczy, które kosztują pieniądze albo są nieodwracalne (faktura po terminie, deadline dziś). Jeśli wszystko jest alarmem, nic nim nie jest.
