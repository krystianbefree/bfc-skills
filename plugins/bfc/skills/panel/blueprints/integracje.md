# Integracje - co podłączyć, żeby panel robił więcej za Ciebie

Panel działa bez żadnej integracji i to jest ważne - nikogo nie blokujemy. Ale to
właśnie podłączenia zamieniają go z tablicy, którą klepiesz ręcznie, w coś, co żyje
samo. Ten krok jest **aktywny i pozytywny**: nie „brakuje Ci X", tylko „podłącz X,
a panel zacznie sam robić Y". Robisz go raz, po zbudowaniu panelu. Bez wracania co chwilę.

## Rdzeń - zaproponuj zawsze (te trzy)

Dla każdego: co odblokowuje (konkret w panelu) + jak podłączyć + że jest opcjonalne.

### 1. Stripe (bramka płatnicza)
- **Odblokowuje:** zakładka Kasa pokazuje **realny przychód na żywo** zamiast szacunku ze stawek. Widać wpłaty i subskrypcje.
- **Jak:** wygeneruj klucz **tylko do odczytu** (restricted key) w panelu Stripe, wklej do pliku `.env` w projekcie jako `STRIPE_API_KEY=...`, w configu ustaw `sources.kasa.zrodlo: stripe`. Klucz zostaje na serwerze - panel go używa, nigdy nie pokazuje.
- **Bez tego:** Kasa leci w trybie ręcznym (wpisujesz kwoty albo szacunek ze stawek).

### 2. Gmail (poczta)
- **Odblokowuje:** `/bfc:panel sync` wciąga **wysłane oferty i odpowiedzi prospektów prosto do lejka**. Zero przepisywania.
- **Jak:** to konektor claude.ai - autoryzujesz go raz w ustawieniach konektorów na swoim koncie claude.ai. Panel pokaże go w zakładce Połączenia jako „podpięty".
- **Bez tego:** lejek prowadzisz z rozmowy (Claude i tak dopisuje fakty).

### 3. Google Calendar
- **Odblokowuje:** spotkania z klientami same ustawiają „ostatni kontakt" i lądują w zakładce Kalendarz.
- **Jak:** konektor claude.ai, tak samo jak Gmail.
- **Bez tego:** kalendarz liczy się z terminów w notatkach.

## Kontekstowo - dopytaj o to, co ma TEN człowiek

Rdzeń to trzy powyżej. Ale jeśli w rozmowie albo w skanie sejfu wyszło narzędzie,
w którym człowiek trzyma **dane o kliencie** albo **komunikację z nim**, dopytaj o nie
osobno - nie zgaduj, pytaj o to, co realnie u niego widać:

- **Notion / Airtable / arkusze** - jeśli trzyma tam klientów, CRM albo projekty -> zapytaj, czy podpiąć (Notion to konektor claude.ai). Uczciwie: pełny import z Notion **prosto do panelu** to robota do dołożenia; na start Claude potrafi z tego czytać w rozmowie i przepisywać do plików panelu.
- **Slack / Discord** - jeśli gada tam z klientami -> zapytaj, czy warto podpiąć (Slack = konektor claude.ai), żeby Claude miał kontekst rozmów.
- **Fakturownia / inna bramka** - jeśli nie używa Stripe, a fakturuje inaczej -> Kasa ma tryb `faktury` (plik ledgera) albo inne API.

Na koniec **zawsze jedno otwarte pytanie**:

> Jest jeszcze coś, z czego korzystasz na co dzień - miejsce, gdzie trzymasz klientów albo gdzie z nimi gadasz - co warto podpiąć?

## Jak pytać (mechanika)

- **Jeden krok**, pozytywna rama. `AskUserQuestion`: dla każdej z trzech „podpiąć teraz / później", plus miejsce na inne z kontekstu.
- **„Później"** = zapisz jako niepodłączone i nie wracaj co chwilę. Zakładka Połączenia i tak pokazuje status na żywo - człowiek dopnie, kiedy zechce.
- **Klucze i tokeny NIGDY w czacie.** Stripe -> człowiek sam wkleja do `.env`. Gmail / Kalendarz / Notion / Slack -> autoryzuje jako konektor na swoim koncie, nie podaje tokenu Tobie. Ty najwyżej mówisz, gdzie kliknąć.

## Po podłączeniu - jak panel to widzi

Zakładka Połączenia sprawdza na żywo, więc nie trzeba nic potwierdzać ręcznie:
- **klucze `.env`** (Stripe) - lekki, tylko-odczytujący strzał do API. Działa -> „aktywny".
- **konektory claude.ai** (Gmail, Kalendarz, Notion, Slack) - z `~/.claude.json`. Podpięty -> „podpięty"; jeśli prosi o logowanie -> „wymaga logowania", autoryzuj w ustawieniach konektorów.

## Bezpieczeństwo (twarde)

- Klucze API tylko w `.env` po stronie serwera. Nigdy w sejfie, w czacie, w przeglądarce.
- Panel pokazuje **status** połączenia (działa / nie działa), nigdy wartość klucza.
- Konektory claude.ai autoryzujesz na swoim koncie - Claude ich nie „zakłada" za Ciebie, tylko prowadzi i sprawdza, czy widać, że są.
