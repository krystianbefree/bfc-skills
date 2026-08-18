# Metoda prospectingu - wyciągnięcie z człowieka

To jest najważniejszy blok wywiadu. Człowiek jest ekspertem od tego, jak w swojej niszy
poznać dobrą firmę. Twoje zadanie: **odtworzyć jego metodę w playbook, który research
UMIE WYKONAĆ** - a nie zebrać mgliste „no szukam fajnych firm".

Reguła nadrzędna: **wynik jest najważniejszy.** Nie bierzesz odpowiedzi z dupy, nie myślisz
„super, wiem, działam". Drążysz, aż masz coś **powtarzalnego i sprawdzalnego**, i sprawdzasz
na żywo, że to działa.

## Pętla drążenia (na każdym punkcie metody)

1. **Pytanie otwarte, najpierw.** „Jak sam sprawdzasz, czy firma to dobry prospekt? Czego u nich
   szukasz? Gdzie tego szukasz?" Daj mu mówić.
2. **Reality-check odpowiedzi.** Zadaj sobie: czy z tego umiem zrobić krok, który POWTÓRZĘ bez
   niego i który da się ZWERYFIKOWAĆ z zewnątrz? To sygnał czy mgła?
3. **Mgła albo nie umiesz tego złapać -> drąż:**
   - „Po czym konkretnie to poznajesz? Co dokładnie widać?"
   - „Gdzie to sprawdzasz - jaka strona, jaki serwis?"
   - „Jak mam to wyłapać - jest to na stronie, w reklamach, w opiniach, w social?"
   - albo podaj kandydatów: „chodzi Ci o X, Y czy Z?"
4. **Walidacja na żywo (obowiązkowa).** Weź JEDNĄ prawdziwą firmę z jego niszy i spróbuj wykonać
   to, co powiedział. Sprzedaje reklamy i „patrzy na ich reklamy Meta"? Wejdź do biblioteki reklam
   i faktycznie sprawdź. Wychodzi -> potwierdzone, zapisujesz jako krok wykonywalny. Nie wychodzi
   (zablokowane / trzeba narzędzia, którego nie ma / on robi to okiem) -> powiedz wprost:
   „tego nie złapię automatem, potrzebuję X" albo „pokaż mi, jak Ty to robisz" i oznacz `[do ręki]`.
5. **Self-check na koniec bloku.** „Czy mam wszystko, żeby powtórzyć Twoją ocenę bez Ciebie?
   Czego mi jeszcze brakuje?" Wypisz luki. Nie udawaj kompletu.

## Co chcesz z niego wyciągnąć

- **Sygnały „warto"** - po czym poznaje firmę, do której warto się odezwać (ma budżet, rośnie,
  ma widoczny problem, który on rozwiązuje).
- **Dyskwalifikatory** - po czym od razu odpada (za mała, sieciówka, nie jego branża).
- **Problem -> sygnał obserwowalny** - dla każdego problemu, który jego usługa naprawia:
  co konkretnie widać z zewnątrz i gdzie to sprawdzić. To jest paliwo na pierwsze zdanie maila.

## Mapuj na to, co da się zobaczyć z zewnątrz

Research audytuje to, co publiczne. Pomagaj człowiekowi przełożyć jego intuicję na sprawdzalne sygnały:

| Człowiek mówi | Sprawdzalny sygnał | Gdzie |
|---|---|---|
| „widać, że wydają na marketing" | aktywne reklamy | biblioteka reklam Meta |
| „mają słabą stronę" | wolna strona / brak formularza / wygasły SSL | audyt strony (Lighthouse, Playwright) |
| „zaniedbany social" | martwe konto, niski engagement | profil IG/FB (Apify) |
| „klienci narzekają" | powtarzalny zarzut w opiniach | serwis opinii wg segmentu |
| „rosną" | rekrutują | ogłoszenia o pracę |

Zakładamy, że klubowicz ma na tym etapie Playwright, Firecrawl i Apify (z wcześniejszych lekcji),
więc audyt może być głęboki. Gdyby czegoś nie miał - degraduj do wyszukiwarki i oznacz `[do ręki]`.

## Zapis

Wynik -> `Grupa docelowa.md` (kogo, gdzie opinie) + `Metoda prospectingu.md` (czego szukam / gdzie /
po jakim sygnale / czym sprawdzam / co [do ręki]). Kształt: `blueprints/fundamenty.md`.

## Wiki - wysnuwaj, nie zakładaj

Jest w sejfie stary research, notatki o prospektach, lista firm? Zaproponuj: „widzę w sejfie
<X> - to Twoja metoda / Twoi prospekci? zgadza się?". Potwierdź, zanim wciągniesz. Notatka sprzed
roku może być nieaktualna.
