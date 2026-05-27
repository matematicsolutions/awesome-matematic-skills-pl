# Tryb 2: Raport Tematyczny

Rozszerzenie trybu wyszukiwania. Po fazach 1-4 (search + fetch) Claude analizuje zbiór i generuje profesjonalny raport z grupowaniem.

```
SEARCH (szukaj_orzeczen.py) → FETCH (saos_fetch.py) → ANALIZA (Claude)
→ JSON (raport_data.json) → DOCX (raport_tematyczny.py) → DELIVER
```

---

## Krok A: Wyszukaj i pobierz

Wykonaj Tryb 1 (fazy 1-4). Rekomendowane: 100-200 orzeczeń.

---

## Krok B: Statystyki zbioru

```bash
cat /home/claude/saos-output/saos_judgments_*.json | python3 -c "
import sys, json
from collections import Counter
data = json.load(sys.stdin)
judgments = data.get('judgments', [])
print(f'Orzeczeń: {len(judgments)}')
dates = sorted([j.get('judgmentDate','') for j in judgments if j.get('judgmentDate')])
if dates: print(f'Zakres dat: {dates[0]} - {dates[-1]}')
types = Counter(j.get('judgmentType','?') for j in judgments)
print(f'Typy: {dict(types)}')
courts = Counter()
for j in judgments:
    cn = (j.get('division') or {}).get('court') or {}
    courts[cn.get('name','?')] += 1
print('Sądy (top 10):')
for c,n in courts.most_common(10): print(f'  {n:3d} | {c}')
regs = Counter()
for j in judgments:
    for r in (j.get('referencedRegulations') or []):
        t = r.get('journalTitle','')
        if t: regs[t] += 1
print('Przepisy (top 10):')
for r,n in regs.most_common(10): print(f'  {n:3d} | {r[:80]}')
judges = Counter()
for j in judgments:
    for jg in (j.get('judges') or []):
        nm = jg.get('name','')
        if nm: judges[nm] += 1
print('Sędziowie (top 10):')
for jg,n in judges.most_common(10): print(f'  {n:3d} | {jg}')
kws = Counter()
for j in judgments:
    for k in (j.get('keywords') or []): kws[k] += 1
print('Hasła (top 15):')
for k,n in kws.most_common(15): print(f'  {n:3d} | {k}')
divs = Counter()
for j in judgments:
    dn = ((j.get('division') or {}).get('name') or '')
    if dn: divs[dn] += 1
print('Wydziały (top 10):')
for d,n in divs.most_common(10): print(f'  {n:3d} | {d}')
prefixes = Counter()
for j in judgments:
    for c in (j.get('courtCases') or []):
        cn = c.get('caseNumber','')
        parts = cn.split()
        if parts: prefixes[parts[0]] += 1
print('Prefiksy sygnatur (top 15):')
for p,n in prefixes.most_common(15): print(f'  {n:3d} | {p}')
"
```

---

## Krok C: Grupowanie tematyczne (PRACA CLAUDE)

Cel: 4-8 grup. Każde orzeczenie → JEDNA grupa. Grupy <5% zbioru → scal z „Pozostałe".

**Metoda adaptacyjna - 5 sygnałów:**

1. **Sygnatury** - prefiks wskazuje typ sprawy:
   `Nsm` = opiekuńcze | `RC` = rodzinne | `K` = karne | `C` = cywilne | `P` = pracownicze | `U` = ubezpieczeniowe | `ACa/Ca` = apelacje cywilne | `Ka` = apelacje karne

2. **Hasła** (`keywords`) - grupuj po powtarzających się hasłach

3. **Wydziały** (`division.name`) - rodzinne, karne, cywilne, pracy...

4. **Podstawy prawne** (`referencedRegulations`) - KRO, KPC, KK, KC...

5. **Text mining treści** - konteksty frazy ±100 znaków, charakterystyczne kolokacje

**Dla każdej grupy:** tytuł + opis (2-3 zdania) + wzorce text mining + lista orzeczeń + top przepisy + rozkład sądów.

**Przekrojowo:** globalne przepisy (top 15) + top sędziowie (top 10) + rozkład sądów (top 15) + konteksty frazy (5-7 głównych) + wnioski (4-6 pkt).

---

## Krok D: JSON raportu

Schemat → patrz [json-schemat.md](json-schemat.md). Claude tworzy plik i zapisuje przez `create_file` do `/home/claude/saos-output/raport_data.json`.

---

## Krok E: Generuj DOCX

```bash
python3 <skill-path>/scripts/raport_tematyczny.py \
  --input /home/claude/saos-output/raport_data.json \
  --output /home/claude/saos-output/raport_tematyczny.docx
```

---

## Krok F: Dostarcz

```bash
cp /home/claude/saos-output/raport_tematyczny.docx /mnt/user-data/outputs/
```

`present_files` z raportem DOCX na pierwszym miejscu.

**Pliki dodatkowe:**

| Plik | Zawartość |
|------|-----------|
| `raport_tematyczny_{fraza}_{ts}.docx` | Profesjonalny raport z grupowaniem |
| `raport_data_{ts}.json` | Struktura danych raportu (opcjonalnie) |
