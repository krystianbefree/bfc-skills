# Synchronizacja zdarzeń - Gmail i kalendarz zasilają panel

Trzeci strumień, który dolewa do lejka i klientów. Write-back bierze fakty z rozmowy, a synchronizacja to Claude sięgający przez MCP do Gmaila i Kalendarza, wyciągający zdarzenia biznesowe i dopisujący je do plików MD sejfu. Serwer panelu tego nie robi - Gmail i Kalendarz są narzędziami Claude, nie serwera.

Odpalasz na żądanie: "zsynchronizuj panel", "/bfc:panel sync", "podciągnij maile do panelu".

## Zasada nadrzędna - tylko firmy już w sejfie

Najpierw zbuduj białą listę firm, dopiero potem czytaj cokolwiek. Lista bierze się z:

- `Pozyskiwanie.md` - nazwy firm ze wszystkich etapów (także z linków `[[Firma]]`).
- `Klienci/*.md` - nazwy z plików plus e-mail/domena, jeśli są we frontmatterze albo w `## Kontakt`.

Liczą się **tylko** zdarzenia pasujące do firm z tej listy. Nieznany nadawca nie zakłada nowego leada - nowe firmy wchodzą z `research`/`cold-mail` albo z rozmowy, nie ze skrobania skrzynki. Wszystko spoza listy pomijasz po cichu i nie czytasz treści.

## Zapytania Gmail

Wysłane oferty (mail wychodzący do firmy z lejka):

```
in:sent newer_than:14d
```

Wyniki przefiltruj po nazwie/domenie firmy z listy. Precyzyjniej, per firma:

```
in:sent newer_than:14d (to:@domena-firmy.pl OR "Nazwa Firmy")
```

Temat/treść przesądza, czy to oferta (słowa: oferta, propozycja, wycena, zakres, pakiet, kwota). Kwota w mailu -> `wartość:`.

Odpowiedzi od prospektów (wątek, w którym wcześniej wyszedł Twój mail/oferta):

```
in:inbox newer_than:14d from:(@domena-A.pl OR @domena-B.pl)
```

Narzędzia MCP Gmaila: `search_threads` do znalezienia, `get_thread`/`get_message` do przeczytania tematu i treści - tylko dla dopasowanych firm.

## Zapytania kalendarza

Wydarzenia z ostatnich 14 dni, których tytuł albo uczestnik pasuje do firmy z sejfu:

- `search_events`/`list_events` w oknie 14 dni.
- Dopasuj po tytule (nazwa firmy, "call z X", "spotkanie X") albo po mailu uczestnika (domena firmy).
- Wydarzenie, które już się odbyło, z klientem -> `ostatni_kontakt:` = data tego wydarzenia.

## Mapowanie zdarzenie -> zmiana pliku

Nie duplikuję tu tabeli - obowiązuje ta z `write-back.md`. Zdarzenia z Gmaila i kalendarza wpadają w te same wiersze:

| Zdarzenie | Wiersz w `write-back.md` |
|---|---|
| Wysłana oferta do firmy z lejka | "wysłałem ofertę X za 4k" -> etap Oferta, `wartość:` jeśli kwota w mailu |
| Odpowiedź od prospekta w wątku | "napisałem/zadzwoniłem do X" -> etap Rozmowa albo ustaw `follow-up:` |
| Rozmowa/spotkanie w kalendarzu z klientem | "gadałem z klientem X" -> `ostatni_kontakt:` = data wydarzenia w `Klienci/X.md` |

Reszta reguł zapisu (jedna zmieniona linia na fakt, kopia przed zapisem, brak liczby to "brak danych") - też z `write-back.md`.

## Prywatność i niejednoznaczne

- Tylko biznesowe. Prywatny mail, newsletter, wątek nie o współpracy -> pomiń.
- Tylko firmy już w sejfie. Whitelist najpierw, czytanie treści potem.
- Niejednoznaczne -> potwierdź z człowiekiem **przed** zapisem. Mail "wysłany", ale nie wiadomo, czy to oferta, czy zwykła odpowiedź? Kwota podana warunkowo? Pokaż, co znalazłeś, zapytaj, dopiero zapisz.

## Degradacja bez MCP

Brak podłączonego Gmaila albo Kalendarza w MCP -> powiedz to jednym zdaniem i pomiń ten strumień, nie wywalaj się. Na przykład: "Gmaila nie widzę w MCP, więc pominąłem synchronizację maili - lejek zostaje na tym, co masz w notatkach i z rozmowy." Reszta panelu działa normalnie.

## Kadencja

Domyślnie ręcznie, na żądanie. Kto chce, może zaplanować to cyklicznie przez `/schedule` (np. co rano) - wtedy sync leci sam i dopisuje zmiany, ale to wybór człowieka, nie domyślka. Po synchronizacji raportuj jedną linią na zmianę, tak jak przy write-back.
