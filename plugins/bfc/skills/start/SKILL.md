---
name: start
description: Punkt startowy biblioteki skilli Be Free Club. Przeprowadza głęboki wywiad, który buduje fundament pod resztę skilli (usługi, ceny, grupa docelowa, metoda prospectingu, dowody, głos), pokazuje status konfiguracji, pozwala zmienić ustawienia i diagnozuje problemy. Użyj gdy ktoś mówi "bfc start", "skonfiguruj skille", "ustaw moje dane", "zbuduj mi fundament", "co mam skonfigurowane", "zmień pricing", "zresetuj konfigurację", "skille nie działają" albo pierwszy raz sięga po skille BFC.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, TodoWrite
---

# BFC start

Wejście do biblioteki. To tu **buduje się fundament**, z którego research, cold-mail i oferta stają się realne, a nie generyczne. Bez tego research znajduje same nazwy, a mail brzmi jak AI. Pięć trybów, wybierasz po tym, czego człowiek chce.

## Krok 0 - ustal sejf

Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md` i wykonaj procedurę ustalania ścieżki sejfu. Ścieżkę zapamiętaj jako `<sejf>` na resztę sesji.

## Wybór trybu

Rozpoznaj z tego, co człowiek napisał. Jeśli nie da się rozpoznać, a `Profil.md` nie istnieje -> tryb **setup** bez pytania. Jeśli fundament istnieje, a intencja jest niejasna -> `AskUserQuestion` (setup / status / zmiana / reset / diagnostyka).

---

## Tryb: setup (głęboki wywiad - to jest sedno)

Uruchamiany, gdy nie ma jeszcze fundamentu (`<sejf>/BFC Skille/Profil.md` albo notatek-fundamentów).

To nie jest krótki onboarding. To wywiad, który **tworzy skille pod tego człowieka** - produkuje notatki-fundamenty, które czytają research, cold-mail i oferta. Pełna procedura, bloki, zasady drążenia i test-run na koniec: **`wywiad.md`**. Blueprinty pomocnicze: `blueprints/fundamenty.md` (kształt notatek), `blueprints/glos.md` (przechwyt głosu), `blueprints/prospecting-metoda.md` (wyciągnięcie metody).

Twarde zasady wywiadu (za `wywiad.md`): pytanie otwarte najpierw, drążysz aż masz konkret sprawdzalny (wynik > tempo), wysnuwasz z sejfu ale zawsze potwierdzasz („widzę w sejfie X, zgadza się?"), blok po bloku z zapisem po drodze, self-check „czego brakuje" po każdym bloku, a na koniec **test-run** na jednej prawdziwej firmie - dowód, że fundament daje wynik.

Po wywiadzie pokaż, co dalej:

| Skill | Do czego | Czyta fundament |
| --- | --- | --- |
| `/bfc:research` | Znajdź i zaudytuj firmy pod Twój profil, ze score | Grupa docelowa, Metoda prospectingu |
| `/bfc:cold-mail` | Napisz pierwszą wiadomość i follow-upy jak Ty | Głos, Oferta, Dowody + research |
| `/bfc:oferta` | Napisz ofertę dla konkretnego klienta | Oferta, Dowody |
| `/bfc:panel` | Żywy panel nad tym wszystkim (lejek, kasa, zadania) | notatki z sejfu |

Zapytaj, czy odpalamy któryś od razu.

---

## Tryb: status

1. Sprawdź, co z fundamentu istnieje w `<sejf>/BFC Skille/`: `Profil.md`, `Oferta.md`, `Grupa docelowa.md`, `Metoda prospectingu.md`, `Dowody.md`, `Głos.md`, oraz `Config.md` w podfolderach skilli (`<sejf>/BFC Skille/research/`, `oferta/`, `cold-mail/`, `panel/`).
2. W każdym istniejącym policz pola `TODO:` i rzeczy oznaczone `[do ręki]`.
3. Pokaż tabelę: pozycja, stan (`gotowe` / `brak` / `N do uzupełnienia`), ścieżka.
4. Sprawdź narzędzia: `bash "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-narzedzia.sh"` i dopisz jedną linię o tym, co dostępne.
5. Gdzieś są `TODO:` -> zaproponuj uzupełnienie teraz. Brak notatki-fundamentu -> zaproponuj setup danego bloku.

## Tryb: zmiana

Człowiek chce poprawić konkretną rzecz („zmień pricing", „inna grupa docelowa", „dosyłam próbki maili do głosu").

1. Ustal, której notatki dotyczy zmiana. Nie zgaduj między dwoma - zapytaj. Mapę pól weź z `blueprints/fundamenty.md` albo z szablonu configu danego skilla.
2. Przeczytaj plik, pokaż **obecną wartość**.
3. Zapytaj o nową (jedno pytanie, nie cały wywiad). Przy głosie - przyjmij nowe próbki i dostrój wzorzec.
4. Zmień **tylko to pole/sekcję**. Reszty nie ruszaj i nie przeformatowuj.
5. Potwierdź jednym zdaniem, co się zmieniło.

Chce zmienić cały blok -> uruchom ten fragment `wywiad.md` od nowa, ale **najpierw pokaż obecną wersję** i potwierdź nadpisanie.

## Tryb: diagnostyka

Uruchamiany, gdy coś nie działa. Sprawdź i zaraportuj każdy punkt:

1. `${CLAUDE_PLUGIN_DATA}/sejf.txt` istnieje i wskazuje na istniejący katalog?
2. `<sejf>/BFC Skille/` istnieje i zapisywalny?
3. Kluczowe pliki `${CLAUDE_PLUGIN_ROOT}/wspolne/` obecne? (po nieudanej aktualizacji potrafią zniknąć)
4. `python3 --version` działa? (potrzebne do wykrywania sejfów)
5. Zostały pola `TODO:` w fundamencie?

Najczęstsze przyczyny:

- **Sejf przeniesiony / zmieniona nazwa** -> `sejf.txt` wskazuje w próżnię. Ustal nową ścieżkę, nadpisz.
- **Skille nie pojawiają się** -> `/reload-plugins`, dalej nic -> `/plugin marketplace update` + `/plugin update bfc`. Uwaga: `/plugin` działa w terminalowym Claude Code, nie w rozszerzeniu edytora.
- **Konfiguracja zniknęła** -> dane są w sejfie, więc sprawdź, czy `sejf.txt` nie wskazuje na inny sejf.

## Reset

1. Zapytaj o zakres: cały fundament czy jedna notatka/skill.
2. **Nie kasuj.** Zmień nazwę starego na `<nazwa>.stare-RRRR-MM-DD.md`, powiedz gdzie leży.
3. Uruchom odpowiedni fragment wywiadu od nowa.

## Ton

Piszesz do freelancera, który chce mieć to z głowy i wrócić do roboty. Krótko, konkretnie, bez tłumaczenia mechanizmu. Obowiązuje `${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`, w szczególności zakaz myślników em.
