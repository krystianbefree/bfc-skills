# Narzędzia - co jest dostępne i jak się zachować

Skille BFC mają działać u każdego od razu po instalacji. Dodatkowe narzędzia je pogłębiają,
ale **nigdy nie są warunkiem uruchomienia**.

## Wykrywanie

Uruchom raz, na początku skilla, który sięga do internetu:

```
bash "${CLAUDE_PLUGIN_ROOT}/wspolne/wykryj-narzedzia.sh"
```

Skrypt wypisuje jedną linię na narzędzie, w formacie `nazwa=tak|nie`, i nigdy nie kończy się błędem.

## Warstwy

### Warstwa podstawowa (zawsze dostępna)

`WebSearch` + `WebFetch`. Tego używasz domyślnie i to wystarcza do sensownego wyniku.

Ograniczenia, o których musisz pamiętać: `WebFetch` nie poradzi sobie ze stroną, która renderuje
treść JavaScriptem ani z niczym za logowaniem. Jak strona wraca pusta, nie kombinuj w kółko -
zapisz w notatce `nie udało się pobrać` z linkiem i idź dalej.

### Warstwa głęboka (gdy jest Firecrawl)

Wykryta, gdy `firecrawl=tak`. Wtedy zamiast `WebFetch` używaj skilla `firecrawl-scrape`
(albo `firecrawl-search` do wyszukiwania), bo radzi sobie ze stronami JS-owymi i zwraca czystszy
tekst. Reszta logiki skilla się nie zmienia.

Wykrywane po: kliencie `firecrawl` w `PATH` albo zmiennej `FIRECRAWL_API_KEY`
(w środowisku lub w pliku `.env` w katalogu projektu).

## Jak o tym mówić użytkownikowi

**Raz, jednym zdaniem, na końcu**, nie na początku i nie w kółko:

> Robiłem to na wbudowanym wyszukiwaniu. Z kluczem Firecrawl schodzę głębiej w strony,
> które ładują treść skryptami - jak będziesz chciał, pokażę, jak go podpiąć.

Czego nie robimy:

- Nie zaczynamy od informowania, czego nam brakuje. Człowiek przyszedł po wynik, nie po listę braków.
- Nie odmawiamy roboty z powodu braku klucza.
- Nie proponujemy płatnych narzędzi w kółko. Jedno zdanie, raz na sesję, koniec.

## Uruchamianie skryptów Pythona (cross-platform)

Komenda `python3` **nie istnieje na Windows** - instalator z python.org tworzy `python` i `py`.
Skrypty `.py` z paczki (`wykryj-sejf.py`, `wykryj-narzedzia.py`, `score.py`, `apify_ig.py`) uruchamiaj
**łańcuchem fallbacku**: spróbuj `python3`, potem `python`, potem `py -3` - pierwszy, który odpowie
na `--version`, jest tym właściwym. Skrypty adresuj **pełną ścieżką** (`${CLAUDE_PLUGIN_ROOT}/...`
albo `<sejf>/...`), nie względną - bo uruchamiają się z katalogu, w którym akurat jest człowiek.

## Pliki `.env`

Jeśli szukasz kluczy w `.env`, czytaj tylko te zmienne, których faktycznie potrzebujesz.
Nigdy nie wypisuj zawartości `.env` do odpowiedzi ani nie zapisuj kluczy w notatkach w sejfie.
