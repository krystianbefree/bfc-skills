# Taksonomia - proza fundamentu na strukturę dla score

Score musi być deterministyczny, więc `solutions/score.py` nie czyta prozy z `Oferta.md`.
Czyta strukturę: `Taksonomia.json` + `icp.json`. Ten blueprint mówi, jak z notatek-fundamentów
(które pisze człowiek zwykłymi zdaniami) skompilować tę strukturę.

Zapis: `<sejf>/BFC Skille/research/Taksonomia.json` i `.../icp.json`. Warstwa pośrednia - człowiek
pisze prozę, silnik dostaje strukturę, oboje mogą zajrzeć i poprawić. Regeneruj przy każdym przebiegu,
jeśli nie masz pewności, że fundament się nie zmienił (kompilacja jest tania: 2 pliki wczytać, 2 zapisać).

## Skąd co czytasz

- `Oferta.md`, sekcja „Problem, który rozwiązuję -> usługa": każda usługa ma `problem`, `widać po`
  (sygnał obserwowalny), `gdzie sprawdzić`, oraz cenę z sekcji wyceny.
- `Metoda prospectingu.md`: `czego szukam / po jakim sygnale / gdzie / czym sprawdzam / [do ręki]`
  oraz opcjonalny `próg` - nadpisuje domyślne progi i mówi, których sond NIE odpalać.
- `Grupa docelowa.md`: ICP -> `icp.json`.

## Biblioteka detektorów (gotowe wpisy JSON - kopiuj i podstaw usługę/cenę/priorytet)

Człowiek pisze „wolna strona", „nie odbierają telefonu", „martwe IG". Ty dobierasz gotowy detektor
i podstawiasz `usluga`, `cena`, `priorytet` z `Oferta.md`. **Progi są ekskluzywne** (`score.py` porównuje
ostro `<`/`>`), więc bierz je z tych wzorów, nie zgaduj. `usluga`/`cena` ZAWSZE z Oferty - żadnych cen na sztywno.

```json
{ "klasa": "wolna strona", "gdzie": "Lighthouse",
  "sygnal": {"zrodlo":"lighthouse.performance","typ":"prog","kierunek":"ponizej","prog_krytyczny":40,"sev_krytyczny":8,"prog_sredni":60,"sev_sredni":5} }

{ "klasa": "slabe SEO", "gdzie": "Lighthouse",
  "sygnal": {"zrodlo":"lighthouse.seo","typ":"prog","kierunek":"ponizej","prog_krytyczny":50,"sev_krytyczny":5,"prog_sredni":70,"sev_sredni":3} }

{ "klasa": "wygasly SSL", "gdzie": "HTTP",
  "sygnal": {"zrodlo":"ssl_error","typ":"incydent","sev_incydent":10} }

{ "klasa": "strona nie odpowiada", "gdzie": "HTTP",
  "sygnal": {"zrodlo":"http_5xx","typ":"incydent","sev_incydent":10} }

{ "klasa": "brak drogi kontaktu", "gdzie": "strona /kontakt",
  "sygnal": {"zrodlo":"kontakt_braki","typ":"prog","kierunek":"powyzej","prog_krytyczny":1,"sev_krytyczny":7,"prog_sredni":0,"sev_sredni":3} }

{ "klasa": "brak obslugi na stronie", "gdzie": "strona",
  "sygnal": {"zrodlo":"livechat_brak","typ":"incydent","sev_incydent":4} }

{ "klasa": "nieaktualna strona", "gdzie": "strona",
  "sygnal": {"zrodlo":"freshness.ostatni_wpis_dni","typ":"prog","kierunek":"powyzej","prog_krytyczny":365,"sev_krytyczny":6,"prog_sredni":120,"sev_sredni":3} }

{ "klasa": "martwy Instagram", "gdzie": "Instagram", "kategoria": "social",
  "sygnal": {"zrodlo":"social.instagram.days_since_last_post","typ":"prog","kierunek":"powyzej","prog_krytyczny":90,"sev_krytyczny":7,"prog_sredni":30,"sev_sredni":4} }

{ "klasa": "slaby engagement", "gdzie": "Instagram", "kategoria": "social",
  "sygnal": {"zrodlo":"social.instagram.engagement_rate","typ":"prog","kierunek":"ponizej","prog_krytyczny":0.01,"sev_krytyczny":5,"prog_sredni":0.02,"sev_sredni":3,"warunek_pole":"social.instagram.followers","warunek_min":500} }

{ "klasa": "zle opinie", "gdzie": "serwis opinii",
  "sygnal": {"zrodlo":"opinie.powtarzalny_zarzut","typ":"incydent","sev_incydent":6} }
```

Twarde zasady kompilacji:
- **`typ:"incydent"` MUSI mieć jawne `sev_incydent`.** Bez tego score policzy 0 (nie zgaduje 10) - i słusznie,
  bo inaczej byle „brak czatu" przebiłby SSL i został dominantem.
- **`kierunek` jawnie** przy każdym `prog`. „Powyżej progu = gorzej" (dni bez posta, braki kontaktu) to
  `powyzej`; „poniżej progu = gorzej" (wydajność, engagement) to `ponizej`. Pominięcie odwraca logikę.
- **`kategoria:"social"`** przy każdym wpisie social (score pomija je przy segmencie B2B).
- **Social tylko `instagram`** - kolektor (`apify_ig.py`) obsługuje IG. Facebook/LinkedIn nie mają kolektora
  metryk -> nie rób z nich wpisu score, wrzuć do `[do ręki]` w `Metoda prospectingu.md`.
- **Reklamy (biblioteka Meta) NIE są wpisem score.** „Ma reklamy" to sygnał BUDŻETU (pozytyw), nie wada,
  a „reklamy kierują na stronę główną" wymaga oceny okiem. To idzie do notatki jako kontekst/`[do ręki]`,
  nie do `Taksonomia.json`.
- **Nadpisania z `Metoda prospectingu.md`:** człowiek podał własny próg („martwe to 2 tygodnie") -> podstaw
  jego liczbę zamiast domyślnej. Fundament > domyślne.

Sygnału nie ma w bibliotece i nie umiesz go zmapować na sprawdzalne pole -> `[do ręki]`, NIE rób wpisu score.

## `Taksonomia.json` - złożenie

```json
{
  "klasy": [
    { "klasa": "wolna strona", "usluga": "<z Oferta.md>", "cena": "<z Oferta.md>", "gdzie": "Lighthouse",
      "priorytet": 1, "sygnal": { "...jak w bibliotece..." } }
  ]
}
```

- **`priorytet`** = kolejność usług w `Oferta.md` (1 = najważniejsza). Przy remisie severity wygrywa usługa,
  na której człowiekowi zależy.
- **`usluga`/`cena`** ZAWSZE z `Oferta.md`. Zero cen i nazw produktów na sztywno w tym pliku.

## `icp.json` (z `Grupa docelowa.md`)

```json
{
  "segment": "lokalna",
  "branze_glowne": ["dentysta", "stomatolog"],
  "branze_pokrewne": ["gabinet medyczny", "ortodonta"],
  "zasieg": "lokalny",
  "miasta": ["Poznań"],
  "wielkosc": ["mikro", "mała"],
  "wielkosc_sasiednia": ["średnia"],
  "dyskwalifikatory": ["sieciówka", "franczyza"],
  "social_relevant": true
}
```

- **`segment`** - twarda bramka: inny segment -> `gate=0`, score 0, nie audytuj.
- **`branze_glowne`** wprost z `Grupa docelowa.md`. **`branze_pokrewne`** - z pola „branże pokrewne", a jeśli
  go nie ma, wyprowadź 2-3 sąsiednie samodzielnie (np. dentysta -> ortodonta, gabinet medyczny) i pokaż je
  człowiekowi do potwierdzenia. Nie zostawiaj `[]` po cichu.
- **`wielkosc`** z pola „Wielkość". **`wielkosc_sasiednia`** wyprowadź z osi mikro <-> mała <-> średnia
  <-> duża (sąsiedni stopień), żeby firma o oczko większa/mniejsza nie dostawała 0 za wielkość.
- **`social_relevant`** = false dla segmentów, gdzie social nie jest kanałem (klasyczne B2B/produkcja).
  Lokalna usługa i e-commerce zwykle true, B2B często false. Wyciągnij z segmentu.
- **`dyskwalifikatory`** - trafienie po granicy słowa w polach tożsamości firmy -> `gate=0`.

## Po kompilacji

Pokaż człowiekowi jednym zdaniem, co wyszło („z Twojej oferty 3 klasy problemów, segment lokalna, social
liczymy, branże pokrewne: ortodonta/gabinet medyczny - ok?") i zapisz oba pliki.
