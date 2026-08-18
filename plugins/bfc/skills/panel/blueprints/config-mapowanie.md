# Config - mapowanie wywiadu na dashboard.config.yaml

Silnik czyta jeden plik `dashboard.config.yaml`. To jedyne miejsce z nazwami z konkretnego biznesu - kod adapterów jest generyczny. Poniżej: skąd bierze się każda wartość.

Config leży w katalogu projektu użytkownika (tam, gdzie skopiowany silnik). Ścieżki do plików sejfu rozwiązują się względem klucza `sejf:`, nie względem projektu.

## Skąd co pochodzi

| Klucz w configu | Źródło |
|---|---|
| `owner.name`, `owner.handle` | `Profil.md` |
| `sejf` | ścieżka sejfu ustalona w Kroku 0 (`sejf.md`) |
| `pipeline.stages` | odpowiedź `etapy_lejka` z wywiadu (albo etapy wywnioskowane ze skanu) |
| `pipeline.unit` / `unit_plural` | stałe: `firma` / `firmy` |
| `pipeline.file` | `Pozyskiwanie.md` (albo istniejący plik lejka ze skanu) |
| `signals.*` | rozbite progi z `sygnaly_late` |
| `sources.pozyskiwanie` | zawsze on; `file` = plik lejka; `import_research_dir` / `import_coldmail_dir` / `followup_dni` = dolewanie ze skilli klubowych |
| `sources.klienci.dir` | `folder_klienci` |
| `sources.biznes.dir` | `folder_biznes` |
| `sources.kasa` | `zrodlo_kasy` (tryb reczne / faktury / stripe / nie licze) + `co_liczysz`; `ledger_file` (faktury) i `accounts` (stripe) |
| `sources.tresci` | tylko gdy `publikuje_tresci` = regularnie; `file` = `Do nagrania.md` |
| `sources.statystyki` | razem z `tresci` (publikuje_tresci = regularnie); `file` = `Zasięgi.md` (zakładka Zasięgi). Opcjonalne, dla publikujących |
| `sources.outputy` | zawsze on; `dir` = `Outputy` (archiwum efektów, zakładka Archiwum) |
| `sources.timer` | zawsze on; zakładka Czas. Domyślne długości w bloku `timer:` (pomodoro/przerwy) |
| `sources.connectors` | zawsze on; `probes` = nazwy kluczy z `.env` do sprawdzenia (sama obecność) |
| `sources.toolkit` | zawsze on |
| `chat` / `terminal` | domyślnie `enabled: false` (człowiek ma Claude w terminalu obok). Terminal działa tylko na macOS/Linux |
| `notifications` | push macOS o nowych alarmach; domyślnie `enabled: false` |

Zakładki To-do i Kalendarz nie mają własnego źródła - front liczy je z pozostałych
bloków (zawsze dostępne). Front sam ukrywa zakładkę, której źródło ma `enabled: false`.

## Mózg zadań (CLAUDE.md)

Po zapisaniu configu wgraj ambientowe reguły z `claudemd.template.md` do `CLAUDE.md`
projektu (Krok 2.5 w SKILL.md): podstaw `{{PORT}}` i `{{SEJF}}`, wstaw między
znaczniki `BFC-PANEL:START/END`. To one sprawiają, że Claude sam pyta o status
zadania i archiwizuje efekt do `Outputy/` w każdej rozmowie. Pełne reguły:
`zadania-lifecycle.md`.

## Etapy lejka -> pipeline.stages

Rozbij `etapy_lejka` na listę. Każdy etap to `{id (slug), label (jak podał), hint (krótko po co)}`:

```yaml
pipeline:
  unit: "firma"
  unit_plural: "firmy"
  source: "markdown"
  file: "Pozyskiwanie.md"
  stages:
    - id: prospekt
      label: "Prospekt"
      hint: "znaleziona, jeszcze nie zaczepiona"
    - id: kontakt
      label: "Kontakt"
      hint: "cold mail wyszedł, czeka na odzew"
    - id: rozmowa
      label: "Rozmowa"
      hint: "gadamy, ustalamy zakres"
    - id: oferta
      label: "Oferta"
      hint: "oferta wysłana, czeka na decyzję"
```

Etap "Klient" nie jest kolumną lejka - klient przechodzi do zakładki Klienci.

## Sygnały -> progi

Każde zdanie z `sygnaly_late` zamień na jeden próg. Domyślne, jeśli człowiek nic nie doda:

```yaml
signals:
  dni_bez_ruchu_lejek: 14       # lead utknął
  dni_bez_kontaktu: 21          # klient bez kontaktu
  deadline_ostrzezenie_dni: 2   # projekt blisko terminu
```

## Kasa -> tryb

Klucz `zrodlo` wybiera źródło przychodu. Kontrakt dla frontu jest ten sam we wszystkich trybach: `revenue_window, funnel_value, active_clients, conversion, window_days, source, note` (+ dorzucone `source_label` i `is_real`, żeby UI pokazał „realne" vs „szacunek").

```yaml
sources:
  kasa:
    enabled: true
    ttl_minutes: 0            # 0 dla reczne/faktury (pliki); podnieś do ~60 dla stripe
    zrodlo: reczne           # reczne | faktury | stripe | nie_licze
    window_days: 30
    ledger_file: "Kasa.md"   # tryb faktury: plik ledgera w sejfie (format: pliki-sejfu.md)
    accounts:                # tryb stripe: wiele kont, klucz TYLKO jako nazwa zmiennej z .env
      - key_env: "STRIPE_API_KEY"
        label: "Be Free Club"
```

- `reczne` - SZACUNEK ze stawek aktywnych klientów (`is_real: false`). Nie mów o tym „przychód".
- `faktury` - REALNA gotówka: suma kwot ze statusem `oplacona` z okna `window_days` (plik `ledger_file`).
- `stripe` - REALNY przychód z API. Wiele kont w `accounts`; brak klucza danego konta -> odnotowane w `note`, reszta liczy się dalej. Bez żadnego klucza -> `revenue_window: null` + czytelny `note`, nigdy crash. Klucz API NIGDY w configu ani w payloadzie - tylko nazwa zmiennej (`key_env`).
- `nie_licze` - panel nie pokazuje kasy.

Tryb `stripe`/`faktury` bez danych (brak klucza / brak pliku) -> panel zostaje przy czytelnym `note`, a nie pustej karcie.

## Zasady

- Klucze API NIGDY w tym pliku. Tu tylko nazwa zmiennej (`key_env`), wartość w `.env`.
- Nie włączaj źródła, które nie ma z czego żyć. Brak folderu klientów -> `sources.klienci.enabled: false`, zakładka się nie pokaże.
- `ttl_minutes: 0` dla plików MD (czytaj zawsze na świeżo). Wyższy TTL tylko dla API (Stripe).
