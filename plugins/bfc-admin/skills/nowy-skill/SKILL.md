---
name: nowy-skill
description: Tworzy nowy skill w bibliotece Be Free Club według standardu (SKILL.md + wywiad + config.template + blueprints), waliduje repo i publikuje zmianę do marketplace. Tylko dla opiekuna biblioteki. Użyj gdy ktoś mówi "dodaj skill do biblioteki BFC", "nowy skill dla klubowiczów", "opublikuj bibliotekę", "wypuść aktualizację skilli", "sprawdź czy repo jest ok".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, TodoWrite
---

# Nowy skill BFC

Narzędzie opiekuna biblioteki. Trzy tryby: `nowy`, `waliduj`, `publikuj`.

## Znajdź repo

1. Katalog bieżący zawiera `.claude-plugin/marketplace.json` z nazwą `befreeclub`? Użyj go.
2. Nie? Zapytaj o ścieżkę, sprawdź, czy plik tam jest.

Wszystkie ścieżki poniżej są względem korzenia repo.

---

## Tryb: nowy

### 1. Zbierz podstawy

Jedno wywołanie `AskUserQuestion`, cztery pytania:

- **Nazwa skilla** (kebab-case, po polsku, jedno albo dwa słowa)
- **Co robi** w jednym zdaniu, językiem klubowicza
- **Kiedy ktoś po niego sięgnie** - trzy albo cztery zwroty, których użyje
- **Czy potrzebuje wywiadu** - prawie zawsze tak; nie tylko wtedy, gdy skill nie ma
  żadnych ustawień specyficznych dla użytkownika

Nazwa nie może kolidować z istniejącym katalogiem w `plugins/bfc/skills/`.

### 2. Zaprojektuj wywiad, zanim napiszesz SKILL.md

To jest krok, który decyduje o jakości. Zadaj sobie i opiekunowi trzy pytania:

- **Co ten skill musi wiedzieć o użytkowniku, żeby wynik był jego, a nie generyczny?**
- **Co z tego jest już w `Profil.md`?** Tego nie pytamy drugi raz.
- **Czy każde pole naprawdę zmienia wynik?** Pole, które nic nie zmienia, wypada.

Zasady, których się trzymasz: `plugins/bfc/wspolne/onboarding.md`.
Maksymalnie 3 partie po 4 pytania. Maksymalnie 2 pytania otwarte na cały wywiad.
Wywiad dłuższy niż 3 partie znaczy, że skill robi za dużo - podziel go na dwa.

Wzorzec do naśladowania: `plugins/bfc/skills/oferta/wywiad.md`.

### 3. Wygeneruj pliki

```
plugins/bfc/skills/<nazwa>/
├── SKILL.md
├── wywiad.md
├── config.template.md
└── blueprints/<temat>.md
```

`SKILL.md` musi mieć:

- frontmatter z `name`, `description` (opis po polsku, z listą zwrotów wyzwalających)
  i `allowed-tools`
- **Krok 0 - konfiguracja**, dokładnie w tej formie co w istniejących skillach:
  sejf, profil, config, dopytywanie tylko o `TODO:`
- odwołania do wspólnych plików przez `${CLAUDE_PLUGIN_ROOT}/wspolne/...`
- odwołanie do `plugins/bfc/wspolne/jakosc-pl.md`, jeśli skill generuje tekst dla klienta
- treść merytoryczną w `blueprints/`, nie w `SKILL.md`

`SKILL.md` ma być cienki. Kierunek i decyzje, nie wiedza.

### 4. Sprawdź i pokaż

Uruchom walidację (tryb poniżej), pokaż wynik i zapytaj, czy publikujemy.

---

## Tryb: waliduj

```
bash scripts/waliduj.sh
```

Skrypt sprawdza:

- czy `marketplace.json` i wszystkie `plugin.json` parsują się jako JSON
- czy każdy `SKILL.md` ma frontmatter z `name` i `description`
- czy nazwa w frontmatterze zgadza się z nazwą katalogu
- czy w plikach skilli nie ma ścieżek wychodzących poza katalog pluginu (`../`)
- czy w treści dla klubowiczów nie ma myślników em ani en
- czy w plikach `.json` nie ma polskich znaków diakrytycznych
- czy odwołania do `blueprints/` i `wspolne/` wskazują na istniejące pliki

Coś nie przechodzi -> napraw, zanim cokolwiek pójdzie dalej. Nie publikujemy z czerwoną walidacją.

---

## Tryb: publikuj

1. **Walidacja.** Nie przeszła -> stop.
2. **Podbij wersję** w `plugins/bfc/.claude-plugin/plugin.json`.
   Bez tego zmiana **nie dojedzie** do klubowiczów, choćby była w repo.
   - nowy skill albo nowe pole w wywiadzie -> podbij drugą liczbę (`1.0.0` -> `1.1.0`)
   - poprawka w treści -> podbij trzecią (`1.1.0` -> `1.1.1`)
3. **Pokaż podsumowanie zmian** i zapytaj o zgodę na push. Repo jest publiczne,
   więc wszystko, co wypchniesz, jest od razu widoczne. Nigdy nie pushuj bez pytania.
4. Po zgodzie:

   ```
   git add -A
   git commit -m "<opis zmiany>"
   git push
   ```

5. **Podaj, co powiedzieć klubowiczom.** Krótko, do wklejenia na Circle:
   co nowego, jak to odpalić, czy trzeba coś zrobić (przy włączonym auto-update
   zwykle nic, przy wyłączonym `/plugin marketplace update` i `/plugin update bfc`).

## Ton komunikatów dla klubowiczów

Piszesz do freelancera, nie do programisty. Żadnych "namespace", "manifest", "frontmatter".
Zamiast tego: co to robi, jak tego użyć, co się zmieni w jego pracy.
Obowiązuje `plugins/bfc/wspolne/jakosc-pl.md`, łącznie z zakazem myślników em.
