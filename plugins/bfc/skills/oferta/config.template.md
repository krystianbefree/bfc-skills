---
utworzone: {{DATA}}
skill: bfc/oferta
---

# Konfiguracja: oferta

Twoje usługi, ceny i warunki. Zwykła notatka, poprawiaj ręcznie kiedy chcesz.
Zmieniłeś cennik? Popraw tu jedną liczbę, nie musisz powtarzać wywiadu.
Pola oznaczone `TODO:` skill dopyta przy następnym uruchomieniu.

## Usługi

{{uslugi}}

## Pieniądze

- **Model rozliczeń:** {{model_rozliczen}}
- **Widełki:** {{widelki}}

**Co przesuwa cenę:**

{{co_przesuwa_cene}}

## Warunki w każdej ofercie

{{warunki}}

**Gwarancja:** {{gwarancja}}

## Forma dokumentu

- **Długość:** {{dlugosc}}
- **Format:** {{format_pliku}}
- **Folder w sejfie:** {{folder_ofert}}

---

## Realizacje do powoływania się

Dopisz tu konkretne realizacje z wynikami, które mogę wstawiać do ofert.
Format, który działa najlepiej:

```
### <Klient albo branża, jeśli nie możesz podać nazwy>
- Problem: <co było nie tak>
- Co zrobiłem: <konkretnie>
- Efekt: <liczba albo obserwowalna zmiana>
- Czy mogę podać nazwę klienta: tak / nie
```

Puste? Skill będzie budował ofertę na procesie i gwarancji zamiast na historii.
To działa, ale słabiej.

## Notatki własne

Wszystko, o co skill nie zapytał, a co ma wiedzieć przy pisaniu ofert.
