# Szkielet weryfikatora domenowego (template marketplace)

Adaptacja 7-plikowego backbone'u z biblioteki Jeanne Sulzer
(`jeannesulzer/international-criminal-tribunals-skills`, CC BY 4.0). Tam każdy trybunał = osobny
skill o identycznej strukturze; dodanie jurysdykcji = kopia szkieletu + podmiana specyfiki.

Tu materializujemy to jako **wzorzec compound dla skilli weryfikacyjnych MateMatic/PATRON**:
dodanie nowej domeny prawnej (np. „prawo zamówień publicznych", „RODO/UODO", „orzecznictwo KIO",
„prawo pracy") = kopia tego szkieletu. **Silnik się nie zmienia** - każdy weryfikator domenowy
reużywa `../../scripts/ground-citations.mjs` (gradient ISTNIENIE/TREŚĆ/FRAGMENT). Podmieniasz
tylko trzy rzeczy domenowe.

## Co jest wspólne (NIE przepisuj per domena)

- **Silnik** `ground-citations.mjs` - mechanika string-match + gradient + kalibracja.
- **Doktryna** `gradient-weryfikacji.md` - poziomy, macierz `claim_type`, reguła kalibracji.
- **Statusy** i format raportu.
- **Reguła RODO** (lokalnie), integracja z AI Act art. 12/14.

## Co podmieniasz per domena (3 rzeczy)

1. **Resolver kotwicy** - skąd bierzesz `anchor_resolved` (ISTNIENIE). PL orzecznictwo → SAOS;
   UE → EUR-Lex/CELEX; KIO → baza UZP; ustawy → ISAP. To jeden companion_skill + jedna drabinka.
2. **Drabinka źródeł** - kolejność fallbacku gdy bezpośredni fetch padnie (wzór: `../drabinka-zrodel-pl.md`).
3. **Pułapki domenowe (`traps.md`)** - to najważniejszy transfer od Sulzer. Patrz niżej.

## 7-plikowy backbone (PL)

```
<domena>/
├── SKILL.md                         # punkt wejścia: dyscyplina, kiedy używać, workflow, twarde reguły
├── CHANGELOG.md                     # semver, Keep-a-Changelog
├── references/
│   ├── zrodla-autorytatywne.md      # Tier 1 / Tier 2 / "nie cytuj" - hierarchia źródeł domeny
│   ├── format-cytatu.md             # jak cytować w tej domenie (sygnatury, numeracja, skróty)
│   ├── drabinka-zrodel.md           # fallback ladder przy awarii fetcha
│   ├── teksty-zrodlowe.md           # co wolno cytować "z pamięci" (akty podstawowe) vs co MUSI być pobrane
│   └── traps.md                     # pułapki domenowe = guardrails (patrz niżej)
└── examples/
    ├── przyklad-weryfikacja.md      # jeden cytat zweryfikowany end-to-end, wszystkie poziomy
    └── przyklad-audyt.md            # audyt gotowego draftu vs audyt finalnego dokumentu
```

## Pułapki domenowe (`traps.md`) - sednowy wzorzec

U Sulzer każdy trybunał ma listę „classic traps" - błędów, których generyczny lint nie złapie,
zakodowanych jako twarde reguły. Przykłady z oryginału: `Article 28(a)` vs niestatutowy `28(1)`;
ten sam oskarżony nosi numer ICTY *i* późniejszy MICT; nigdy nie ujawniaj chronionego świadka.

To jest **dokładnie wzorzec `marko-pl-content` / `matematic-patron-pr-review-pl`** zastosowany do
weryfikacji cytatów: „regresje specyficzne dla domeny". Dla każdej polskiej domeny wypisz 3-7 pułapek:

**Przykłady pułapek PL (do `traps.md` konkretnej domeny):**
- **Numeracja jednostek redakcyjnych:** `art. 446 § 4 k.c.` vs `art. 446 ust. 4` (kodeksy mają §,
  ustawy ustępy) - mylenie = sygnał, że cytat nie był sprawdzony w źródle.
- **Tekst ujednolicony vs pierwotny:** który stan prawny na datę zdarzenia? Powołanie aktualnego
  brzmienia do zdarzenia sprzed nowelizacji = błąd merytoryczny mimo poprawnej sygnatury.
- **Teza vs uzasadnienie:** cytat z uzasadnienia podany jako teza orzeczenia; zdanie odrębne podane
  jako stanowisko składu (to polski odpowiednik „majority vs separate opinions" Sulzer).
- **Uchwała vs wyrok vs postanowienie:** moc wiążąca i charakter różne - nie zrównuj.
- **Sygnatura izby:** `CSK` (Izba Cywilna) vs `KK` (Karna) vs `PK` (Pracy) - litera nośna.
- **Glosa ≠ orzeczenie:** cytowanie glosy jako stanowiska sądu.

Pułapki domenowe wpinasz w workflow jako check przed/po groundingu: gdy `claim_type` =
`cytat_doslowny` podpiera tezę o stanowisku sądu, dorzuć rekord `stanowisko_sadu` (reguła
z `gradient-weryfikacji.md`).

## Jak zainstalować nowy weryfikator

1. Skopiuj `SKILL.template.md` → `<domena>/SKILL.md`, wypełnij placeholdery `<…>`.
2. Napisz `traps.md` (3-7 pułapek domeny) - to daje skillowi przewagę nad generycznym groundingiem.
3. Wskaż resolver kotwicy i drabinkę (zwykle 1 companion_skill + 1 plik drabinki).
4. Silnik reużyj przez relatywną ścieżkę lub symlink do `ground-citations.mjs` - NIE kopiuj kodu.
5. Dwa przykłady end-to-end na realnych (nie hipotetycznych) sprawach z domeny.

To jest compound: szkielet napisany raz, każda kolejna domena to godziny zamiast dni, a silnik
poprawiony w jednym miejscu ulepsza wszystkie weryfikatory naraz.
