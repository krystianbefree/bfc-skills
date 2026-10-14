# Biblioteka skilli Be Free Club

Gotowe skille do Claude Code, które wgrywasz raz i używasz codziennie.

Różnica względem promptów, które krążą po internecie: te skille **najpierw pytają o Twoje dane**.
Jakie firmy szukasz, z jakich źródeł, co Cię w nich interesuje, ile bierzesz za robotę, jak wygląda
Twoja oferta, jakim tonem piszesz. Odpowiadasz raz, odpowiedzi lądują jako notatki w Twoim sejfie
Obsidian, a skill od tej pory pracuje pod Ciebie, nie pod jakiegoś abstrakcyjnego freelancera.

## Co jest w środku

| Skill | Co robi |
|---|---|
| `/bfc:start` | Wywiad startowy, status konfiguracji, zmiana ustawień |
| `/bfc:panel` | Stawia żywy panel operacyjny nad Twoim sejfem: pozyskiwanie, klienci, kasa, czas, archiwum efektów. Sam pilnuje statusu zadań z rozmowy |
| `/bfc:research` | Znajduje firmy pod Twój profil klienta i robi z nich notatki w sejfie |
| `/bfc:sygnaly` | Obserwuje wybrane firmy i mówi, która właśnie ma powód kupić (KRS, ogłoszenia, strona, opinie, reklamy, dotacje, zmiany pracy dawnych klientów) |
| `/bfc:oferta` | Pisze ofertę pod konkretnego klienta, z Twoim pricingiem i Twoimi dowodami |
| `/bfc:cold-mail` | Pisze pierwszą wiadomość i follow-upy oparte na tym, co research faktycznie znalazł |

## Czego potrzebujesz

- Claude Code (CLI, aplikacja desktopowa albo wtyczka do edytora)
- Sejf Obsidian (ten, który zakładasz w module o drugim mózgu). Jak nie masz, skille zrobią zwykły
  folder `~/BFC-Skille` i będą działać dalej.

Nie potrzebujesz konta GitHub, kluczy API ani niczego płatnego.

## Instalacja

W Claude Code wpisz po kolei:

```
/plugin marketplace add https://github.com/krystianbefree/bfc-skills.git
/plugin install bfc@befreeclub
```

Przy `install` Claude pokaże ekran z potwierdzeniem. Zatwierdź. Jeśli w podsumowaniu zobaczysz
`Run /reload-plugins to activate`, odpal `/reload-plugins`.

Na koniec:

```
/bfc:start
```

To uruchomi wywiad startowy. Zajmuje kilka minut i robisz go raz.

> Wpisz dokładnie ten adres z `https://` i `.git` na końcu. Skrócona forma `krystianbefree/bfc-skills`
> też istnieje, ale Claude Code próbuje przy niej pobierać repo przez SSH, więc bez skonfigurowanego
> klucza SSH dostaniesz błąd.

## Auto-update

Wejdź w `/plugin`, zakładka **Marketplaces**, znajdź `befreeclub` i włącz **Enable auto-update**.
Nowe skille i poprawki dojadą do Ciebie same przy kolejnym starcie Claude Code.

Ręcznie, kiedy chcesz sprawdzić od razu:

```
/plugin marketplace update
/plugin update bfc
```

## Jak to działa w praktyce

Nie musisz pamiętać żadnej komendy konfiguracyjnej. Piszesz normalnie, na przykład:

> zrób research firm pod moją usługę

Jeśli skill nie ma jeszcze Twoich danych, sam zada pytania, zapisze odpowiedzi i dopiero potem
zabierze się do roboty. Za drugim razem od razu leci do roboty.

Wszystkie Twoje odpowiedzi siedzą w sejfie w folderze `BFC Skille/`:

```
BFC Skille/
├── Profil.md              # kim jesteś, co sprzedajesz, dla kogo, jakim tonem
├── research/Config.md
├── oferta/Config.md
└── cold-mail/Config.md
```

To zwykłe notatki. Zmieniłeś pricing? Wchodzisz w `oferta/Config.md`, poprawiasz liczbę i tyle.
Żadnego wywiadu od nowa.

## Panel operacyjny (`/bfc:panel`)

Panel to żywe okno nad Twoim sejfem: pozyskiwanie klientów, obecni klienci, własny
biznes, kasa, czas pracy i archiwum gotowych efektów. Odpalasz `/bfc:panel`, a
Claude skanuje sejf, dopytuje o luki i stawia lokalny serwer (`http://127.0.0.1:8765`).

Najważniejsze: panel **sam pilnuje zadań**. Gdy razem z Claude robisz cennik,
ofertę czy scenariusz, na koniec Claude pyta, czy odhaczyć zadanie, i zapisuje
gotowy efekt do folderu `Outputy/` - żeby nie zginął w czacie i dało się go później
wkleić. Wszystko lokalnie, klucze API zostają na Twojej maszynie.

Działa na macOS, Linux i **Windows** (na Windowsie panel startuje `python solutions\panel.py`
albo dwuklik `panel.cmd`; zakładka Terminal jest tylko na macOS/Linux, reszta ta sama).
Serwer sam zakłada środowisko i doinstalowuje zależności przy pierwszym uruchomieniu.

## Sygnały (`/bfc:sygnaly`)

Prospecting na sygnałach: zamiast pisać do każdej firmy z listy, piszesz do tych, u których właśnie
coś się zmieniło. Przy pierwszym uruchomieniu krótki wywiad ustala, które zmiany są sygnałem dla
**Twojej** usługi (np. ogłoszenie o handlowca, które wraca, jest sygnałem dla kogoś od automatyzacji
obsługi zapytań, a szumem dla grafika).

- Firmy dodajesz ręcznie albo z `/bfc:research` - research sam zaproponuje, które obserwować,
  i zapyta o zgodę.
- Skan odpalasz na komendę. Darmowe źródła (rejestr KRS z historią, strona firmy z sitemapą,
  narzędziami i ogłoszeniami w kodzie, archiwum strony) sprawdza skrypt i pokazuje tylko to, co się
  zmieniło. Domyślnie skan lekki (prawie zero tokenów), pełny raz na kilka tygodni.
- Sygnały widać od pierwszego skanu: skrypt sięga w historię KRS i w archiwum strony.
- Tryb szukaj znajduje nowe firmy, które mają sygnał teraz (np. kto w Twoim mieście szuka handlowca).
- Skill uczy się, które sygnały dają Ci odpowiedzi, i sam przestawia wagi.
- Byli klienci w nowych firmach: raz w miesiącu wrzucasz eksport kontaktów z LinkedIna, skill wyłapuje
  zmiany pracy w całej sieci, bez scrapowania.
- Firmy z sygnałem trafiają do lejka w `/bfc:panel` i do zakładki Dziś.
- Co 90 dni skill pokazuje firmy, które milczą, i decydujesz: obserwować dalej czy napisać
  zwykłą wiadomość bez sygnału.
- Opcjonalnie: klucz Apify (opinie Google, Instagram, płatne grosze) i token Meta Ad Library
  (reklamy). Bez nich skill działa na darmowych źródłach. Klucze wpisujesz do pliku `.env`,
  nigdy do czatu.

## Jak działać lepiej (opcjonalnie)

Skille działają na wbudowanym wyszukiwaniu Claude Code i to wystarcza. Jeśli masz klucz Firecrawl
(`FIRECRAWL_API_KEY` w zmiennych środowiskowych albo w pliku `.env` w projekcie), research automatycznie
przełączy się na głębszą ścieżkę: więcej stron, pełna treść, mniej zgadywania. Sam to wykryje,
nic nie musisz przestawiać.

## Coś nie działa

**`/plugin marketplace add` wywala błąd.** Sprawdź, czy wkleiłeś pełny adres z `https://` i `.git`.

**Skill nie odpala się sam.** Wywołaj go wprost: `/bfc:research`, `/bfc:oferta`, `/bfc:cold-mail`.

**Skill pyta o rzeczy, na które już odpowiadałeś.** Odpal `/bfc:start` i wybierz status.
Pokaże, gdzie leżą Twoje konfigi i czy któryś ma nieuzupełnione pola.

**Chcę zacząć konfigurację od zera.** `/bfc:start`, opcja resetu. Stare notatki zostaną w sejfie,
nic nie znika bezpowrotnie.

## Odinstalowanie

```
/plugin uninstall bfc
/plugin marketplace remove befreeclub
```

Twoje notatki w sejfie zostają.

## Licencja

MIT. Rób z tym, co chcesz.
