---
name: panel
description: Buduje zywy panel dowodzenia nad Twoim freelance-biznesem - pozyskiwanie klientow, obecni klienci z ich projektami, Twoj wlasny biznes, kasa. Najpierw skanuje Twoj sejf Obsidian i sklada panel z tego, co juz masz, potem dopytuje tylko o luki. Zapisuje fakty z rozmowy prosto do notatek (zapis) i synchronizuje maile oraz kalendarz z lejkiem (sync). Uzyj gdy ktos mowi "zrob mi dashboard", "panel", "centrum dowodzenia", "chce widziec swoj biznes w jednym miejscu", "co mam dzis do zrobienia z klientami", "zsynchronizuj panel", "zapisz to do panelu".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, TodoWrite, Skill
---

# Panel dowodzenia freelancera

Stawiasz człowiekowi jedno okno, które odpowiada na cztery pytania: **kogo dziś zaczepić albo dopilnować, co u obecnych klientów, co w moim własnym biznesie, ile kasy**. Serce panelu to pozyskiwanie klientów - to jest główna robota freelancera i główny powód, dla którego uczył się Claude Code.

Silnik to lokalny serwer (dane na żywo, klucze API po stronie serwera). Markdown w sejfie jest źródłem prawdy, a człowiek i tak rozmawia z Claude, więc panel dopisuje zmiany do notatek prosto z rozmowy.

## Zasada nadrzędna

Zacznij od sejfu, nie od szablonu. Panel ma się złożyć z tego, co ten człowiek **już ma** w swojej bazie wiedzy, i pokazywać to, na co i tak patrzy raz dziennie. Pusta zakładka uczy, że panel jest do oglądania, nie do używania. Nie buduj zakładek na zapas.

Panel wykłada fakty i podaje link. Nie ustawia priorytetów za człowieka.

## Krok 0 - konfiguracja

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`, ustal `<sejf>`.
2. Brak `<sejf>/BFC Skille/Profil.md` -> wywiad profilowy (`${CLAUDE_PLUGIN_ROOT}/wspolne/profil.wywiad.md`), zapisz, wróć tutaj.
3. Przeczytaj `Profil.md`. Panel **dziedziczy** z niego: co sprzedajesz, dla kogo, forma współpracy, ton. Nie pytaj o to drugi raz.
4. Wykryj narzędzia i klucze: `bash "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-narzedzia.sh"`. Zasady: `${CLAUDE_PLUGIN_ROOT}/wspolne/narzedzia.md`.

## Krok 0.5 - skan sejfu i propozycja (to jest sedno)

Zanim cokolwiek zapytasz, przejdź bazę wiedzy człowieka i **złóż z niej gotową propozycję panelu**. Pełna procedura: `blueprints/skan-sejfu.md`. W skrócie:

1. **Mapa struktury** - `find`/`ls` na folderach i nazwach plików sejfu. Nie czytaj wszystkiego. **Pomiń foldery prywatne** (dziennik, finanse osobiste, zdrowie) zgodnie z `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md`.
2. **Czytaj tylko notatki biznesowe, które coś wnoszą**: foldery typu Klienci / Prospekty / Projekty / Oferty / CRM, wyniki `research` i `cold-mail`, folder treści jeśli jest.
3. **Wywnioskuj propozycję**:
   - Ma już klientów? (pliki w Klienci/CRM) -> zasil zakładkę **Klienci**.
   - Ma notatki o własnym biznesie, ofercie, stronie, systemach? -> zasil zakładkę **Biznes**.
   - Publikuje treści? (folder Rolki/Treści/Content) -> zaproponuj zakładkę **Treści** albo sekcję w Biznesie.
   - Jakie etapy lejka widać w notatkach? Jakie liczby i źródła są w zasięgu (klucz Stripe w `.env`, pliki faktur)?
4. **Pokaż propozycję jako szkic, nie pytanie**: "Z Twojego sejfu wygląda, że masz 8 klientów w folderze X, prowadzisz lejek w Y i publikujesz rolki. Zbuduję panel tak: [zakładki + skąd biorą dane]. Zgadza się?"
5. **Dopiero teraz wywiad** (`wywiad.md`, mechanika `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`) - i to **tylko o luki i niejasności**, których ze sejfu nie dało się wywnioskować. Pole rozstrzygnięte skanem = nie pytasz. Zapisz z `config.template.md` do `<sejf>/BFC Skille/panel/Config.md`.

Człowiek ma zobaczyć, że panel zna jego biznes, zanim zada pierwsze pytanie.

## Krok 1 - załóż dane, jeśli ich nie ma

Panel czyta Markdown z sejfu. Czego skan nie znalazł, załóż z gotową strukturą, żeby panel nie był pusty. Struktury: `blueprints/pliki-sejfu.md`.

- `Pozyskiwanie.md` - lejek. Jedna sekcja na etap z configu, każdy prospekt to jedna linia z datą ostatniego ruchu. **Źródło prawdy lejka.** Wyniki `research` i `cold-mail` dolewają się tutaj (`blueprints/pozyskiwanie.md`).
- `Klienci/<Klient>.md` - jeden plik na klienta: status, ostatni kontakt, stawka, sekcja `## Projekty` (deliverables z etapem i deadline) i sekcja `## Do zrobienia` (checkboxy dla tego klienta).
- `Biznes/` - Twój własny biznes: własne projekty (zbuduj ofertę, stronę, system, marketing) i własne to-do. Praca **nad** biznesem, nie dla klienta.
- `Outputy/` - archiwum gotowych efektów skończonych zadań (cenniki, oferty, scenariusze, teksty). Pusty na start, Claude zapisuje tu efekty z rozmowy przy zamykaniu zadań. Podfoldery per typ: `Wyceny`, `Oferty`, `Treści`, `Scenariusze`, `Maile`, `Strategie`, `Inne`. Struktura i konwencja: `blueprints/zadania-lifecycle.md`.

Jeśli w sejfie już są odpowiedniki (folder Klienci, notatki projektowe) - **używaj ich**, nie zakładaj drugich. Markdown zostaje źródłem prawdy, nie przenoś tego do bazy.

## Krok 2 - złóż i odpal silnik

1. Skopiuj cały katalog `${CLAUDE_PLUGIN_ROOT}/skills/panel/solutions/` do projektu użytkownika (silnik + `solutions/panel.py` + `solutions/panel.sh` + `solutions/panel.cmd` + `solutions/requirements.txt`). Silnik ma przeżyć aktualizację pluginu, więc **nie zostaje** w `PLUGIN_ROOT`.
2. Napisz `dashboard.config.yaml` z propozycji ze skanu plus odpowiedzi z wywiadu (mapowanie: `blueprints/config-mapowanie.md`). Nazwy etapów, progi sygnałów, źródła kasy, ścieżki do folderów sejfu - wszystko tu. Kod adapterów nie zawiera ani jednej nazwy z konkretnego biznesu.
3. Odpal launcherem cross-platform (sam zakłada `.venv` i doinstalowuje zależności przy pierwszym razie):
   - macOS / Linux: `solutions/panel.sh` (przez `bash`)
   - Windows: `solutions/panel.py` (przez `python`, albo dwuklik `solutions/panel.cmd`)
   - panel wstaje na `http://127.0.0.1:8765`

Klucze API zostają po stronie serwera. Nigdy w pliku w sejfie, nigdy we froncie.

## Krok 2.5 - mózg zadań w CLAUDE.md (always-on)

Panel żyje, bo człowiek rozmawia z Claude, a Claude pisze do plików. Żeby działało to w **każdej** rozmowie, nie tylko po `/bfc:panel`, wgraj reguły do `CLAUDE.md` projektu - to jedyny plik czytany co sesję.

1. Weź `${CLAUDE_PLUGIN_ROOT}/skills/panel/claudemd.template.md`.
2. Podstaw `{{PORT}}` (port panelu) i `{{SEJF}}` (ścieżka sejfu).
3. Dopisz do `CLAUDE.md` w katalogu, z którego człowiek odpala Claude Code (utwórz plik, jeśli go nie ma). Blok jest owinięty znacznikami `<!-- BFC-PANEL:START -->` / `<!-- BFC-PANEL:END -->` - jeśli już tam są, **podmień treść między nimi** (idempotentnie), nie doklejaj drugiego.

Pełne reguły (wykrycie pracy nad zadaniem, pytanie o status przy zamknięciu, archiwizacja efektu do `Outputy/`, podawanie efektu z archiwum) opisuje `blueprints/zadania-lifecycle.md`. Blok w `CLAUDE.md` to ich skrót do pamięci stałej. Od tej pory, gdy w rozmowie powstaje konkret pasujący do otwartego zadania, Claude sam pyta o status i zapisuje output.

## Krok 3 - zakładki

Domyślne, freelance-first:

- **Samouczek** - ściąga: co która zakładka robi i czego potrzebuje, żeby ożyła. Status na żywo (działa / czeka na Ciebie / wyłączone). Zawsze. To pierwsze miejsce, do którego kierujesz człowieka po instalacji.
- **Dziś** - max 5 pozycji. Agregat sygnałów plus terminowe to-do zebrane od klientów i z Biznesu.
- **Pozyskiwanie** - lejek nowych klientów.
- **Klienci** - obecni klienci; przy każdym jego projekty i jego to-do.
- **Biznes** - Twój własny biznes: własne projekty i to-do.
- **To-do** - agregat wszystkich otwartych zadań od klientów i z Biznesu (front-only, zawsze).
- **Kasa** - liczby z configu.
- **Archiwum** - gotowe efekty skończonych zadań z `Outputy/`, klikalne, z kopiowaniem. Domyślnie on.
- **Zasięgi** - statystyki treści (zasięg, top posty) dla publikujących. Włącza się razem z Content (`publikuje_tresci` = regularnie). Dane z `Zasięgi.md`.
- **Kalendarz** - terminy z pozostałych bloków, liczony we froncie (zawsze).
- **Czas** - timer roboczy (pomodoro/stoper), stan po stronie serwera. Domyślnie on.
- **Połączenia** - stan integracji na żywo (konektory claude.ai, MCP, klucze API). Domyślnie on.
- **Toolkit** - skróty do `research`/`oferta`/`cold-mail` i narzędzi AI klubu.

Zakładka **Content** (treści do nagrania) pojawia się tylko, gdy `publikuje_tresci` = regularnie. Przy "czasem" treści są sekcją w Biznesie. Przy "nie" - nie ma ich wcale.

Front **sam ukrywa** zakładkę, której źródło jest wyłączone w configu (`enabled: false`) - żeby nie było pustych kafelków. Dziś, To-do, Kalendarz zostają zawsze (liczone z innych bloków). Czat i Terminal domyślnie wyłączone.

Reguły treści zakładek: `blueprints/zakladki.md`. Poziom **alarm** rezerwuj na rzeczy, które kosztują pieniądze albo są nieodwracalne.

## Krok 3.5 - podłączenia (żeby panel robił więcej sam)

Panel działa bez żadnej integracji, ale to podłączenia zamieniają go w coś, co żyje samo. Po zbudowaniu panelu przeprowadź **jeden aktywny krok** propozycji podłączeń, w pozytywnej ramie („podłącz X, a panel zacznie sam robić Y"), nie „brakuje Ci X". Pełna procedura, co odblokowuje każde, jak podłączyć i bezpieczeństwo: `blueprints/integracje.md`.

Rdzeń (proponuj zawsze): **Stripe** (realny przychód w Kasie), **Gmail** (oferty i odpowiedzi same do lejka przez `sync`), **Google Calendar** (spotkania -> ostatni kontakt + Kalendarz). Kontekstowo dopytaj o to, co u tego człowieka realnie widać (Notion/Slack/arkusze - gdzie trzyma klientów albo z nimi gada) i zadaj jedno otwarte pytanie o inne warte podłączenia. Klucze/tokeny NIGDY w czacie: Stripe do `.env`, konektory claude.ai autoryzuje na koncie. „Później" = zapis jako niepodłączone, bez wracania - zakładka Połączenia i tak pokazuje status na żywo.

## Krok 3.6 - samouczek (na koniec instalacji)

Panel stoi, ale człowiek go nie zna. Zanim skończysz, **przejdź w tekście po zakładkach** i skieruj go do zakładki **Samouczek** (jest w panelu, pokazuje status na żywo). W czacie wypisz zwięźle, per zakładka: **do czego jest** + **czy już działa, czy czeka na niego** (i na co konkretnie). Bazuj na TYM, co realnie ma włączone - nie recytuj wszystkich zakładek, tylko te, które widzi:

- **działa** (jest źródło i dane) - jedno zdanie, co tam zobaczy.
- **czeka na Ciebie** (włączone, ale pusto) - konkret, co dorzucić („dodaj klientów", „wpisz zasięgi", „podłącz Stripe albo wpisuj kwoty").
- **wyłączone** (świadomie) - wspomnij raz, że da się włączyć, jeśli zechce (np. Content/Zasięgi przy publikowaniu).

Cel: po instalacji człowiek wie, gdzie patrzeć i co zrobić, żeby puste zakładki ożyły. Zakładka Samouczek zostaje jako ta sama ściąga na później.

## Krok 4 - aktualizacja z rozmowy (write-back)

To jest różnica między panelem-obrazkiem a panelem, który żyje. Kiedy człowiek mówi coś, co zmienia stan biznesu ("wysłałem ofertę firmie X za 4k", "Nowak zapłacił", "skończyłem stronę dla Kowalskiego", "nowy pomysł na własny lead magnet"), **nie pomijaj tego po cichu**. Zaproponuj zapis jednym zdaniem ("Zapisać to do panelu? Przesunę X do Oferty") i po potwierdzeniu dopisz do właściwego pliku: lejek, plik klienta albo Biznes. Reguły, mapowanie zdań na pliki i oba tryby (pasywny + na żądanie): `blueprints/write-back.md`.

Twarde: jedna zmieniona linia na jeden fakt, kopia przed zapisem, potwierdzasz niejednoznaczne, nie wymyślasz danych, brak liczby to "brak danych", a nie zero.

Osobna, mocniejsza warstwa to **lifecycle zadań**: gdy praca w rozmowie jest robieniem konkretnego zadania z panelu (cennik, oferta, scenariusz), przy zamknięciu **zawsze pytasz o status** i na "zrobione" archiwizujesz efekt do `Outputy/` plus odhaczasz zadanie z linkiem. Pełne reguły: `blueprints/zadania-lifecycle.md` (te same, które lądują w `CLAUDE.md` w Kroku 2.5).

## Krok - zapis z rozmowy na żądanie

Gdy pada "/bfc:panel zapisz" albo "zapisz to do panelu", świadomie przejrzyj **bieżącą rozmowę** pod kątem faktów biznesowych (wysłana oferta, rozmowa, płatność, nowy lead, zrobione zadanie) i zastosuj write-back do wszystkiego, co znajdziesz. Procedura i lista faktów: `blueprints/write-back.md` (sekcja "Dwa tryby"). Na końcu raportuj jedną linią na zmianę, niejednoznaczne potwierdź przed zapisem.

## Krok - synchronizacja zdarzeń (Gmail/kalendarz)

Gdy pada "zsynchronizuj panel", "/bfc:panel sync" albo "podciągnij maile do panelu", pobierz zdarzenia biznesowe z Gmaila i Kalendarza przez MCP i dolej je do lejka i klientów: wysłana oferta -> etap Oferta, odpowiedź prospekta -> Rozmowa lub `follow-up:`, spotkanie z klientem -> `ostatni_kontakt:`. Pełna procedura, zapytania, prywatność i degradacja bez MCP: `blueprints/sync-zdarzen.md`. Tylko firmy już obecne w sejfie, niejednoznaczne potwierdź przed zapisem. Domyślnie ręcznie na żądanie, opcjonalnie cyklicznie przez `/schedule`.

## Krok 5 - osadzenie w Obsidianie

1. Wtyczki użytkownika: **Custom Frames** + **Terminal**.
2. Custom Frames -> ramka z URL `http://127.0.0.1:8765`, przeciągnij do lewego panelu.
3. Terminal -> odpal `claude`.

Efekt: panel po lewej, notatki w środku, Claude po prawej. Jedno okno.

## Krok 6 - weryfikacja

- [ ] Odpal panel i **zobacz go na oczy** (screenshot).
- [ ] Zapis do plików sprawdź **na kopii**: dokładnie jedna zmieniona linia.
- [ ] Liczby zgadzają się ze źródłem.
- [ ] Odmiana liczebników po polsku: 1 klient, 2 klientów, 5 klientów.
- [ ] Zero em-dashów w tekstach dla użytkownika.

Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`.
