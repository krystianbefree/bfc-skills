# Wywiad: panel

**Do tego wywiadu wchodzisz po skanie sejfu (Krok 0.5 w SKILL.md), z gotową propozycją.**
Pytaj **tylko o to, czego ze sejfu nie dało się wywnioskować** albo co jest niejednoznaczne.
Pole rozstrzygnięte skanem -> nie pytasz, tylko pokazujesz, co ustaliłeś, i prosisz o potwierdzenie.

Mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`.
Szablon wyniku: `config.template.md` -> `<sejf>/BFC Skille/panel/Config.md`.

Panel dziedziczy z `Profil.md` (co sprzedajesz, dla kogo, forma współpracy, ton). Nie pytaj o to.

---

### publikuje_tresci | wybor | 1
**Pytanie:** Publikujesz treści (rolki, posty), żeby zdobywać klientów?
**Po co:** Decyduje, czy treści dostają osobne zakładki (Content + Zasięgi), siedzą w Biznesie, czy w ogóle ich nie ma. U większości freelancerów to zbędny kafelek.
**Wnioskuj z:** Skan sejfu. Jest folder Rolki/Treści/Content z notatkami -> zaproponuj "regularnie" i tylko potwierdź.
**Opcje:** Nie, pozyskuję bezpośrednio :: brak treści w panelu | Czasem :: treści jako sekcja w zakładce Biznes | Tak, regularnie :: zakładki Content (pipeline pomysł-nagranie-publikacja) + Zasięgi (statystyki treści)
**Domyślnie:** Nie, pozyskuję bezpośrednio
**Walidacja:** Jedna wartość. "Tak, regularnie" -> `sources.tresci.enabled: true` ORAZ `sources.statystyki.enabled: true`.

### etapy_lejka | tekst | 1
**Pytanie:** Jak nazywasz etapy zdobywania klienta? Od pierwszego kontaktu do podpisanej współpracy.
**Po co:** To są kolumny lejka w zakładce Pozyskiwanie. Twoje nazwy, bo na nie patrzysz codziennie.
**Wnioskuj z:** Skan sejfu (jak nazwane sekcje w notatkach o prospektach) i `forma_wspolpracy` z `Profil.md`. Przy stałej współpracy dodaj "Okres próbny".
**Domyślnie:** Prospekt -> Kontakt -> Rozmowa -> Oferta -> Klient
**Walidacja:** Minimum trzy etapy. Puste zamień na domyślne.

### co_liczysz | wybor-wielu | 1
**Pytanie:** Jakie liczby chcesz widzieć w zakładce Kasa?
**Po co:** Liczę tylko to, co zaznaczysz. Reszta to kafelki, na które nikt nie patrzy.
**Opcje:** Przychód w oknie 30 dni :: ile realnie wpłynęło | Wartość lejka :: suma potencjalnych deali w toku | Konwersja lead do klient :: ilu z zaczepionych zostaje klientem | Skuteczność outreachu :: ile wysłanych wiadomości, jaki procent odpowiedzi | Liczba aktywnych klientów :: ilu klientów masz teraz na pokładzie
**Domyślnie:** Przychód w oknie 30 dni, Wartość lejka
**Walidacja:** Minimum jedna pozycja.

---

### zrodlo_kasy | wybor | 2
**Pytanie:** Skąd panel ma brać kwoty przychodu?
**Po co:** Decyduje, czy liczby lecą automatycznie z API, czy wpisujesz je ręcznie.
**Wnioskuj z:** Skan sejfu i wykrycie narzędzi. Jest klucz Stripe -> zaproponuj Stripe. Są pliki faktur -> zaproponuj tryb ręczny na ich podstawie.
**Opcje:** Ręcznie w notatce :: wpisujesz kwoty przy kliencie, zero konfiguracji, działa od razu | Stripe :: automatycznie, jeśli masz klucz (podłączę go po stronie serwera) | Fakturownia albo inne API :: automatycznie, jeśli masz klucz | Na razie nie liczę kasy :: zakładka Kasa wyłączona
**Domyślnie:** Ręcznie w notatce
**Walidacja:** Jedna wartość. Stripe albo Fakturownia bez wykrytego klucza -> powiedz, gdzie go wpisać, i do tego czasu leć na trybie ręcznym.

### folder_klienci | tekst | 2
**Pytanie:** Gdzie w sejfie trzymasz obecnych klientów? Albo gdzie mam ich zakładać?
**Po co:** Zakładka Klienci czyta ten folder. Jeden plik = jeden klient, w środku jego projekty i jego to-do.
**Wnioskuj z:** Skan sejfu. Znajdź folder Klienci/CRM i zaproponuj go zamiast pytać.
**Domyślnie:** BFC Skille/panel/Klienci
**Walidacja:** Ścieżka względem katalogu sejfu.

### folder_biznes | tekst | 2
**Pytanie:** Gdzie trzymasz rzeczy dotyczące własnego biznesu? Własne projekty, pomysły, robota nad ofertą i stroną. Albo gdzie mam je zakładać?
**Po co:** Zakładka Biznes czyta ten folder. To jest praca nad Twoim biznesem, oddzielona od pracy dla klientów.
**Wnioskuj z:** Skan sejfu. Znajdź folder o nazwie typu Biznes / Moje / Projekty własne i zaproponuj go.
**Domyślnie:** BFC Skille/panel/Biznes
**Walidacja:** Ścieżka względem katalogu sejfu.

### sygnaly_late | tekst-dlugi | 2
**Pytanie:** Co Cię ostatnio zaskoczyło za późno w biznesie? Klient, do którego trzy tygodnie nikt się nie odezwał? Faktura po terminie? Follow-up, o którym zapomniałeś? Własny projekt, który stoi od miesiąca?
**Po co:** Każda taka rzecz staje się jednym sygnałem w sekcji Dziś. To jest to, co sprawia, że panel Cię pilnuje, zamiast tylko wyświetlać.
**Domyślnie:** Zaległy follow-up po cold mailu, projekt klienta blisko deadline, faktura po terminie
**Walidacja:** Dowolny tekst. Puste zamień na domyślne. Rozbij odpowiedź na osobne progi w configu.

### wpina_research | wybor | 2
**Pytanie:** Robisz outreach przez `/bfc:research` i `/bfc:cold-mail`?
**Po co:** Jeśli tak, panel dolewa ich wyniki (znalezione firmy, wysłane maile, statusy follow-upów) prosto do lejka w Pozyskiwanie.md. Nie musisz nic przepisywać.
**Wnioskuj z:** Skan sejfu. Są wyniki tych skilli (Prospekty, cold-mail) -> zaproponuj "Tak".
**Opcje:** Tak :: podpinam lejek pod wyniki research i cold-mail | Nie jeszcze :: lejek prowadzisz ręcznie, a ja dopisuję z rozmowy
**Domyślnie:** Tak
**Walidacja:** Jedna wartość.
