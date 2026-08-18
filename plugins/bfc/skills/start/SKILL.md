---
name: start
description: Punkt startowy biblioteki skilli Be Free Club. Przeprowadza wywiad startowy, pokazuje status konfiguracji, pozwala zmienić ustawienia dowolnego skilla i diagnozuje problemy. Użyj gdy ktoś mówi "bfc start", "skonfiguruj skille", "ustaw moje dane", "co mam skonfigurowane", "zmień pricing w ofercie", "zresetuj konfigurację", "gdzie są moje ustawienia", "skille nie działają" albo pierwszy raz sięga po skille BFC.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, TodoWrite
---

# BFC start

Wejście do biblioteki. Cztery tryby, wybierasz po tym, czego człowiek chce.

## Krok 0 - ustal sejf

Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md` i wykonaj procedurę ustalania ścieżki sejfu.
Ścieżkę zapamiętaj jako `<sejf>` na resztę sesji.

## Wybór trybu

Rozpoznaj z tego, co człowiek napisał. Jeśli nie da się rozpoznać, a `Profil.md` nie istnieje ->
tryb **onboarding** bez pytania. Jeśli `Profil.md` istnieje, a intencja jest niejasna ->
`AskUserQuestion` z czterema trybami poniżej.

---

## Tryb: onboarding

Uruchamiany, gdy nie ma jeszcze `<sejf>/BFC Skille/Profil.md`.

1. Przywitaj się jednym zdaniem i powiedz, co się teraz stanie. Bez wstępu o tym, czym są skille.
2. Przeprowadź wywiad profilowy: mechanika w `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`,
   pytania w `${CLAUDE_PLUGIN_ROOT}/wspolne/profil.wywiad.md`.
3. Zapisz `<sejf>/BFC Skille/Profil.md` z szablonu `${CLAUDE_PLUGIN_ROOT}/wspolne/profil.template.md`.
   `{{DATA}}` to dzisiejsza data w formacie RRRR-MM-DD.
4. Pokaż, co dalej. Krótko, tabelką:

   | Skill | Do czego |
   | --- | --- |
   | `/bfc:research` | Znajdź firmy pod Twój profil klienta |
   | `/bfc:oferta` | Napisz ofertę dla konkretnego klienta |
   | `/bfc:cold-mail` | Napisz pierwszą wiadomość i follow-upy |

   Dodaj jedno zdanie: każdy z nich dopyta o swoje szczegóły przy pierwszym użyciu,
   nie trzeba nic konfigurować z góry.

5. Zapytaj, czy odpalamy któryś od razu. Jak tak, przekaż sterowanie temu skillowi.

**Nie** przeprowadzaj tu wywiadów poszczególnych skilli. Onboarding ma być krótki.

---

## Tryb: status

1. Sprawdź, co istnieje:
   - `<sejf>/BFC Skille/Profil.md`
   - `<sejf>/BFC Skille/research/Config.md`
   - `<sejf>/BFC Skille/oferta/Config.md`
   - `<sejf>/BFC Skille/cold-mail/Config.md`
2. W każdym istniejącym pliku policz pola `TODO:`.
3. Pokaż tabelę: skill, stan (`gotowe` / `nieskonfigurowane` / `N pól do uzupełnienia`),
   ścieżka do pliku.
4. Sprawdź narzędzia: `bash "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-narzedzia.sh"`
   i dopisz jedną linię o tym, co jest dostępne.
5. Jeśli gdzieś są `TODO:`, zaproponuj uzupełnienie ich teraz.

---

## Tryb: zmiana

Człowiek chce poprawić konkretną rzecz ("zmień pricing", "inna grupa docelowa", "inne źródła").

1. Ustal, którego pliku dotyczy zmiana. Nie zgaduj między dwoma - zapytaj.
2. Przeczytaj plik i pokaż **obecną wartość** pola, którego dotyczy zmiana.
3. Zapytaj o nową wartość. Jedno pytanie, nie cały wywiad.
4. Zmień **tylko to pole**. Reszty pliku nie ruszaj i nie przeformatowuj.
5. Potwierdź jednym zdaniem, co się zmieniło.

Człowiek chce zmienić wszystko w danym skillu -> uruchom wywiad tego skilla od nowa,
ale **najpierw pokaż obecną konfigurację** i zapytaj, czy na pewno nadpisujemy.

---

## Tryb: diagnostyka

Uruchamiany, gdy coś nie działa.

Sprawdź po kolei i zaraportuj wynik każdego punktu:

1. `${CLAUDE_PLUGIN_DATA}/sejf.txt` istnieje i wskazuje na istniejący katalog?
2. `<sejf>/BFC Skille/` istnieje i da się do niego zapisać?
3. `python3 --version` działa? (potrzebne do wykrywania sejfów)
4. Czy w konfigach zostały pola `TODO:`?
5. Wykrywanie narzędzi zwraca sensowny wynik?

Najczęstsze przyczyny i co z nimi zrobić:

- **Sejf przeniesiony albo zmieniona nazwa katalogu** -> `sejf.txt` wskazuje w próżnię.
  Ustal nową ścieżkę i nadpisz plik.
- **Skille nie pojawiają się po instalacji** -> `/reload-plugins`, a jak dalej nic,
  to `/plugin marketplace update` i `/plugin update bfc`.
- **Konfiguracja zniknęła po aktualizacji** -> to nie powinno się zdarzyć, bo dane siedzą w sejfie.
  Sprawdź, czy `sejf.txt` nie wskazuje na inny sejf niż ten, którego człowiek używa.

## Reset

Człowiek prosi o reset:

1. Zapytaj o zakres: cały profil czy jeden skill.
2. **Nie kasuj plików.** Zmień nazwę starego na `<nazwa>.stare-RRRR-MM-DD.md` i powiedz, gdzie leży.
3. Uruchom odpowiedni wywiad od nowa.

## Ton

Piszesz do freelancera, który chce mieć to z głowy i wrócić do roboty.
Krótko, konkretnie, bez tłumaczenia jak działa mechanizm. Obowiązuje
`${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`, w szczególności zakaz myślników em.
