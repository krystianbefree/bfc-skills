# Wywiad: research

Trzy partie. Mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`.
Szablon wyniku: `config.template.md` -> `<sejf>/BFC Skille/research/Config.md`.

Nie pytaj o nic, co już jest w `Profil.md`. Pole `dla_kogo` z profilu jest punktem wyjścia
dla `profil_firmy` - pokaż je jako propozycję do doprecyzowania, nie pytaj od zera.

---

### profil_firmy | tekst | 1
**Pytanie:** Jakich firm mam szukać? Branża, a jeśli to ma znaczenie, to też wielkość i lokalizacja.
**Po co:** To jest zapytanie, z którym idę do źródeł. Im węższe, tym mniej śmieci w wynikach.
**Wnioskuj z:** `dla_kogo` w `Profil.md`. Pokaż tę wartość i zapytaj, czy doprecyzować.
**Domyślnie:** Wartość `dla_kogo` z profilu.
**Walidacja:** Musi zawierać branżę albo typ firmy.

### wielkosc | wybor | 1
**Pytanie:** Jakiej wielkości firmy Cię interesują?
**Po co:** Decyduje, gdzie szukam i kogo szukam po stronie klienta. W jednoosobowej firmie decyduje właściciel, w większej ktoś z marketingu.
**Opcje:** Jednoosobowe i mikro :: właściciel decyduje sam, szybka decyzja, mniejszy budżet | Małe, do 50 osób :: jest już ktoś od marketingu, decyzja w tydzień lub dwa | Średnie i większe :: dłuższy proces, kilka osób w decyzji, większe budżety | Bez znaczenia :: nie filtruję po wielkości
**Domyślnie:** Małe, do 50 osób

### lokalizacja | tekst | 1
**Pytanie:** Gdzie mam szukać? Miasto, region, cała Polska, zagranica.
**Po co:** Filtruje źródła. Bez tego lokalne katalogi są bezużyteczne.
**Domyślnie:** Cała Polska
**Walidacja:** Dowolny tekst.

### ile_firm | liczba | 1
**Pytanie:** Ile firm mam znajdować w jednym przebiegu?
**Po co:** Więcej firm to dłuższe czekanie. Lepiej robić mniejsze tury i od razu pisać.
**Opcje:** 10 :: szybko, dobre na start i na testowanie segmentu | 20 :: pełna tura na jeden dzień pracy | 5 :: bardzo dokładnie, mało firm, dużo szczegółów o każdej
**Domyślnie:** 10
**Walidacja:** Liczba od 1 do 50. Powyżej 20 uprzedź, że to potrwa.

---

### zrodla | wybor-wielu | 2
**Pytanie:** Skąd mam brać firmy?
**Po co:** Każde źródło daje inne firmy i inne dane. Wybór decyduje, co w ogóle da się znaleźć.
**Opcje:** Google i Google Maps :: najszersze, dobre do lokalnych usług i firm z fizycznym adresem | LinkedIn :: dobre do B2B, widać decydentów i ogłoszenia o pracę | Katalogi branżowe :: dokładniejsze w wąskich niszach, mniej śmieci | Biblioteka reklam Meta :: pokazuje, kto już płaci za reklamę, czyli ma budżet
**Domyślnie:** Google i Google Maps
**Walidacja:** Minimum jedno źródło.

### sygnaly | wybor-wielu | 2
**Pytanie:** Po czym mam poznać, że firma jest warta zaczepienia?
**Po co:** To jest filtr, który odróżnia listę firm od listy szans. Bez tego dostajesz książkę telefoniczną.
**Opcje:** Wydaje na reklamę :: ma budżet i już kupuje usługi marketingowe | Rekrutuje :: rośnie, ma pieniądze, często szuka też z zewnątrz | Ma widoczny problem w mojej działce :: stara strona, martwe social media, słabe opinie | Niedawno coś zmienili :: nowa strona, nowy produkt, zmiana właściciela
**Domyślnie:** Ma widoczny problem w mojej działce
**Walidacja:** Minimum jeden sygnał.

---

### dane | wybor-wielu | 3
**Pytanie:** Jakie dane mam zbierać o każdej firmie?
**Po co:** Zbieram tylko to, co zaznaczysz. Reszta to marnowanie czasu i notatki, których nikt nie czyta.
**Opcje:** Kontakt i kto decyduje :: mail, telefon, imię osoby decyzyjnej z firmowej strony | Stan strony i social mediów :: co konkretnie jest do poprawy w Twojej działce | Opinie klientów :: co ludzie im wytykają, gotowy materiał na pierwszą wiadomość | Czym się zajmują i dla kogo :: kontekst do rozmowy, żeby nie pisać ogólników
**Domyślnie:** Kontakt i kto decyduje, Stan strony i social mediów
**Walidacja:** Minimum jedna pozycja.

### dyskwalifikatory | tekst | 3
**Pytanie:** Co sprawia, że od razu odpuszczasz firmę?
**Po co:** Odsiewam je przed zbieraniem danych, więc nie tracisz czasu na firmy, których i tak nie chcesz.
**Domyślnie:** Agencje z tej samej branży co ja, firmy bez strony internetowej, sieciówki i franczyzy z centralnym marketingiem.
**Walidacja:** Dowolny tekst. Puste zamień na domyślne.

### folder_wynikow | tekst | 3
**Pytanie:** W którym folderze sejfu mam zapisywać notatki o firmach?
**Po co:** Żeby wpadały tam, gdzie ich szukasz, a nie w osobny kąt.
**Wnioskuj z:** Poszukaj w sejfie folderu o nazwie zawierającej "Klienci", "Prospekty", "Sprzedaż" albo "CRM" i zaproponuj go.
**Domyślnie:** BFC Skille/research
**Walidacja:** Ścieżka względem katalogu sejfu.
