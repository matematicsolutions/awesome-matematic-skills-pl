---
name: intake-sufficiency-pl
description: >
  Ocena wystarczalnosci zlecenia/briefu na WEJSCIU - zanim zaczniesz prace prawna,
  sprawdza czy masz dosc kontekstu: jasny cel, zdefiniowany zakres, zidentyfikowany
  podmiot, fakty/dokumenty, ograniczenia. Wypisuje luki i niejednoznacznosci, generuje
  pytania uzupelniajace do zadania klientowi, sklada szkielet karty zlecenia. Lustro
  legal-request-router-pl: router ocenia jaka kontrole dac OUTPUTOWI, ten skill ocenia
  czy WEJSCIE wystarcza, by w ogole zaczac. Uzywaj gdy: "czy mam dosc zeby zaczac",
  "ocen brief", "czego brakuje w zleceniu", "jakie pytania zadac klientowi", "czy to
  zlecenie jest kompletne", "luki w brief", "doprecyzuj zlecenie", "intake", na poczatku
  nowej sprawy / po pierwszym kontakcie / po bookingu spotkania.
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: AnttiHero/lavern (Apache 2.0) - pattern src/api/briefing (analiza wystarczalnosci), schemat i rubryka napisane od zera
  companion_skills: legal-request-router-pl, let-it-be, citation-grounding-pl
---

# Intake Sufficiency PL - ocena wystarczalnosci zlecenia

## Filozofia

**Polowa zlych opinii prawnych to nie blad analizy, tylko zbyt cienkie wejscie.** Klient pisze
"sprawdzcie te umowe", po czym okazuje sie, ze nie wiadomo wobec jakiego ryzyka, kto jest druga
strona ani jaki jest cel. Ten skill nazywa to, czego brakuje, ZANIM zacznie sie praca - i zamienia
luki w konkretne pytania do klienta, zamiast w domysly wpisane do deliverable.

Skill **nie wykonuje** pracy prawnej. Ocenia kompletnosc wejscia i generuje pytania.

## Lustro routera

- `legal-request-router-pl` patrzy na zadanie i decyduje, jaka kontrole dac **outputowi** (grounding / debata / paczka).
- `intake-sufficiency-pl` patrzy na zlecenie i decyduje, czy **wejscie** wystarcza, by zaczac.

Naturalna kolejnosc: najpierw intake-sufficiency (czy mam dosc), potem praca, potem router (jak skontrolowac wynik).

## Rubryka wystarczalnosci (6 wymiarow, 0-100)

| Wymiar | Pytanie kontrolne | Waga |
|---|---|---|
| Cel | Czy wiadomo, po co klient przychodzi (opinia / audyt / pismo / negocjacja)? | 20 |
| Zakres | Czy zakres jest zdefiniowany (co wchodzi, co nie)? | 20 |
| Podmiot | Czy strony / podmiot sa zidentyfikowane (nazwa, NIP/KRS, rola)? | 15 |
| Fakty | Czy sa dokumenty albo stan faktyczny do oparcia analizy? | 20 |
| Ograniczenia | Czy znane sa twarde ograniczenia (deadline, budzet, poufnosc, jurysdykcja)? | 15 |
| Kryteria sukcesu | Czy wiadomo, co dla klienta znaczy dobry wynik? | 10 |

Werdykt: **strong** >= 80, **adequate** >= 50, **insufficient** < 50.

## Workflow

1. **Pseudonimizuj** wejscie przez `let-it-be`, jesli zawiera dane objete tajemnica.
2. **Oceń** zlecenie wg 6 wymiarow rubryki - kazdy wymiar ma fakty na poparcie oceny, nie ogolnik.
3. **Wypisz luki i niejednoznacznosci** - co konkretnie jest nieobecne lub niejasne.
4. **Wygeneruj pytania uzupelniajace** - jedno pytanie na luke, kazde przypisane do wymiaru, oznaczone
   wymagane/opcjonalne. Pytanie ma byc gotowe do wyslania klientowi, nie notatka dla siebie.
5. **Zloz szkielet karty zlecenia** - cel / zakres / podmiot / ryzyka / kryteria sukcesu / instrukcje wstepne.
   Pola, ktorych nie da sie wypelnic z wejscia, zostaja jawnie "(do ustalenia - patrz pytania)".

## Schemat wyjscia

```json
{
  "wystarczalnosc": {
    "score": 45,
    "werdykt": "insufficient",
    "luki": ["brak zdefiniowanego celu", "podmiot druga strona niezidentyfikowany"],
    "niejednoznacznosci": ["'pilne' bez konkretnego terminu"]
  },
  "pytania_uzupelniajace": [
    { "id": "q_cel", "text": "Jaki jest cel - opinia, pismo czy negocjacja?", "wymiar": "cel", "wymagane": true }
  ],
  "karta_zlecenia": {
    "cel": "(do ustalenia - patrz pytania)",
    "zakres": "...",
    "podmiot": "...",
    "ryzyka": [],
    "kryteria_sukcesu": [],
    "instrukcje_wstepne": "..."
  }
}
```

## Output (dla uzytkownika)

```
## Wystarczalnosc zlecenia: 45/100 (insufficient)

### Luki
- brak zdefiniowanego celu sprawy
- druga strona niezidentyfikowana (brak nazwy / NIP)

### Pytania do klienta (zadac PRZED rozpoczeciem)
- [wymagane] (cel) Czy oczekuja Panstwo opinii, pisma czy wsparcia w negocjacji?
- [wymagane] (podmiot) Jaka firma jest druga strona (pelna nazwa, NIP/KRS)?
- [opcjonalne] (ograniczenia) Czy jest twardy termin?

### Karta zlecenia (szkielet)
- Cel: (do ustalenia - patrz pytania)
- Zakres: weryfikacja umowy dostawy
- Podmiot: (do ustalenia)
- Instrukcje wstepne: zebrac komplet zalacznikow do umowy

Rekomendacja: NIE zaczynaj analizy merytorycznej przed odpowiedzia na pytania wymagane.
```

## Reguly twarde

- **Insufficient = stop, nie zgaduj.** Przy werdykcie insufficient nie wypelniaj luk domyslami w deliverable -
  najpierw pytania do klienta. Domysl wpisany jako fakt to zarodek blednej opinii.
- **Pytanie na luke, nie na zapas.** Nie generuj pytan o rzeczy, ktore wejscie juz zawiera.
- **Jedno wejscie, jedna ocena.** Skill ocenia kompletnosc, nie jakosc merytoryczna sprawy.

## Ochrona danych (RODO)

Ocena dziala na tresci zlecenia - jezeli zawiera dane objete tajemnica zawodowa, pseudonimizuj przez
`let-it-be` przed wyslaniem do modelu. Skill nie zapisuje wejscia poza katalogiem sprawy.

## Integracja z AI Act

Jawne nazwanie luk i niejednoznacznosci na wejsciu to element nadzoru czlowieka (art. 14) - czlowiek
swiadomie decyduje, czy zaczac z niepelnym wejsciem, zamiast dostac deliverable udajacy kompletnosc.
Ocena wystarczalnosci moze trafic do `legal-ai-audit-bundle` jako uzasadnienie startu sprawy.

## Atrybucja

Pattern (analiza wystarczalnosci briefu: score + luki + pytania uzupelniajace + karta zlecenia)
zainspirowany przez AnttiHero/lavern (Apache 2.0, `src/api/briefing/briefing-schema.ts`). Rubryka
6 wymiarow, schemat i reguly napisane od zera pod polski kontekst kancelaryjny. Nie skopiowano kodu Lavern.
