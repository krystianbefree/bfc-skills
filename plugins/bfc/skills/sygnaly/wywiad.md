# Wywiad: sygnały

Cel: zbudować **mapę sygnałów pod usługę tego człowieka**. Ten sam fakt (ktoś szuka handlowca) jest sygnałem dla specjalisty od automatyzacji obsługi zapytań i szumem dla grafika. Dlatego nie dajemy gotowej listy, tylko dobieramy ją z fundamentu i potwierdzamy.

Mechanika pytań: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`. Maksymalnie 4 tury.
Wynik: `config.template.md` -> `<sejf>/BFC Skille/sygnaly/Config.md` oraz `Mapa sygnałów.md` wg `blueprints/mapa-sygnalow.md`.

**Zanim zapytasz o cokolwiek**, przeczytaj `Oferta.md` (sekcja „Problem, który rozwiązuję -> usługa", zwłaszcza „Widać go z zewnątrz po"), `Grupa docelowa.md` i `Metoda prospectingu.md`. Z nich proponujesz sygnały do potwierdzenia. Człowiek ma klikać i poprawiać, a nie wymyślać od zera.

---

### zanim_potrzebuje | tekst-dlugi | 1
**Pytanie:** Co dzieje się w firmie Twojego klienta, zanim zacznie potrzebować Twojej usługi? Przykład: przy 3 osobach w zespole Excel i mail wystarczą, przy 20 już nie, i dopiero wtedy pojawia się problem.
**Po co:** Z tej odpowiedzi wychodzą sygnały, które są Twoje, a nie ogólne. To jedno pytanie robi połowę mapy.
**Wnioskuj z:** `Oferta.md` - problem i „Widać go z zewnątrz po". Zaproponuj jedną wersję do poprawienia, zamiast pytać na pusto.
**Domyślnie:** Opis z `Oferta.md` przepisany jako zdarzenie w czasie („firma rośnie, a obsługa zapytań zostaje ręczna").
**Walidacja:** Musi opisywać zmianę albo moment, a nie stan („mają słabą stronę" to stan, „otwierają drugą lokalizację i strona nie nadąża" to moment). Stan -> dopytaj raz o moment.

### sygnaly_wzrost | wybor-wielu | 2
**Pytanie:** Które sygnały wzrostu u Twojego klienta znaczą, że możesz mu się przydać?
**Po co:** Wzrost to pieniądze i rosnący chaos. Wybrane pozycje skrypt i model będą sprawdzać przy każdym skanie.
**Opcje:** Rekrutacje (nowe ogłoszenia o pracę) :: sprawdzam ogłoszenia i zakładkę kariera | Nowa lokalizacja albo oddział :: pilnuję strony i adresów | Podwyższenie kapitału, nowa spółka :: pilnuję KRS | Ruszyły reklamy :: pilnuję biblioteki reklam Meta
**Wnioskuj z:** `Oferta.md`. Zaznacz jako proponowane te, które łączą się z problemem z oferty, i w opisie opcji napisz, co dany sygnał znaczy **dla tej usługi**.
**Domyślnie:** Rekrutacje, Nowa lokalizacja albo oddział
**Walidacja:** Co najmniej jedna pozycja albo świadome „żadna".

### sygnaly_zmiana | wybor-wielu | 2
**Pytanie:** Które zmiany w firmie są dla Ciebie dobrym momentem?
**Po co:** Nowa osoba na stanowisku ma kilka miesięcy, żeby pokazać, że coś zmieniła, i szuka do tego ludzi.
**Opcje:** Zmiana w zarządzie (KRS) :: pilnuję wpisów w KRS | Rebranding, nowa strona, nowe podstrony :: pilnuję strony | Nowa oferta albo produkt :: pilnuję strony | Zmiana pracy kogoś, z kim robiłem projekt :: pilnuję listy dawnych kontaktów
**Wnioskuj z:** `Oferta.md`, `Metoda prospectingu.md`.
**Domyślnie:** Zmiana w zarządzie (KRS), Rebranding, nowa strona, nowe podstrony
**Walidacja:** Co najmniej jedna pozycja albo świadome „żadna".

### sygnaly_bol | wybor-wielu | 2
**Pytanie:** Po czym z zewnątrz widać, że firma ma problem, który rozwiązujesz?
**Po co:** Ból to sygnał najbliższy Twojej usłudze. Tu najbardziej przydaje się drugi sygnał obok, bo jeden bywa przypadkiem.
**Opcje:** Ogłoszenie o pracę wraca albo długo wisi :: znaczy, że nie mogą kogoś znaleźć | Skupisko złych opinii z jednego okresu :: pilnuję opinii z datami | Instagram zamarł, choć wcześniej żył :: pilnuję profilu | Reklamy zniknęły :: pilnuję biblioteki reklam
**Wnioskuj z:** `Metoda prospectingu.md` („Po czym poznaję, że mają problem").
**Domyślnie:** Ogłoszenie o pracę wraca albo długo wisi, Skupisko złych opinii z jednego okresu
**Walidacja:** Co najmniej jedna pozycja albo świadome „żadna".

### sygnaly_intencja | wybor-wielu | 2
**Pytanie:** Gdzie Twoi klienci sami ogłaszają, że kogoś szukają?
**Po co:** Intencja to najcieplejszy sygnał, ale widzą go też inni, więc liczy się szybkość.
**Opcje:** Zapytania ofertowe w Bazie Konkurencyjności :: firmy z dotacją UE muszą tam publikować | Na stronie pojawia się logo dotacji :: zapowiedź zapytań ofertowych | Posty „szukam wykonawcy" w grupach i na Useme :: sprawdzam ręcznie, poza skanem
**Wnioskuj z:** `Grupa docelowa.md` (segment). Bazę Konkurencyjności proponuj, gdy klienci to firmy, które realnie biorą dotacje (produkcja, B2B, szkolenia, firmy rosnące).
**Domyślnie:** Na stronie pojawia się logo dotacji
**Walidacja:** Dowolna liczba.

### kalendarz | tekst | 3
**Pytanie:** Czy w Twojej branży są momenty, które znasz z wyprzedzeniem? Sezon, targi, termin nowego przepisu, nabór dotacji. Wypisz te, które realnie zmieniają potrzeby Twoich klientów.
**Po co:** To jedyne sygnały, które nic nie kosztują, bo nie trzeba ich szukać. Wystarczy data.
**Wnioskuj z:** Branża z `Grupa docelowa.md`. Zaproponuj 1-2 oczywiste (np. szkoła językowa: planowanie naboru w czerwcu). Terminów przepisów i naborów nie podawaj z pamięci, tylko po sprawdzeniu u źródła.
**Domyślnie:** brak (sekcja zostaje pusta, można dopisać później)
**Walidacja:** Każda pozycja ma okres albo datę i informację, kogo dotyczy.

### limit_na_skan | liczba | 3
**Pytanie:** Ile firm sprawdzać w jednym skanie?
**Po co:** Więcej firm to więcej tokenów i dłuższe czekanie. Reszta poczeka w kolejce do następnego razu.
**Opcje:** 15 :: rozsądny start | 10 :: oszczędnie | 25 :: duża lista, skan raz w tygodniu
**Domyślnie:** 15
**Walidacja:** Liczba od 3 do 50.

### pelny_co_dni | liczba | 3
**Pytanie:** Jak często robić pełny skan (z wyszukiwaniem ogłoszeń, Bazy Konkurencyjności i płatnymi sondami)? Pomiędzy skill robi lekkie skany, tylko z darmowych źródeł.
**Po co:** Pełny skan zużywa tokeny i grosze w Apify. Lekki prawie nic, a łapie KRS, stronę, narzędzia i ogłoszenia zapisane w kodzie.
**Opcje:** 28 :: raz w miesiącu, rozsądny start | 14 :: dwa razy w miesiącu, gdy lista jest mała | 56 :: oszczędnie, duża lista
**Domyślnie:** 28
**Walidacja:** Liczba od 7 do 90.

### przeglad_po_dniach | liczba | 3
**Pytanie:** Po ilu dniach bez żadnego sygnału mam zapytać, co zrobić z firmą?
**Po co:** Wtedy decydujesz: obserwować dalej, napisać zwykłą wiadomość bez sygnału albo odpuścić. Dzięki temu lista się nie zapycha.
**Opcje:** 90 :: kwartał, typowe okno po zmianie | 60 :: szybciej czyścisz listę | 120 :: dłuższe cykle zakupowe
**Domyślnie:** 90
**Walidacja:** Liczba od 30 do 365.

### kontakty | wybor | 3
**Pytanie:** Czy chcesz, żebym pilnował, gdzie pracują ludzie z Twoich dawnych projektów?
**Po co:** Osoba, z którą już pracowałeś, w nowej firmie to najmocniejszy sygnał: ufa Ci, a nowa firma nie zna jeszcze Twojej konkurencji.
**Opcje:** Tak, przez eksport z LinkedIna :: raz w miesiącu wrzucasz plik z kontaktami, skill sam wyłapuje zmiany pracy w całej sieci, zero tokenów | Tak, podam listę ręcznie :: imię, ostatnia firma, link; skill sprawdza ich wyszukiwaniem co 30 dni | Później :: dodasz komendą, kiedy zechcesz | Nie :: pomijam
**Domyślnie:** Później
**Walidacja:** Jedna opcja.

### klucze | wybor-wielu | 4
**Pytanie:** Które źródła chcesz mieć sprawdzane automatycznie? Bez kluczy skill działa na darmowych źródłach (KRS, strona firmy, wyszukiwanie).
**Po co:** Klucze zamieniają ręczne sprawdzanie w automat i oszczędzają tokeny. Każdy jest opcjonalny.
**Opcje:** Apify :: opinie Google z datami i aktywność na Instagramie, płatne za użycie (ułamki grosza za opinię) | Meta Ad Library :: reklamy firmy bez przeglądarki, darmowe, wymaga potwierdzenia tożsamości w Meta | Na razie nic :: działam na darmowych, płatne sondy wyłączone
**Wnioskuj z:** Sprawdź, czy klucz już jest: `S plan` zwraca `klucze.apify` i `klucze.meta`. Jest -> nie pytaj, tylko potwierdź jednym zdaniem.
**Domyślnie:** Na razie nic
**Walidacja:** Dowolne.

**Jak podpiąć klucz (powiedz to człowiekowi, gdy wybrał źródło, którego jeszcze nie ma):**

- Klucz wkleja **sam** do pliku `.env` w katalogu, z którego uruchamia Claude Code. Nigdy nie wkleja go do czatu i nigdy nie trafia on do sejfu.
- Apify: konto na apify.com, Settings -> API & Integrations, kopiuje token, w `.env` dopisuje linię `APIFY_TOKEN=...`.
- Meta Ad Library: wejście na facebook.com/ads/library/api, potwierdzenie tożsamości, aplikacja w Meta for Developers, token dostępu, w `.env` linia `META_ADLIB_TOKEN=...`. To trwa dłużej, więc zaproponuj „później", jeśli człowiek nie ma czasu.
- Po dopisaniu: `S plan` pokaże `klucze` jako `true`. Nie ma -> sprawdźcie nazwę zmiennej i katalog.
- Nie wybrał źródła płatnego -> w `Config.md` ustaw te sondy jako wyłączone (opinie, instagram). Reklamy zostają włączone w trybie ręcznym, sprawdzane tylko przy firmach z innym sygnałem.

---

## Po pytaniach: zapis

1. `Config.md` z `config.template.md`. Sondy włączasz zgodnie z wybranymi sygnałami i kluczami (tabela w `blueprints/zrodla.md` mówi, która sonda łapie który sygnał).
2. `Mapa sygnałów.md` wg `blueprints/mapa-sygnalow.md`: przy każdym sygnale **co znaczy dla tej usługi** i którą sondą jest łapany. To z tej mapy korzysta interpretacja przy każdym skanie.
3. Kontakty: „przez eksport z LinkedIna" -> podaj instrukcję eksportu z `blueprints/obserwowane.md` (Droga 1). „Ręcznie" -> poproś o listę (Droga 2). W `Config.md` zapisz wybrany sposób w polu `kontakty_sposob`.

## Walidacja na żywo (raz, po pierwszym wywiadzie)

Mapa sygnałów nie może zostać teorią. Weź **jedną** prawdziwą firmę: z obserwowanych, z notatki researchu albo podaną przez człowieka.

1. Dodaj ją (`S dodaj`), uzupełnij KRS i Instagram, jeśli łatwo je znaleźć.
2. Uruchom na niej sondy z planu. Pierwszy odczyt nie pokaże zmian, więc pokaż człowiekowi **stan**: co skrypt widzi na stronie, w KRS, w opiniach, co znalazło wyszukiwanie ogłoszeń.
3. Zapytaj jednym pytaniem: „Gdyby jutro coś z tego się zmieniło, które zmiany byłyby dla Ciebie powodem, żeby napisać?". Odpowiedź porównaj z mapą. Rozjazd -> popraw mapę teraz.
4. Powiedz, kiedy najbliższy skan ma sens (po kadencji najczęstszej sondy) i że wtedy zobaczy już zmiany.
