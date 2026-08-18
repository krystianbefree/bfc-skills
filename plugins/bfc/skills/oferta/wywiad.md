# Wywiad: oferta

Trzy partie. Mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`.
Szablon wyniku: `config.template.md` -> `<sejf>/BFC Skille/oferta/Config.md`.

To jest najważniejszy wywiad w całej bibliotece, bo dotyka pieniędzy.
Nie skracaj go, ale i nie rozdmuchuj - trzy partie wystarczą.

Nie pytaj o ton ani o dowody, to jest w `Profil.md`.

---

### uslugi | tekst-dlugi | 1
**Pytanie:** Wypisz usługi, które sprzedajesz, i przy każdej krótko: co klient dostaje na koniec.
**Po co:** To jest lista, z której dobieram to, co pasuje do problemu konkretnego klienta. Bez "co dostaje" oferta będzie opisywać Twoją pracę zamiast efektu.
**Wnioskuj z:** `co_sprzedajesz` w `Profil.md` oraz stare oferty i cenniki w sejfie. Znalazłeś - pokaż propozycję listy do poprawki, nie pytaj od zera.
**Domyślnie:** TODO
**Walidacja:** Minimum jedna usługa z opisem tego, co klient dostaje.

### model_rozliczen | wybor | 1
**Pytanie:** Jak rozliczasz te usługi?
**Po co:** Decyduje o całej konstrukcji oferty: czy kończy się odbiorem, czy prowadzi do stałej współpracy.
**Wnioskuj z:** `forma_wspolpracy` w `Profil.md`. Jeśli tam coś jest, pokaż to i poproś tylko o potwierdzenie.
**Opcje:** Stała cena za projekt :: klient wie z góry, ile zapłaci, Ty pilnujesz zakresu | Miesięczny abonament :: oferta prowadzi do stałej współpracy, zakres opisany miesiącami | Stawka godzinowa :: rozliczasz czas, w ofercie musi być szacunek godzin | Cena za projekt plus opieka :: wdrożenie na start, potem stała opłata
**Domyślnie:** Stała cena za projekt

### widelki | tekst | 1
**Pytanie:** W jakich widełkach cenowych się poruszasz? Podaj tak, jak myślisz o tym na co dzień, na przykład "od 3 do 8 tysięcy za projekt" albo "2 tysiące miesięcznie".
**Po co:** Bez tego oferta wyjdzie bez ceny, a oferta bez ceny wraca z pytaniem o cenę i traci tydzień.
**Wnioskuj z:** Cenniki i stare oferty w sejfie.
**Domyślnie:** TODO
**Walidacja:** Musi zawierać przynajmniej jedną kwotę. Sama waluta nie wystarczy.

---

### co_przesuwa_cene | tekst | 2
**Pytanie:** Co sprawia, że schodzisz do dolnej albo wychodzisz do górnej granicy widełek?
**Po co:** Dzięki temu oferta uzasadnia cenę zamiast ją tylko podawać. To jest połowa negocjacji załatwiona z góry.
**Domyślnie:** Zakres pracy, termin i to, ile materiałów dostarcza klient.
**Walidacja:** Dowolny tekst. Puste zamień na domyślne.

### warunki | wybor-wielu | 2
**Pytanie:** Które warunki mają zawsze znaleźć się w ofercie?
**Po co:** To są rzeczy, o które klienci pytają i tak. Lepiej, żeby były w dokumencie, niż w trzeciej wymianie maili.
**Opcje:** Termin realizacji :: kiedy skończysz, licząc od startu | Sposób płatności :: zaliczka, transze, płatność po odbiorze | Zakres poprawek :: ile rund poprawek wchodzi w cenę | Co jest po stronie klienta :: materiały, dostępy, decyzje, bez których stoisz
**Domyślnie:** Termin realizacji, Sposób płatności, Zakres poprawek
**Walidacja:** Minimum jedna pozycja.

### gwarancja | tekst | 2
**Pytanie:** Dajesz jakąś gwarancję albo zabezpieczenie dla klienta? Jak nie, wpisz "brak".
**Po co:** Przy pierwszej współpracy to często jest ten element, który przechyla decyzję. Ale tylko jeśli jest prawdziwy.
**Domyślnie:** brak
**Walidacja:** Dowolny tekst.

---

### dlugosc | wybor | 3
**Pytanie:** Jak długa ma być oferta?
**Po co:** Za długa nie zostanie przeczytana, za krótka nie odpowie na pytania. To zależy od tego, komu wysyłasz.
**Opcje:** Krótka, jedna strona :: dla małych firm i szybkich decyzji, sam konkret | Średnia, dwie albo trzy strony :: standard, jest miejsce na kontekst i dowody | Rozbudowana :: dla większych firm i dłuższych procesów decyzyjnych
**Domyślnie:** Średnia, dwie albo trzy strony

### format_pliku | wybor | 3
**Pytanie:** W czym chcesz dostać gotową ofertę?
**Po co:** Decyduje, czy piszę czysty tekst do wklejenia, czy dokument gotowy do wysłania jako plik.
**Opcje:** Notatka w sejfie :: kopiujesz stamtąd, gdzie chcesz, najprościej | Notatka plus wersja do wklejenia w maila :: dostajesz od razu skróconą wersję mailową | Dokument do wydruku albo PDF :: przygotuję strukturę pod eksport, z podziałem na strony
**Domyślnie:** Notatka plus wersja do wklejenia w maila

### folder_ofert | tekst | 3
**Pytanie:** W którym folderze sejfu mam zapisywać oferty?
**Po co:** Żeby leżały tam, gdzie ich szukasz.
**Wnioskuj z:** Poszukaj w sejfie folderu z nazwą zawierającą "Oferty", "Klienci" albo "Sprzedaż" i zaproponuj go.
**Domyślnie:** BFC Skille/oferta
**Walidacja:** Ścieżka względem katalogu sejfu.
