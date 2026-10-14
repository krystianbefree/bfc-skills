# Sejf - gdzie mieszkają dane użytkownika

Ten plik czyta każdy skill BFC w Kroku 0. Ustala jedno: **gdzie zapisywać i skąd czytać**.

## Zasada

Katalog pluginu (`${CLAUDE_PLUGIN_ROOT}`) jest kasowany przy każdej aktualizacji.
Nigdy nie zapisujemy tam niczego. Dane użytkownika trzymamy w dwóch miejscach:

| Co | Gdzie | Dlaczego tam |
|---|---|---|
| Wskaźnik na sejf | `${CLAUDE_PLUGIN_DATA}/sejf.txt` | Przeżywa aktualizacje pluginu |
| Wszystko inne | `<sejf>/BFC Skille/` | Widoczne i edytowalne w Obsidianie |

`sejf.txt` to jedna linia: bezwzględna ścieżka do katalogu sejfu. Nic więcej.

## Ustalanie ścieżki sejfu

1. **Przeczytaj `${CLAUDE_PLUGIN_DATA}/sejf.txt`.**
   Plik istnieje, a ścieżka w nim wskazuje na istniejący katalog -> gotowe, używaj jej.
   Nie pytaj o nic więcej.

2. **Plik nie istnieje albo ścieżka jest nieaktualna** -> wykryj sejfy:

   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-sejf.py"
   ```

   Na Windows nie ma `python3` - uruchom łańcuchem `python3` -> `python` -> `py -3` (patrz `narzedzia.md`).

   - **Jeden wynik** -> pokaż go i poproś o potwierdzenie jednym pytaniem
     (`AskUserQuestion`, opcje: "Tak, ten" / "Chcę inny").
   - **Kilka wyników** -> `AskUserQuestion` z listą wykrytych sejfów jako opcjami.
     W `description` każdej opcji podaj pełną ścieżkę.
   - **Zero wyników** -> zapytaj, czy użytkownik ma Obsidiana:
     - ma, ale nie wykryło -> poproś o wklejenie ścieżki do katalogu sejfu
     - nie ma -> użyj `~/BFC-Skille`, powiedz o tym jednym zdaniem i **leć dalej**.
       Brak Obsidiana nie może zatrzymać roboty.

3. **Zapisz wynik**: utwórz katalog `${CLAUDE_PLUGIN_DATA}` jeśli nie istnieje (`mkdir -p`),
   wpisz ścieżkę do `sejf.txt`.

4. **Załóż strukturę** (`mkdir -p`), jeśli jej nie ma:

   ```
   <sejf>/BFC Skille/
   ```

Ścieżki z polskimi znakami i spacjami są normą. W komendach powłoki **zawsze** cytuj ścieżki.

## Struktura w sejfie

```
<sejf>/BFC Skille/
├── Profil.md                  # wspólny profil, wypełniany raz
├── research/
│   ├── Config.md
│   └── <wyniki: notatki o firmach>
├── oferta/
│   ├── Config.md
│   └── <wyniki: oferty>
├── cold-mail/
│   ├── Config.md
│   └── <wyniki: wiadomości i sekwencje>
└── sygnaly/
    ├── Config.md
    ├── Mapa sygnałów.md         # jakich sygnałów szukasz i co znaczą dla Twojej usługi
    ├── Obserwowane.md           # widok listy, generuje skrypt
    ├── Raport sygnałów <data>.md
    ├── obserwowane.json         # lista, historia sygnałów, wyniki wiadomości (prowadzi skrypt)
    ├── ustawienia.json          # ustawienia z Config.md dla skryptu
    ├── linkedin/                # tu człowiek wrzuca eksport Connections.csv
    ├── stan/                    # ostatni odczyt każdej firmy (do wykrywania zmian)
    └── .kopie/                  # kopie lejka panelu przed dopisaniem firm z sygnałem
```

Katalog skilla zakładaj dopiero wtedy, gdy dany skill jest pierwszy raz używany.
Nie zaśmiecaj sejfu pustymi folderami na zapas.

## Czytanie kontekstu z sejfu

Sejf to drugi mózg użytkownika, nie tylko magazyn na configi. Zanim zapytasz człowieka o coś,
co może już mieć zapisane, **poszukaj w sejfie**:

- Piszesz ofertę dla firmy X -> najpierw `grep -ril "X" "<sejf>"` i przeczytaj trafienia.
  Notatka po rozmowie, notatka z researchu, stary mail. To jest kontekst, którego nie da
  żadne pytanie.
- Potrzebujesz dowodów (case study, liczby, referencje) -> szukaj w sejfie, zanim poprosisz
  o wklejenie.
- Znalazłeś coś istotnego -> **pokaż to użytkownikowi i poproś o potwierdzenie**, nie zakładaj
  po cichu, że jest aktualne. Notatka sprzed roku może być nieprawdą.

Czego nie robimy: nie indeksujemy całego sejfu, nie czytamy wszystkiego "na wszelki wypadek",
nie zaglądamy do folderów, które wyglądają na prywatne (dziennik, finanse, zdrowie), chyba że
użytkownik sam na nie wskaże.

## Zapisywanie wyników

- Nazwa pliku: `<Nazwa Firmy> - <co to jest>.md`, czytelnie, bez sztucznych prefiksów z datą,
  chyba że użytkownik ustawił inaczej w swoim `Config.md`.
- Na górze każdej generowanej notatki frontmatter:

  ```yaml
  ---
  utworzone: RRRR-MM-DD
  skill: bfc/<nazwa-skilla>
  ---
  ```

- Plik już istnieje -> **nie nadpisuj po cichu**. Pokaż, co jest w środku, i zapytaj:
  nadpisać, dopisać na dole, czy zapisać obok pod nową nazwą.
- Linkuj wikilinkami do tego, co w sejfie faktycznie istnieje. Nie wymyślaj `[[linków]]`
  do notatek, których nie ma.
