# Wywiad: research (tylko ustawienia przebiegu)

Profil klienta, segment, źródła, sygnały i metoda oceny **nie są tu pytane** - biorą się z fundamentu
z `/bfc:start` (`Grupa docelowa.md`, `Oferta.md`, `Metoda prospectingu.md`). Brak fundamentu -> odeślij
do `/bfc:start`, nie prowadź tu drugiego wywiadu profilowego.

Ten wywiad pyta tylko o to, co dotyczy jednego przebiegu. Mechanika: `${CLAUDE_PLUGIN_ROOT}/wspolne/onboarding.md`.
Szablon wyniku: `config.template.md` -> `<sejf>/BFC Skille/research/Config.md`.

---

### folder_wynikow | tekst | 1
**Pytanie:** W którym folderze sejfu mam zapisywać notatki o firmach?
**Po co:** Żeby wpadały tam, gdzie ich szukasz, a nie w osobny kąt.
**Wnioskuj z:** Poszukaj w sejfie folderu z „Klienci", „Prospekty", „Sprzedaż" albo „CRM" i zaproponuj go.
**Domyślnie:** BFC Skille/research
**Walidacja:** Ścieżka względem katalogu sejfu.

### ile_firm | liczba | 1
**Pytanie:** Ile firm mam sprawdzać w jednym przebiegu?
**Po co:** Każda firma to pełny audyt, więc więcej firm to dłuższe czekanie. Lepiej mniejsze tury i od razu pisać.
**Opcje:** 10 :: dobre na start i test segmentu | 15 :: pełna tura na dzień pracy | 5 :: mało firm, bardzo dokładnie
**Domyślnie:** 10
**Walidacja:** Liczba od 1 do 30. Powyżej 15 uprzedź, że potrwa.

### prog_score | liczba | 1
**Pytanie:** Od jakiego score firma jest warta zaczepienia?
**Po co:** Poniżej progu ląduje na dole listy jako słabszy lead. To Twój filtr „pisać czy odpuścić".
**Domyślnie:** 60
**Walidacja:** Liczba od 0 do 100.
