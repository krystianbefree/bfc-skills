<!-- BFC-PANEL:START - blok panelu, nie edytuj ręcznie; nadpisze go aktualizacja -->
## Panel operacyjny (Be Free Club)

Masz żywy panel na `http://127.0.0.1:{{PORT}}`. Źródłem prawdy są notatki Markdown
w sejfie: `{{SEJF}}`. Ty piszesz do plików, panel czyta pliki i odświeża się sam.
Te reguły działają w KAŻDEJ rozmowie, nie tylko po `/bfc:panel`.

**Zadania - pilnujesz ich sam:**

1. Gdy w rozmowie powstaje konkretny efekt (cennik, oferta, skrypt rolki, post,
   scenariusz automatyzacji, cold mail, strategia) i pasuje znaczeniowo do
   otwartego `- [ ]` w `Klienci/*.md` albo `Biznes/*.md` - wiedz, że pracujecie
   nad tym zadaniem. Otwarte zadania sprawdzasz w plikach, nie z pamięci.
2. Gdy efekt jest gotowy i zaakceptowany - **zawsze zapytaj o status** jednym
   pytaniem: `zrobione / w toku / zostaw`. Nigdy nie odhaczaj z automatu, nie pytaj
   w środku iteracji.
3. Na „zrobione" zrób dwie rzeczy:
   - Zapisz **sam efekt** (czysty tekst do wklejenia, bez komentarzy) do
     `Outputy/<Typ>/RRRR-MM-DD Tytuł.md` z frontmatterem `typ`, `zadanie`,
     `klient` lub `projekt`, `data`, `zrodlo`. Typy: `Wyceny`, `Oferty`, `Treści`,
     `Scenariusze`, `Maile`, `Strategie`, `Inne`.
   - W pliku zadania zmień **jedną linię** `- [ ]` -> `- [x]` i dopisz
     `(output: [[Outputy/...]])`.
   - Zaraportuj jedną linią: gdzie efekt i które zadanie odhaczone.
4. „skończyłem X" -> odhacz zadanie; jeśli efekt jest w rozmowie, zapisz do
   `Outputy/`; jeśli zrobił poza czatem, tylko odhacz (nie wymyślaj treści).
5. „gdzie jest / wklej mi <efekt>" -> znajdź w `Outputy/`, wklej treść albo podaj
   ścieżkę. Kilka trafień -> wypisz i spytaj który.

**Twarde:** zawsze pytaj o status przy zamknięciu; jedna zmieniona linia na fakt;
nie zmyślaj (nie wiesz, do czego pasuje - dopytaj); w archiwum ląduje sam
deliverable; po polsku, na „Ty", zero em-dashów (`—` -> `-`).
<!-- BFC-PANEL:END -->
