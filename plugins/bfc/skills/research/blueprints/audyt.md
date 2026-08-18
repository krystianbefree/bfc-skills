# Audyt firmy - zbieranie surowych sygnałów

Cel: dla jednej firmy zebrać **goły kolektor** `raw-signals.json` - same odczyty, zero
klasyfikacji. Decyzję „co z tego jest problemem i jak mocnym" podejmuje potem `solutions/score.py`.
Ty tu tylko mierzysz.

**Sterujesz się Taksonomią.** Odpalasz TYLKO te sondy, których `zrodlo` występuje w `Taksonomia.json`.
Nikt nie sprzedaje wszystkiego - jak w ofercie nie ma nic o social, nie ruszasz Instagrama. To realizuje
regułę „metoda człowieka steruje kolektorem", nie odwrotnie.

**Cross-platform.** Zero skryptów bash w ścieżce krytycznej (padają na Windows). Sondy przez narzędzia,
które Claude woła identycznie na macOS i Windows: Playwright (MCP albo CLI), Lighthouse (chrome-devtools
`lighthouse_audit`), Firecrawl (`firecrawl-scrape`/`firecrawl-search`), Apify (`solutions/apify_ig.py`).
Brak narzędzia nigdy nie blokuje ani nie zmyśla - patrz „Degradacja".

## Kształt `raw-signals.json` (kontrakt ze `score.py`)

Zapisuj do `<folder_wynikow>/.audit/<firma>/raw-signals.json`. Wypełniaj tylko pola potrzebne wg Taksonomii.

```json
{
  "name": "Gabinet Uśmiech", "url": "https://usmiech.pl",
  "segment": "lokalna", "branza": "dentysta", "miasto": "Poznań", "wielkosc": "mikro",
  "domena_martwa": false, "http_status": 200, "http_5xx": false, "ssl_error": false,
  "lighthouse": { "performance": 34, "seo": 78, "accessibility": 82, "best_practices": 90 },
  "kontakt": { "email": true, "telefon": false, "formularz": 0 },
  "kontakt_braki": 2,
  "livechat": false, "livechat_brak": true,
  "freshness": { "ostatni_wpis_dni": 420, "stopka_rok": 2021 },
  "social": { "instagram": { "followers": 1200, "days_since_last_post": 95, "engagement_rate": 0.008 } },
  "reklamy": { "meta_aktywne": true, "liczba": 8 },
  "opinie": { "powtarzalny_zarzut": "nie odbierają telefonu" },
  "do_reki": ["reklamy: biblioteka Meta zablokowała automat - sprawdź ręcznie"]
}
```

Pola `segment/branza/miasto/wielkosc` przenieś z `_prospekty.json` z discovery (Krok 2). `kontakt_braki`
i `livechat_brak` **ty liczysz** z surowych checków (żeby score tylko progował liczbę).

## Sondy (odpalaj wg Taksonomii)

1. **HTTP / SSL / domena** (Firecrawl `scrape` albo `WebFetch`). Pobranie się nie udaje z błędem
   certyfikatu -> `ssl_error: true`. Brak DNS / domena nie istnieje -> `domena_martwa: true`. Kod 5xx
   -> `http_5xx: true`. **Incydent twardy:** `domena_martwa` albo trwałe 5xx -> zapisz minimalny
   `raw-signals` (te flagi) i **przerwij audyt tej firmy** - reszta sond bez sensu.
2. **Lighthouse** (chrome-devtools `lighthouse_audit` na URL) -> `performance/seo/accessibility/best_practices`
   (0-100). Narzędzia brak -> pola `null`, dopisz do `do_reki`. Nie licz perf „na oko".
3. **Kontakt** (Playwright `browser_navigate` na `/kontakt`, potem homepage, `browser_evaluate`):
   policz formularze (odfiltruj wyszukiwarkę i newsletter), znajdź email (regex) i telefon PL
   (`(?:\+48)?\s?\d{3}\s?\d{3}\s?\d{3}`). `kontakt.telefon/email/formularz` -> policz
   `kontakt_braki` = ile brakuje z {telefon, formularz>0, email}.
4. **Live-chat** (Playwright `browser_evaluate`: sprawdź `window.*` dla 13 vendorów - Intercom, Tawk,
   Tidio, Smartsupp, Crisp, LiveChat, Zendesk, Drift, Freshchat, HubSpot, Chatra, Gorgias, Userlike;
   albo w HTML z Firecrawl poszukaj tych nazw). Brak -> `livechat: false, livechat_brak: true`.
5. **Świeżość** (`freshness`): rok w stopce, data ostatniego wpisu na blogu/aktualnościach. Liczysz dni.
6. **Social** (tylko gdy Taksonomia ma wpis social i segment go nie wyłącza): Playwright/Firecrawl skanuje
   `<a>` na homepage -> handles IG/FB/LinkedIn. **Filtr złych handli:** odrzuć `sharer`, `share`, `tr?`,
   `plugins`, puste. Potem metryki (uruchom `python3` -> `python` -> `py -3`, pełną ścieżką):
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/research/solutions/apify_ig.py" <handle>` -> `followers`,
   `days_since_last_post`, `engagement_rate`. Skrypt sam skipuje bez tokenu i przy dziwnej odpowiedzi.
   Kolektor metryk działa tylko dla **Instagrama**. Facebook/LinkedIn -> handles zapisz, metryki `[do ręki]`.
7. **Reklamy** (`reklamy`): biblioteka reklam Meta (`facebook.com/ads/library`). Zwykle blokuje automat ->
   szukaj przez `WebSearch` „<firma> ads library" albo Firecrawl; nie masz pewności -> `do_reki`.
8. **Opinie** (`opinie.powtarzalny_zarzut`): z serwisu opinii dobranego pod segment (patrz `blueprints/zrodla.md`).
   Interesują Cię **powtarzalne** zarzuty operacyjne, nie pojedyncza zła opinia. Nigdy nie cytuj opinii w mailu.

## Degradacja (twarda zasada z `wspolne/narzedzia.md`)

Brak narzędzia = sygnał ląduje jako `[do ręki]`, nie jako zmyślona liczba i nie jako blokada.

- Brak Firecrawl -> `WebFetch`/`WebSearch`; strona JS pusta -> pole `= "[do ręki]"`, dopisek w `do_reki`.
- Brak Apify / `APIFY_TOKEN` -> handles zapisane (z Playwright), metryki `= "[do ręki]"`; klasa social
  nie liczy severity (score potraktuje brak jako 0), za to wpada do sekcji `[Do ręki]` w notatce.
- Brak Playwright -> screenshoty pomiń; **kontakt (sonda 3), świeżość (5) i live-chat (4) licz z HTML**
  (Firecrawl/WebFetch, tymi samymi regexami na email/telefon/vendorów); czego nie da się wyczytać -> `[do ręki]`.
- Brak Lighthouse -> `performance = "[do ręki]"`. Nie fabrykuj liczby.

**Score liczy się z tego, co jest.** Brakujący sygnał = severity 0 (nie kara). Firma nie dostaje niższego
score za to, że Ty nie miałeś narzędzia - dostaje uczciwą notkę „sprawdź to ręcznie".

## Screenshoty (opcjonalnie, dla człowieka)

Jeśli Playwright dostępny, zrób screenshot desktop i mobile (Playwright `browser_take_screenshot`,
viewport 1920x1080 i 375x667). To nie wchodzi do score - to dowód wzrokowy do notatki, żeby człowiek
zobaczył, o czym mówi mail, zanim go wyśle.
