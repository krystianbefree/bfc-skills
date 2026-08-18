# Wywiad profilowy

Wypełniany **raz**, przy pierwszym uruchomieniu dowolnego skilla BFC.
Wynik ląduje w `<sejf>/BFC Skille/Profil.md` i jest czytany przez wszystkie skille.

Mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`.
Szablon wyniku: `${CLAUDE_PLUGIN_ROOT}/wspolne/profil.template.md`.

Trzy partie, około 4 minut. Nic więcej do tego pliku nie dopisujemy - to jest wspólny mianownik
wszystkich skilli, a nie miejsce na szczegóły któregokolwiek z nich.

---

### obszar | wybor | 1
**Pytanie:** Czym się zajmujesz na co dzień?
**Po co:** Ustawia słownictwo i punkt odniesienia w każdym tekście, który dla Ciebie napiszę.
**Opcje:** Marketing i reklama :: kampanie, Meta Ads, Google Ads, strategia | Social media i treści :: prowadzenie kont, wideo, copy | Strony i sklepy :: WordPress, Shopify, Webflow, kod | AI i automatyzacje :: wdrożenia, boty, integracje, usprawnienia procesów
**Domyślnie:** Marketing i reklama
**Walidacja:** Jedna wartość. Jeśli człowiek wpisze swoje, zapisz dosłownie to, co napisał.

### forma_wspolpracy | wybor | 1
**Pytanie:** Jak najczęściej pracujesz z klientem?
**Po co:** Decyduje, czy oferta prowadzi do jednorazowego projektu, czy do stałej współpracy.
**Opcje:** Projekt z konkretnym zakresem :: oferta kończy się odbiorem i fakturą | Stała współpraca miesięczna :: oferta prowadzi do abonamentu, zakres opisany miesiącami | Godzinowo lub na godziny w pakiecie :: rozliczasz czas, nie efekt | Mieszanie :: projekt na start, potem opieka
**Domyślnie:** Projekt z konkretnym zakresem

### staz | wybor | 1
**Pytanie:** Od jak dawna to robisz?
**Po co:** Decyduje, czy w tekstach opieram się na Twoim doświadczeniu, czy na konkretnym efekcie dla klienta.
**Opcje:** Zaczynam :: unikam powoływania się na lata, gram konkretem i zaangażowaniem | Rok do trzech lat :: mogę wspominać o doświadczeniu ogólnie | Ponad trzy lata :: doświadczenie jest argumentem, mogę je wysuwać na przód
**Domyślnie:** Rok do trzech lat

### ton | wybor | 1
**Pytanie:** Jak się zwracasz do klientów?
**Po co:** Ustawia formę gramatyczną w każdym mailu i każdej ofercie. Zmiana w połowie brzmi fatalnie.
**Opcje:** Na Ty, luźno :: swobodnie, jak do kolegi po fachu | Na Ty, ale rzeczowo :: bezpośrednio, bez spoufalania się | Na Pan/Pani :: forma grzecznościowa, klasyczny biznes | Zależy od klienta :: zapytam przy każdym tekście
**Domyślnie:** Na Ty, ale rzeczowo

---

### co_sprzedajesz | tekst-dlugi | 2
**Pytanie:** Opisz w kilku zdaniach, co konkretnie sprzedajesz. Nie nazwę usługi, tylko co klient dostaje i co się u niego zmienia.
**Po co:** To jest rdzeń każdej oferty i każdego maila. Im konkretniej tu, tym mniej ogólników tam.
**Wnioskuj z:** Jeśli w sejfie są notatki o Twoich usługach, cenniku albo starych ofertach, zaproponuj podsumowanie na ich podstawie i poproś o poprawkę zamiast pytać od zera.
**Domyślnie:** TODO (to pole musi wypełnić człowiek, nie da się go zgadnąć)
**Walidacja:** Minimum dwa zdania i przynajmniej jedna konkretna rzecz, którą klient dostaje.

### dla_kogo | tekst | 2
**Pytanie:** Kto jest Twoim klientem? Branża, wielkość firmy, kto po ich stronie decyduje.
**Po co:** Bez tego research szuka wszystkiego, a maile trafiają do nikogo.
**Wnioskuj z:** Notatki o dotychczasowych klientach w sejfie.
**Domyślnie:** TODO
**Walidacja:** Musi zawierać branżę albo typ firmy. Sama fraza "małe firmy" to za mało - dopytaj raz o branżę.

---

### dowody | wybor-wielu | 3
**Pytanie:** Czym możesz się podeprzeć, rozmawiając z nowym klientem?
**Po co:** Decyduje, czym argumentuję w ofercie. Bez tego oferta stoi na obietnicach.
**Opcje:** Realizacje w portfolio :: będę się na nie powoływać z nazwy | Konkretne wyniki liczbowe :: liczby wejdą do ofert i maili | Referencje i opinie klientów :: cytaty jako dowód | Nie mam jeszcze czym :: gram procesem, gwarancją i konkretem zamiast historią
**Domyślnie:** Nie mam jeszcze czym

### portfolio_link | tekst | 3
**Pytanie:** Link do portfolio, strony albo profilu, który mogę podawać klientom. Jak nie masz, wpisz "brak".
**Po co:** Wstawiam go w maile i oferty zamiast pisać "chętnie pokażę przykłady".
**Domyślnie:** brak
**Walidacja:** Adres zaczynający się od http, albo słowo "brak".

### czerwone_linie | tekst | 3
**Pytanie:** Czego nigdy nie obiecujesz klientom albo czego nie robisz?
**Po co:** To jest bezpiecznik. Nic z tej listy nie pojawi się w żadnym tekście, który dla Ciebie napiszę.
**Domyślnie:** Nie obiecuję konkretnych wyników sprzedażowych ani pozycji w Google.
**Walidacja:** Dowolny tekst. Puste zamień na wartość domyślną.
