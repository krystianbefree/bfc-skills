# Pozyskiwanie - lejek i jak się sam zasila

Zakładka Pozyskiwanie to serce panelu. `Pozyskiwanie.md` jest źródłem prawdy (format: `pliki-sejfu.md`), a dwa strumienie **dolewają** się do niego automatycznie, żeby człowiek nie przepisywał danych ręcznie.

## Co pokazuje adapter

- Liczba prospektów w każdym etapie z configu (`etapy_lejka`).
- Wartość lejka: suma `wartość: <kwota>` z etapów Rozmowa i Oferta (dealy, które realnie mogą wpaść).
- Konwersja: ilu z etapu wejściowego doszło do "Klient" (jeśli człowiek wybrał tę liczbę).
- Pozycje z zaległym `follow-up:` lecą do sygnałów i do zakładki Dziś.

## Strumień 1 - z research i cold-mail (jeśli `wpina_research` = Tak)

- Nowe firmy z `research` (tabela `Prospekty <data>.md`, notatki o firmach) -> dopisz do etapu **Prospekt**, jeśli jeszcze ich nie ma w lejku. Dedup po nazwie firmy.
- Wysłany cold mail z `cold-mail` -> przesuń firmę do **Kontakt** i ustaw `follow-up:` wg sekwencji z tego skilla.
- Nie duplikuj. Firma jest w lejku raz, przesuwa się między etapami, nie pojawia się w kilku naraz.

Import jest **dolewaniem**, nie nadpisaniem. Ręczne zmiany człowieka w `Pozyskiwanie.md` mają pierwszeństwo: jeśli ktoś ręcznie przesunął firmę do Oferty, import z research nie cofa jej do Prospekt.

## Strumień 2 - z rozmowy (write-back)

Zdania typu "zadzwoniłem do firmy X", "wysłałem ofertę Y za 4k" przesuwają firmę między etapami. Reguły: `write-back.md`.

## Czego nie robić

- Nie licz atrybucji sprzedaży do pojedynczej rolki ani maila. Lejek pokazuje ruch, nie przyczynę.
- Nie wymyślaj wartości deala. Brak `wartość:` to brak liczby, nie zero - taka pozycja nie wchodzi do wartości lejka, ale liczy się do liczby prospektów.
- Firma bez ruchu od dawna to sygnał (lead utknął), nie powód do cichego usunięcia.
