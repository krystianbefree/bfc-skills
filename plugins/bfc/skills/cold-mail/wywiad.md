# Wywiad: cold-mail

Dwie partie, krótko. Mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`.
Szablon wyniku: `config.template.md` -> `<sejf>/BFC Skille/cold-mail/Config.md`.

Nie pytaj o ton, dowody ani czerwone linie - to jest w `Profil.md`.
Nie pytaj o usługi ani ceny - to jest w `Config.md` skilla oferta, przeczytaj go, jeśli istnieje.

---

### kanal | wybor-wielu | 1
**Pytanie:** Gdzie najczęściej zaczepiasz nowych klientów?
**Po co:** Mail, LinkedIn i wiadomość na Instagramie to trzy różne teksty. Ta sama treść przeklejona między nimi wygląda źle w każdym.
**Opcje:** Mail :: najwięcej miejsca, temat wiadomości decyduje o otwarciu | LinkedIn :: krócej, mniej formalnie, bez tematu | Instagram albo Facebook :: bardzo krótko, ton rozmowy a nie pisma | Telefon po wcześniejszej wiadomości :: wiadomość ma tylko umówić rozmowę
**Domyślnie:** Mail
**Walidacja:** Minimum jeden kanał.

### jedna_oferta | tekst | 1
**Pytanie:** Z czym zaczepiasz w pierwszej wiadomości? Jedna rzecz, nie lista.
**Po co:** W pierwszym kontakcie proponujesz jedną rzecz. Trzy propozycje wymagają od odbiorcy decyzji, a on w skrzynce decyzji nie podejmuje.
**Wnioskuj z:** `uslugi` w `Config.md` skilla oferta oraz `co_sprzedajesz` w `Profil.md`. Jeśli tam jest kilka usług, zapytaj, która najlepiej otwiera rozmowę, i podaj je jako opcje.
**Domyślnie:** TODO
**Walidacja:** Jedna usługa albo jeden konkretny problem do rozwiązania. Wpisano kilka - dopytaj raz, która otwiera najlepiej.

### cta | wybor | 1
**Pytanie:** Czym chcesz kończyć pierwszą wiadomość?
**Po co:** To jedyna rzecz, którą odbiorca ma zrobić. Im mniejszy próg, tym więcej odpowiedzi.
**Opcje:** Pytanie zamknięte :: "Mam to rozpisać?" - najniższy próg, odpowiedź to jedno słowo | Propozycja krótkiej rozmowy :: konkretny termin, nie "kiedy Panu pasuje" | Wysyłam coś za darmo :: krótki audyt albo nagranie, jeśli powiedzą "tak" | Pytanie otwarte o ich sytuację :: wolniejsze, ale zaczyna rozmowę zamiast sprzedaży
**Domyślnie:** Pytanie zamknięte

### dlugosc | wybor | 1
**Pytanie:** Jak długa ma być pierwsza wiadomość?
**Po co:** Cold mail dłuższy niż ekran telefonu przegrywa, zanim ktokolwiek go przeczyta.
**Opcje:** Bardzo krótka, do 60 słów :: sam haczyk i pytanie, najwyższy odsetek odpowiedzi | Krótka, do 120 słów :: haczyk, jedno zdanie diagnozy, propozycja, pytanie | Średnia, do 200 słów :: dla bardziej złożonych usług i większych firm
**Domyślnie:** Krótka, do 120 słów

---

### liczba_followupow | wybor | 2
**Pytanie:** Ile razy przypominasz się, jeśli nie odpiszą?
**Po co:** Większość odpowiedzi przychodzi po drugiej albo trzeciej wiadomości, nie po pierwszej. Ale po czwartej to już nagabywanie.
**Opcje:** Dwa follow-upy :: rozsądny standard, nie męczy | Jeden follow-up :: gdy nie chcesz naciskać albo piszesz do małej grupy | Trzy follow-upy :: przy większych klientach i dłuższych procesach | Zero :: jedna wiadomość i tyle
**Domyślnie:** Dwa follow-upy

### odstepy | wybor | 2
**Pytanie:** Co ile dni wysyłasz kolejną wiadomość?
**Po co:** Wpisuję konkretne daty przy każdym follow-upie, żebyś nie musiał tego pilnować w głowie.
**Opcje:** 3 i 7 dni :: pierwszy szybko, drugi po tygodniu, sprawdzony rytm | 4 i 10 dni :: spokojniej, do większych firm | 2 i 5 dni :: szybciej, gdy sprawa jest pilna albo sezonowa
**Domyślnie:** 3 i 7 dni

### zakazane | tekst | 2
**Pytanie:** Są słowa albo zwroty, których nie chcesz w swoich wiadomościach?
**Po co:** Trafiają na twardą listę zakazów. Nic z tego nie pojawi się w żadnym tekście.
**Domyślnie:** Serdecznie zapraszam, oferta specjalna, wychodząc naprzeciw oczekiwaniom, kompleksowe rozwiązania, mam nadzieję że mail zastanie Pana w dobrym zdrowiu.
**Walidacja:** Dowolny tekst. Puste zamień na domyślne.

### folder_wiadomosci | tekst | 2
**Pytanie:** W którym folderze sejfu mam zapisywać wiadomości?
**Po co:** Żeby leżały razem z resztą materiałów o kliencie.
**Wnioskuj z:** Folder ustawiony w `Config.md` skilla research. Jeśli istnieje, zaproponuj ten sam.
**Domyślnie:** BFC Skille/cold-mail
**Walidacja:** Ścieżka względem katalogu sejfu.
