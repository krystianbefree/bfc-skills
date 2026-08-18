# Głos w mailu + pętla uczenia

To jest warstwa, która odróżnia ten skill od „ChatGPT napisz mi cold maila". Głos siedzi w `Głos.md` (fundament z `/bfc:start`), a każda poprawka człowieka dostraja go dalej. Anty-AI floor (`${CLAUDE_PLUGIN_ROOT}/wspolne/jakosc-pl.md`) jest podłogą dla wszystkich; głos jest odciskiem palca jednego człowieka na tej podłodze.

## Część 1 - jak nałożyć głos na maila

### Co czytasz z `Głos.md`

- **Wzorzec stylu:** forma (Ty / Pan), typowa długość, jak otwiera (pytanie / obserwacja / konkret), rytm (krótkie cięte zdania czy dłuższe), zwroty które POWTARZA (z cytatami), emoji tak/nie, humor tak/nie, jak podpisuje, i **czego NIE robi**.
- **Próbki** (jeśli są) - kanon. Jak masz wątpliwość „czy on by tak napisał", wracaj do próbek, nie do wzorca. Próbka bije opis.
- **`## Reguły z pętli uczenia`** - to, czego nauczył Cię przy poprzednich mailach. Traktuj każdą regułę jak twarde ograniczenie, na równi z czerwonymi liniami.

### Przełożenie surowego haczyka na głos

Notatka researchu daje **haczyk bez głosu** - sam fakt plus obserwacja, w neutralnym tonie. Twoja robota to ten sam fakt powiedzieć jego kadencją, nie przepisać jeden do jednego.

Przykład. Notatka daje:

> „Wasza strona ładuje się na telefonie w kilka sekund (Lighthouse: 34/100 wydajności) - przy płatnym ruchu to zwykle znaczy, że część kliknięć nie dochodzi do formularza."

Ten sam fakt, trzy różne głosy (z `Głos.md`):

- **Krótkie cięte zdania, otwiera pytaniem, forma Ty:** „Wchodziłeś ostatnio na swoją stronę z telefonu? Ładowała mi się dobrych kilka sekund. Lighthouse daje jej 34 na 100 za szybkość - przy reklamach to zwykle znaczy, że część klikających ucieka, zanim zobaczy formularz."
- **Spokojny, rzeczowy, forma Pan:** „Sprawdziłem Państwa stronę na telefonie - ładuje się kilka sekund, Lighthouse ocenia jej szybkość na 34/100. Przy płatnym ruchu to zwykle punkt, w którym gubi się część kliknięć."
- **Zwięzły, bez rozgrzewki, wchodzi w konkret:** „34 na 100 - tyle Lighthouse daje Waszej stronie za szybkość na telefonie. Płacicie za ruch, który wykrwawia się na ładowaniu."

Fakt i liczba są te same (z notatki, sprawdzalne). Zmienia się rytm, forma, otwarcie. **Nie zmieniasz liczb pod głos** - zmieniasz opakowanie.

### Zasady nakładania głosu

- Głos dostraja **rytm, dobór słów, otwarcie, podpis**. Nie dostraja faktów ani struktury (haczyk -> diagnoza -> propozycja -> pytanie zostaje).
- Reguły z pętli uczenia biją domyślny wzorzec. Jeśli reguła mówi „nie otwieraj pytaniem", to nie otwierasz, choćby wzorzec lubił pytania.
- Głos nie jest wymówką od anty-AI floor. Człowiek może „tak mówić", ale em-dash, spalone frazy i zmyślone liczby wypadają zawsze.
- Brak realnych próbek w `Głos.md` (sam wzorzec z kalibracji) -> jesteś na ~80%. Powiedz to raz i traktuj pierwsze poprawki jako szczególnie cenne - to one dosyłają brakujące 20%.

## Część 2 - pętla uczenia

Człowiek poprawia maila. Ty naprawiasz tę wiadomość **i** decydujesz, czy to lekcja na przyszłość. Cel: z każdym mailem pisać bliżej niego, bez zamęczania go pytaniami.

### Co jest regułą, a co nie

**Regułą** (idzie do `Głos.md`) jest poprawka o **stylu, formie, preferencji** - coś, co powtórzy się przy następnej firmie:

- „nie pisz »Dzień dobry«, tylko »Hej«"
- „za sztywno, luźniej"
- „nie podpisuj »Pozdrawiam«, tylko samym imieniem"
- „nie zaczynaj od »Widzę, że«"
- „za długie, ja piszę max 4 zdania"
- „nie mów »oferuję«, ja mówię »robię«"

**Nie jest regułą** (NIE idzie do `Głos.md`):

- **Fakt o tej firmie** („to nieprawda, oni nie mają drugiego oddziału") -> popraw treść maila i notatkę researchu, nie głos.
- **Decyzja jednorazowa** („tu akurat dodaj zdanie o promocji") -> nanieś na ten mail i tyle.
- **Coś, co już jest w `Głos.md`** -> nie dubluj, najwyżej doprecyzuj istniejącą regułę.

Jak nie masz pewności, do której szuflady trafia poprawka - zapytaj wprost przy pytaniu „jednorazowo czy reguła".

### Mechanika

1. **Nanieś poprawkę od razu** na bieżącą wiadomość. Człowiek ma najpierw dostać poprawiony mail, nie ankietę.
2. **Zapytaj raz.** Jedna poprawka -> `AskUserQuestion`: „To jednorazowo, czy reguła na przyszłość?" (opcje: „Reguła - stosuj zawsze" / „Tylko ten raz"). Kilka poprawek naraz -> nie pytaj po kolei; zdestyluj je w krótką listę reguł i pokaż zbiorczo: „Zapisać któreś na stałe? [lista]". Niech zaznaczy które.
3. **Zdestyluj regułę.** Z „no bo wiesz, to »serdecznie« brzmi jak z urzędu, ja tak nie gadam" robisz: „Bez »serdecznie« i urzędowego tonu - piszę jak do znajomego." Konkretnie, w trybie rozkazującym, z przykładem jeśli pomaga. Nie zapisuj cytatu rozmowy, zapisz regułę.
4. **Dopisz do `Głos.md`.** Przeczytaj plik, znajdź sekcję `## Reguły z pętli uczenia`, **dopisz na jej końcu** (nie przepisuj całego pliku, nie ruszaj próbek ani wzorca). Format:

   ```markdown
   - <reguła w trybie rozkazującym> (z poprawki RRRR-MM-DD)
   ```

   Sekcji nie ma (starszy `Głos.md`) -> dodaj nagłówek `## Reguły z pętli uczenia` na końcu pliku, potem regułę.
5. **Potwierdź jedną linią:** „Dopisałem do Głosu: »<reguła>«. Następne maile już to uwzględnią." Bez elaboratu.

### Czego nie robić w pętli

- Nie pytaj „jednorazowo czy reguła" przy poprawce, która oczywiście jest jednorazowa (fakt o firmie, dopisek na tę jedną wiadomość). Pytanie ma wartość tylko przy stylu.
- Nie zapisuj reguł sprzecznych z tym, co już jest, bez pokazania konfliktu. „Wcześniej ustaliliśmy »otwieraj pytaniem«, teraz mówisz odwrotnie - nadpisać?"
- Nie destyluj reguły z jednej wpadki, jeśli człowiek sam mówi „to akurat wyjątek".
- Nie rozdmuchuj `Głos.md`. Dziesięć ostrych reguł jest warte więcej niż pięćdziesiąt rozmytych. Zbliźniaczone łącz w jedną.
