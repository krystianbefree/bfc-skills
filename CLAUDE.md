# bfc-skills - konwencje repo

Publiczny marketplace pluginów Claude Code dla klubowiczów Be Free Club.
Odbiorca: polskojęzyczny freelancer, często nietechniczny. Każda decyzja projektowa ma go nie zablokować.

## Układ

```
.claude-plugin/marketplace.json      # katalog: befreeclub -> bfc, bfc-admin
plugins/bfc/                         # to instalują klubowicze
  .claude-plugin/plugin.json         # version steruje aktualizacjami u ludzi
  wspolne/                           # czytane przez każdy skill tego pluginu
  skills/<nazwa>/SKILL.md            # jeden katalog = jeden skill
plugins/bfc-admin/                   # tylko dla opiekuna, defaultEnabled: false
scripts/waliduj.sh                   # odpal przed każdym pushem
```

## Twarde reguły platformy

- **Plugin nie widzi plików spoza swojego katalogu.** Przy instalacji kopiowany jest wyłącznie
  katalog pluginu, więc `../cokolwiek` nie zadziała u użytkownika. Dlatego `wspolne/` leży
  wewnątrz `plugins/bfc/`, a nie w korzeniu repo. Jeśli `bfc-admin` będzie kiedyś potrzebował
  tej samej wiedzy, kopiujemy plik, nie linkujemy.
- **Skille są namespace'owane nazwą pluginu**: `/bfc:research`, nie `/research`.
- **`${CLAUDE_PLUGIN_ROOT}` i `${CLAUDE_PLUGIN_DATA}` rozwijają się w treści SKILL.md w dowolnym
  miejscu.** Używamy tego zamiast ścieżek względnych.
- **Nigdy nie zapisujemy stanu w `${CLAUDE_PLUGIN_ROOT}`.** Ten katalog jest kasowany przy każdej
  aktualizacji pluginu. Stan idzie do `${CLAUDE_PLUGIN_DATA}` (przeżywa update) albo do sejfu użytkownika.
- **Podbicie `version` w `plugin.json` = klubowicze dostają zmianę.** Bez podbicia aktualizacja
  do nich nie dojedzie.

## Reguły treści

- Wszystko po polsku, na "Ty", luźno. Bez "guru", "mentora", "coacha", bez hustle culture.
- **Zero em-dashy i en-dashy w tekście polskim.** Zamiast `—` i `–` używamy `-`. To najszybszy
  sygnał, że coś napisała AI.
- Zero fraz z listy w `plugins/bfc/wspolne/jakosc-pl.md`. Ta lista obowiązuje też SKILL.md-y,
  nie tylko treść, którą one generują.
- W plikach `.json` nie używamy polskich znaków diakrytycznych (opisy pluginów lądują w UI
  i w różnych terminalach renderują się losowo).

## Anatomia skilla

Każdy skill w `plugins/bfc/skills/<nazwa>/` ma:

| Plik | Rola |
|---|---|
| `SKILL.md` | Kierunek i orkiestracja. Krok 0 to zawsze bramka konfiguracyjna. Krótki. |
| `wywiad.md` | Spec pytań: pole, typ, opcje, domyślna wartość, walidacja. |
| `config.template.md` | Szablon notatki zapisywanej w sejfie. Puste pola jako `TODO:`. |
| `blueprints/*.md` | Wiedza merytoryczna. Czytane dopiero wtedy, kiedy są potrzebne. |
| `solutions/*.sh|py` | Deterministyczny kod. Tylko tam, gdzie model nie powinien improwizować. |

`SKILL.md` ma być **cienki**. Wiedza idzie do `blueprints/`, żeby nie ładować jej do kontekstu
przy każdym uruchomieniu.

## Kontrakt bramki konfiguracyjnej

Każdy skill dla klubowicza zaczyna od tego samego:

1. Przeczytaj `${CLAUDE_PLUGIN_ROOT}/wspolne/sejf.md` i ustal ścieżkę sejfu.
2. Brak `Profil.md` -> wywiad profilowy z `wspolne/profil.wywiad.md`.
3. Brak `Config.md` skilla albo zostały w nim pola `TODO:` -> wywiad z `wywiad.md`, dopytaj tylko o braki.
4. Dopiero potem robota.

Nigdy nie każemy użytkownikowi "najpierw odpalić setupu". Setup ma się dziać sam, w miejscu,
w którym człowiek i tak już jest.

## Przed pushem

```
bash scripts/waliduj.sh
```

Sprawdza JSON-y, frontmattery, ścieżki wychodzące poza plugin, em-dashe i niedokończone sentinele.
Nic nie idzie na `main` bez zielonej walidacji i bez testu instalacji z lokalnej ścieżki.
