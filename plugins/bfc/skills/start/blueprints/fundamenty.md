# Fundamenty - notatki, które produkuje wywiad

`/bfc:start` nie kończy się na `Profil.md`. Głęboki wywiad produkuje **pięć notatek-fundamentów** w `<sejf>/BFC Skille/`. To z nich research, cold-mail i oferta stają się realne, a nie generyczne. Każda notatka to zwykły Markdown - człowiek może ją potem poprawić ręcznie.

Zasada zapisu: wypełniaj **tylko tym, co wyszło z wywiadu**. Czego nie ustaliłeś, zostaw jako `TODO:` z opisem, czego brakuje - nigdy nie zmyślaj, żeby notatka wyglądała na pełną. Puste pole jest uczciwe, zmyślone jest groźne (poleci do klienta).

Kto co czyta:

| Notatka | Czyta ją |
|---|---|
| `Profil.md` | wszystkie skille (ton, dowody, czerwone linie) |
| `Oferta.md` | oferta, cold-mail (co proponujesz + cena) |
| `Grupa docelowa.md` | research (kogo szukać + gdzie opinie) |
| `Metoda prospectingu.md` | research (jak audytować + po jakim sygnale) |
| `Dowody.md` | oferta, cold-mail (czym się podeprzeć) |
| `Głos.md` | cold-mail (żeby brzmiało jak człowiek, nie jak AI) |

---

## Oferta.md

```markdown
---
utworzone: {{DATA}}
skill: bfc/start
---

# Oferta

## Co sprzedaję
Jedna, dwie usługi, które faktycznie sprzedajesz. Nie lista wszystkiego, co umiesz.
- <usługa 1>: <co klient dostaje, co się u niego zmienia - jednym zdaniem>
- <usługa 2>: ...

## Model wyceny
Jeden z: pakiety | wycena per projekt | godzinowo. (Rozgałęzienie z wywiadu.)

### Pakiety (jeśli tak wyceniasz)
- <pakiet A> - <cena> - <dla kogo / co zawiera>
- <pakiet B> - <cena>

### Widełki per projekt (jeśli wyceniasz indywidualnie)
- <typ projektu 1>: <od X do Y zł> (z ostatnich realizacji)
- <typ projektu 2>: <widełki>
Regula: w ofercie i mailu podajemy widełki uczciwie („takie projekty robię w przedziale X-Y, dokładna wycena po rozmowie"), nie udajemy sztywnej ceny.

### Godzinowo (jeśli tak)
- Stawka: <X zł/h>. Typowy projekt: <ile godzin>.

Waluta i netto/brutto: <PLN, netto> (żeby oferta nie zgadywała).

## Problem, który rozwiązuję -> usługa
To jest paliwo dla researchu i pierwszego zdania maila. Dla każdej usługi:
- **Usługa <X>** rozwiązuje: <konkretny problem klienta>.
  - Widać go z zewnątrz po: <sygnał, który AI/człowiek może sprawdzić - np. „reklamy kierują na stronę główną", „brak formularza kontaktowego", „martwe konto na IG">.
  - Gdzie to sprawdzić: <biblioteka reklam Meta / strona / opinie / social>.
```

---

## Grupa docelowa.md

```markdown
---
utworzone: {{DATA}}
skill: bfc/start
---

# Grupa docelowa

## Kogo szukam
- Branża / typ firmy: <konkretnie, np. gabinety stomatologiczne, sklepy e-commerce z suplementami>
- Branże pokrewne: <2-3 sąsiednie, np. ortodonta, gabinet medyczny - te też bierzesz, ze słabszym dopasowaniem>
- Wielkość: <mikro / mała / średnia - i po czym to poznajesz>
- Miasto / zasięg: <lokalnie X / cała Polska / online>
- Segment: <lokalna usługa | e-commerce | B2B> (decyduje, gdzie szukać opinii)

## Kogo NIE chcę (dyskwalifikatory)
- <np. sieciówki z centralnym marketingiem, firmy bez budżetu, branże, których nie tykasz>

## Gdzie szukać opinii o takich firmach
Zależy od segmentu. Ustalone w wywiadzie, potwierdzone na żywo na 1 przykładzie:
- <segment> -> <serwis 1>, <serwis 2>
Domyślne wg segmentu (do potwierdzenia z człowiekiem):
- lokalna usługa -> Google Maps, gowork.pl
- beauty / uroda -> booksy.com, Google Maps
- medycyna -> znanylekarz.pl
- e-commerce -> opineo.pl, ceneo.pl, Allegro, Empik (wg kategorii)
- B2B / produkcja -> aleo.com, panoramafirm.pl, LinkedIn
```

---

## Metoda prospectingu.md

```markdown
---
utworzone: {{DATA}}
skill: bfc/start
---

# Jak weryfikuję prospekta

Odtworzona metoda człowieka - to research ma WYKONAĆ, nie zgadywać. Każdy punkt
przeszedł przez pętlę drążenia (co dokładnie / gdzie / po jakim sygnale) i został
sprawdzony na żywo na 1 firmie. Punkty, których AI nie umie złapać automatem, są
oznaczone `[do ręki]`.

## Czego szukam u dobrej firmy (sygnały, że warto)
- <sygnał 1> - widać po: <co konkretnie> - sprawdzam w: <gdzie> - AI umie: <tak / [do ręki]> - (opcjonalnie) próg: <jeśli Twój jest inny niż domyślny, np. „martwe konto = 14 dni bez posta">

Reklamy i to, „dokąd kierują" (np. na stronę główną zamiast landing), zostaw jako `[do ręki]` -
„ma reklamy" to sygnał budżetu, a ocena jakości reklamy wymaga oka, nie automatu.

## Co ją dyskwalifikuje
- <sygnał czerwony> - widać po: ...

## Po czym poznaję, że mają problem, który rozwiązuję
- <problem> -> obserwowalny sygnał: <co> -> gdzie sprawdzić: <serwis/strona>

## Czego AI nie złapie sama (zostaw człowiekowi)
- <rzecz, którą freelancer robi okiem / z doświadczenia>
```

---

## Dowody.md

```markdown
---
utworzone: {{DATA}}
skill: bfc/start
---

# Dowody

Czym podpierasz się w ofercie i mailu. Tylko rzeczy, które FAKTYCZNIE masz.
Brak dowodów nie jest katastrofą - wtedy stoimy na procesie i gwarancji.

## Realizacje / case studies
Format problem -> co zrobiłem -> efekt (z liczbą, jeśli jest):
- <klient/branża>: <problem> -> <co zrobiłeś> -> <efekt: liczba albo konkret>. Widełki: <ile to było za projekt>.

## Portfolio / linki
- <link do strony / realizacji, który można pokazać klientowi>

## Co mogę obiecać (uczciwie)
- <rzeczy, które realnie dowozisz - bez zmyślonych procentów>

## Czego NIE obiecuję (czerwone linie)
- <z Profil.md - bezpiecznik>
```

---

## Głos.md

Szczegóły ekstrakcji: `blueprints/glos.md`. Kształt notatki:

```markdown
---
utworzone: {{DATA}}
skill: bfc/start
zrodlo_glosu: probki | swieze-pisanie | kalibracja
---

# Głos

## Próbki (surowe, do wglądu)
Wklejone maile/teksty człowieka. To jest kanon - z tego uczymy się stylu.
- <próbka 1>
- <próbka 2>

## Wzorzec stylu (wyciągnięty z próbek)
- Forma: <Ty / Pan>
- Długość: <krótko / średnio> - typowo <ile zdań>
- Otwarcie: <od pytania / od obserwacji o nich / od konkretu>
- Rytm: <krótkie zdania / dłuższe> - <charakterystyczne dla niego>
- Zwroty, których używa: <cytaty z próbek>
- Emoji: <tak / nie>, humor: <tak / nie>
- Podpis: <jak podpisuje>
- Czego NIE robi: <czego w jego mailach nie ma - np. nie tłumaczy się, nie sprzedaje w pierwszej wiadomości>

## Reguły z pętli uczenia
Rośnie w czasie. Dopisywane przez cold-mail, gdy człowiek poprawia maile i potwierdza, że to reguła na przyszłość.
- (na razie pusto - zapełni się przy pisaniu)
```
