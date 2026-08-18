# Lifecycle zadań - Claude sam pilnuje statusu i archiwizuje efekty

To jest warstwa, przez którą panel przestaje być tablicą do ręcznego klikania, a
staje się czymś, co żyje razem z rozmową. Człowiek i tak pracuje z Claude. Kiedy
ta praca **jest** robieniem zadania z panelu, Claude to widzi, na koniec pyta o
status, a gotowy efekt zapisuje jako notatkę, żeby nie zginął w czacie.

Reguły niżej działają w **każdej** rozmowie (są wpisane do `CLAUDE.md` projektu),
nie tylko po wywołaniu `/bfc:panel`. Uzupełniają [write-back.md](write-back.md):
tamten dopisuje **fakty** (oferta wysłana, płatność), ten prowadzi **zadania od
początku do końca** i archiwizuje ich **efekty**.

## 1. Kiedy „pracujemy nad zadaniem"

Uznaj, że robicie zadanie z panelu, gdy w rozmowie powstaje **samodzielny
deliverable** i pasuje on do otwartego `- [ ]` u klienta albo w Biznesie.

Deliverable to np.: cennik/wycena, oferta, skrypt rolki, post, artykuł,
newsletter, scenariusz automatyzacji (Make/n8n), cold mail, sekwencja follow-up,
strategia, plan, brief, opis usługi, landing.

- **Pasuje do otwartego zadania** (znaczeniowo, nie co do słowa: „stwórz cennik"
  ≈ „rozpisać 3 pakiety cenowe") -> trzymaj z tyłu głowy: *pracujemy nad tym
  zadaniem*. Nie ogłaszaj tego, po prostu wiedz.
- **Nie ma takiego zadania**, ale efekt jest konkretny i biznesowy -> na koniec
  zaproponuj dopięcie: „To był konkret. Dopiąć jako zrobione zadanie u <klient> i
  zapisać do archiwum?".

Co **nie** jest zadaniem: krótka odpowiedź, burza mózgów, notatka z researchu,
wersja robocza w trakcie iteracji. Nie archiwizuj tego z automatu.

Żeby wiedzieć, jakie zadania są otwarte, zerknij do plików źródłowych (sekcje
`## Do zrobienia` w `Klienci/*.md` i `Biznes/*.md`) albo do lejka. Nie zgaduj z
pamięci sprzed wielu tur.

## 2. Zamknięcie zadania - ZAWSZE pytaj o status

Gdy deliverable jest **gotowy i zaakceptowany** (człowiek mówi „spoko / dawaj /
to jest to", przechodzi dalej), zatrzymaj się i zadaj **jedno** pytanie. Za
każdym razem, nigdy z automatu „zrobione":

> Zadanie »<nazwa zadania>« - jaki status? **zrobione** / **w toku** / **zostaw**.
> Jak zrobione, zapiszę efekt do `Outputy/<typ>/` i odhaczę zadanie.

Nie pytaj w środku iteracji. Pytasz, kiedy realnie jest co zamykać.

## 3. Na „zrobione" - dwie rzeczy naraz

**a) Zapisz efekt do archiwum.** Nowy plik w `Outputy/<typ>/`:

Ścieżka: `Outputy/<Typ>/RRRR-MM-DD Tytuł.md` (data dzisiejsza, tytuł krótki, z
klientem jeśli dotyczy). Typ z tabeli:

| Deliverable | Folder |
|---|---|
| cennik, wycena, kalkulacja stawki | `Wyceny` |
| oferta, propozycja współpracy | `Oferty` |
| skrypt rolki, post, artykuł, newsletter | `Treści` |
| scenariusz automatyzacji, opis procesu | `Scenariusze` |
| cold mail, follow-up, sekwencja | `Maile` |
| strategia, plan, brief | `Strategie` |
| cokolwiek innego | `Inne` |

Zawartość pliku - **frontmatter + czysty deliverable**, nic więcej. Bez „oto Twój
cennik", bez komentarzy Claude'a. Ma się wklejać jednym ruchem:

```markdown
---
typ: wycena
zadanie: "rozpisać 3 pakiety cenowe"
klient: Salon Uroda
data: 2026-08-18
zrodlo: Klienci/Salon Uroda.md
---

# Cennik - Salon Uroda

<sam cennik, gotowy do wysłania>
```

Dla pracy nad własnym biznesem zamiast `klient:` daj `projekt:`.

**b) Odhacz zadanie i podepnij link.** W pliku źródłowym (`zrodlo`) zmień
**dokładnie jedną linię**: `- [ ]` -> `- [x]` i dopisz odnośnik do efektu:

```
- [x] rozpisać 3 pakiety cenowe (output: [[Outputy/Wyceny/2026-08-18 Cennik - Salon Uroda]])
```

Panel odświeży się sam - zadanie znika z otwartych, efekt pojawia się w zakładce
**Archiwum**.

**c) Zaraportuj jedną linią:**
> Zrobione. Efekt: `Outputy/Wyceny/2026-08-18 Cennik - Salon Uroda.md`. Odhaczyłem zadanie w `Klienci/Salon Uroda.md`.

## 4. Na „w toku" / „zostaw"

- **w toku** - zostaw `- [ ]`. Nie archiwizuj. Możesz dopisać krótką notkę w
  `## Do zrobienia`, co jeszcze zostało. Efekt zapiszesz, jak domkniecie.
- **zostaw** - nie ruszaj niczego.

## 5. Człowiek zamyka sam

- „skończyłem X" / „zrobione X" -> odhacz zadanie w pliku. Jeśli efekt powstał w
  tej rozmowie, zapisz go do `Outputy/` jak w punkcie 3. Jeśli zrobił to poza
  czatem, tylko odhacz (nie ma czego archiwizować, nie wymyślaj treści).
- Odhaczył/przeciągnął w panelu -> panel już zapisał status do pliku, nie
  dubluj. Zadziałaj tylko, gdy mówi to Tobie.

## 6. Podawanie efektu z archiwum

Gdy pada „gdzie jest cennik dla Salonu", „wklej mi tamtą ofertę", „podeślij ten
scenariusz":

1. Przejrzyj `Outputy/` (po nazwie klienta/typu/dacie).
2. Jest jeden trafny -> wczytaj i **wklej treść** albo podaj ścieżkę, jak woli.
3. Jest kilka -> wypisz krótko (typ, klient, data) i spytaj który.
4. Nie ma -> powiedz wprost, zaproponuj zrobienie od nowa.

## Zasada zaufania (twarde)

- **Zawsze pytaj o status przy zamknięciu.** Nigdy nie odhaczaj sam z siebie.
- **Jedna zmieniona linia na jeden fakt.** Nie przepisujesz pliku klienta.
- **Nie zmyślaj.** Nie wiesz, do którego zadania pasuje efekt -> dopytaj. Nie ma
  liczby -> „brak danych", nie zero.
- **Efekt = czysty tekst do wklejenia.** W pliku archiwum ląduje sam deliverable.
- **Nie archiwizuj hipotez ani wersji roboczych** bez zgody człowieka.
- Po polsku, na „Ty". **Zero em-dashów** (`—` -> `-`). Zero fraz z `jakosc-pl.md`.
