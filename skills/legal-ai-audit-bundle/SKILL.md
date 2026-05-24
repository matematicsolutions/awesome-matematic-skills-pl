---
name: legal-ai-audit-bundle
description: >
  Pakuje output AI prawny w artefakt audytowy zgodny z AI Act art. 12 - łączy
  deliverable, ślad rozumowania (debata / grounding), log kosztu i metadane
  (model, data, źródła, kto zatwierdził) w jeden ustrukturyzowany folder z manifestem
  i hashami integralności SHA256. Generalizacja matematic-video-governance na dowolny
  output prawny. Dowód należytej staranności i record-keepingu. Używaj gdy: "spakuj
  audyt", "bundle zgodności", "artefakt AI Act", "ślad rozumowania do archiwum",
  "dokumentacja outputu AI", "record-keeping", "co archiwizować dla AI Act",
  "log kosztu i decyzji", "paczka audytowa deliverable", po zakończeniu opinii /
  adversarial-legal-review / grounding gdy trzeba zarchiwizować dowód.
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: AnttiHero/lavern (Apache 2.0) - pattern audit-bundle; wzór własny matematic-video-governance (AI Act art. 12)
  companion_skills: adversarial-legal-review-pl, citation-grounding-pl, matematic-video-governance, legal-ai-plugin-governance
---

# Legal AI Audit Bundle - artefakt zgodności dla outputu AI prawnego

## Filozofia

**Jeśli nie potrafisz odtworzyć, jak AI doszło do wyniku, nie powinieneś wysyłać tego wyniku.**

AI Act art. 12 wymaga rejestrowania zdarzeń (prowadzenia rejestrów) dla systemów wysokiego ryzyka,
art. 14 - nadzoru człowieka, art. 50 - poinformowania osoby, że treść została wygenerowana przez AI.
Dla kancelarii używającej AI w pracy
z klientem oznacza to: dla każdego istotnego deliverable musi istnieć ślad - jaki model, jakie
źródła, jaka weryfikacja, jaki koszt, kto zatwierdził. Ten skill składa ten ślad w jedną paczkę
z hashami integralności, tak by dało się ją odtworzyć i wykazać przy audycie.

To nie jest deliverable dla klienta. To deliverable dla audytora, regulatora i Twojej własnej
odpowiedzialności zawodowej.

## Co wchodzi do paczki

| Artefakt | Źródło | Wymagane |
|---|---|---|
| Deliverable finalny | praca prawna | TAK |
| Ślad rozumowania | transcript `adversarial-legal-review-pl` lub log analizy | TAK dla high-stakes |
| Raport grounding | output `citation-grounding-pl` | TAK jeśli były cytaty |
| Log kosztu | tokeny / koszt przebiegów | TAK |
| Metadane | model, wersja, data, źródła, autor, zatwierdzający | TAK |
| Pseudonimizacja | mapa `let-it-be` (jeśli użyta) - TRZYMANA OSOBNO, nie w paczce | warunkowo |

## Workflow

1. **Zbierz artefakty** - upewnij się, że istnieją pliki: deliverable, transcript/ślad,
   raport grounding, log kosztu. Brakujące oznacz w manifeście jako `MISSING` - paczka i tak
   powstaje, ale z widoczną luką (audytor musi widzieć, czego nie ma).

2. **Opisz manifest** - przygotuj descriptor JSON (patrz FORMAT) z metadanymi i ścieżkami do
   artefaktów.

3. **Złóż paczkę** - uruchom skrypt:
   ```bash
   node scripts/assemble-bundle.mjs <descriptor.json> <katalog-docelowy>
   ```
   Skrypt: kopiuje artefakty do ustrukturyzowanego folderu, liczy SHA256 każdego pliku
   (integralność), generuje `manifest.json` + czytelny `INDEX.md`.

4. **Zweryfikuj kompletność** - skrypt zwraca listę `MISSING` i ostrzega, jeśli brak
   record-keepingu wymaganego dla high-stakes. Uzupełnij albo świadomie odnotuj brak.

5. **Archiwizuj** - paczka idzie do rejestru AI kancelarii. Mapa pseudonimizacji NIGDY nie ląduje
   w paczce - trzymana osobno, dostęp ograniczony (to klucz do re-identyfikacji = dane osobowe).

## Format descriptora (input skryptu)

```json
{
  "deliverable_id": "OPINIA-2026-018",
  "tytul": "Opinia w sprawie ważności klauzuli X",
  "data": "2026-05-22",
  "model": "claude-opus-4-7",
  "autor": "Wiesław Mazur",
  "zatwierdzajacy": "adw. ...",
  "stawka": "WYSOKA",
  "zrodla": ["II CSK 1/19", "art. 385(1) KC", "CELEX 32024R1689"],
  "pseudonimizacja_uzyta": true,
  "artefakty": {
    "deliverable": "C:/.../opinia-final.md",
    "slad_rozumowania": "C:/.../adversarial-transcript.md",
    "raport_grounding": "C:/.../grounding-report.json",
    "log_kosztu": "C:/.../cost.json"
  }
}
```

Pole `zrodla` to lista dowolnych identyfikatorów źródeł w formie tekstowej (sygnatura, oznaczenie
przepisu, numer CELEX, nazwa pliku) - skrypt zapisuje je bez parsowania, służą tylko do opisu paczki.

## Struktura wygenerowanej paczki

```
OPINIA-2026-018/
├── INDEX.md              # czytelne streszczenie: co, kiedy, model, źródła, kompletność
├── manifest.json         # metadane + SHA256 każdego artefaktu + status MISSING
├── 01-deliverable/
├── 02-slad-rozumowania/
├── 03-grounding/
└── 04-koszt/
```

## Output (raport po złożeniu)

```
## Paczka audytowa: OPINIA-2026-018

Zlokalizowana: <katalog>/OPINIA-2026-018/
Artefakty: 4/4 obecne | 0 MISSING
Integralność: 4 pliki zahashowane (SHA256 w manifest.json)
High-stakes: TAK → wymóg śladu rozumowania SPEŁNIONY ✅
Pseudonimizacja: użyta → mapa NIE w paczce (trzymaj osobno) ⚠️

Gotowe do archiwizacji w rejestrze AI kancelarii.
```

## Ochrona danych (RODO)

- Skill działa lokalnie - kopiowanie plików i hashowanie w Node, bez sieci.
- **Mapa pseudonimizacji nigdy nie wchodzi do paczki** - to klucz re-identyfikacji (dane osobowe
  art. 4 pkt 5 RODO). Paczka audytowa ma być bezpieczna do pokazania audytorowi; mapa - nie.
- Jeśli deliverable zawiera dane wrażliwe, rozważ przechowywanie w paczce hasha + lokalizacji
  zamiast pełnej treści (decyzja kancelarii / inspektora ochrony danych).

## Integracja z AI Act i resztą stacku

- **art. 12** prowadzenie rejestrów: manifest + hashe = odtwarzalny rejestr zdarzeń.
- **art. 50** poinformowanie o AI: INDEX.md mówi jasno, że wynik powstał z udziałem AI i jakiego modelu.
- **art. 14** nadzór: pole `zatwierdzajacy` = człowiek wziął odpowiedzialność.
- Wejścia produkują: `adversarial-legal-review-pl` (ślad), `citation-grounding-pl` (raport).
- Pokrewny: `matematic-video-governance` robi to samo dla wideo; ten skill - dla pism prawnych.

## Roadmap upgrade integralności: Merkle chain nad SHA256

Obecna wersja składa paczkę z **SHA256 per artefakt** w `manifest.json`. To wystarczy dla pojedynczego
deliverable, ale przy kancelarii produkującej setki opinii rocznie audytor chce zweryfikować
integralność dowolnej paczki **bez czytania całego rejestru AI**.

Cherry-pick wzorca z [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)
(MIT, "Merkle-chained audit log"): nad zbiorem hashes paczek buduje się Merkle tree, root chain'owany
z poprzednim rootem. Proof-of-inclusion dla pojedynczej paczki w O(log n) zamiast O(n).

Praktycznie dla kancelarii (planowane, nie zaimplementowane):

1. Każda paczka audytowa po złożeniu rejestruje swój `manifest_hash` w rejestrze AI kancelarii.
2. Co N paczek (np. N=64) liczy się Merkle root + zapisuje obok poprzedniego (chain).
3. Audytor pyta "czy paczka OPINIA-2026-018 jest integralna i istniała wtedy gdy twierdzicie" →
   verifier zwraca proof O(log 64) zamiast hash całego rejestru.

Wartość dla AI Act art. 12: kancelaria po 5 latach działania ma dziesiątki tysięcy paczek;
weryfikacja "ten log nie był modyfikowany od 2027 r." musi być efektywna. SHA256-per-paczka
zostaje (wymagany dla detekcji modyfikacji w obrębie paczki), Merkle dodany dla efektywnej
weryfikacji rejestru.

Status: roadmap, do zaplanowania w osobnym sprintcie. Nie blokuje obecnego użycia skilla.

## Roadmap rozszerzenie 2: per-decision proof receipt (`check_id` + `policy_hash`)

**Komplementarne do Merkle, nie zamienne**. Merkle daje **integralność lańcucha audytu** (audytor wie, że log nie był modyfikowany). Proof receipt daje **dowód konkretnej pojedynczej decyzji** (audytor wie, że "decyzja X z 2026-09-12 14:23 została zaakceptowana zgodnie z polityką wersji Y").

Cherry-pick wzorca z [ICME Preflight](https://docs.icme.io) (cloud-only, NIE wpinamy jako zależność z powodu Art. 1 lokalności danych - patrz [ADR-0031 PATRON](https://github.com/matematicsolutions/patron/blob/main/governance/adr/0031-deterministyczna-walidacja-z-lokalnym-proof-receipt.md)). Wzorzec lokalny:

1. Każda paczka audytowa (`OPINIA-2026-018`) opcjonalnie zawiera plik `policy-verdict.json`:
   ```json
   {
     "check_id": "0f25c151-e63e-4253-8eb2-1e6e894c7ce5",
     "policy_hash": "60c79bbc4f8ac087de1110fa0e347292f35b6d2943a2a4ccd18ae991a5d64418",
     "verdict": "ALLOWED",
     "policy_version": "v1.4 z 2026-08-15",
     "timestamp": "2026-09-12T14:23:00Z"
   }
   ```
2. `policy_hash` to SHA256 ze skompilowanej polityki (Konstytucja AI kancelarii w wersji obowiązującej w momencie decyzji).
3. Audytor (regulator UODO, KIRP, klient kancelarii) dostaje paczkę audytową + binarkę `kancelaria-verify` która offline weryfikuje, że `policy_hash` zgadza się z zarchiwizowaną polityką + verdict jest deterministyczny dla tej polityki.
4. **Public surface** lokalnie: `proof-listing.html` w paczce audytowej generuje czytelną stronę "X decyzji weryfikowanych w tym kwartale, lista check_id, polityka v1.4 obowiązywała".

Wartość dla AI Act art. 12 + art. 26: kancelaria nie pokazuje audytorowi "ufaj mi że logowaliśmy". Pokazuje "tu jest 47 proof receiptów, każdy z policy_hash, polityka v1.4 SHA256 5f3a..., zweryfikuj sam offline".

Status: roadmap. Razem z Merkle składają się na pełną warstwę audytu: Merkle (integralność lańcucha) + proof receipt (dowód decyzji) + paczka audytowa (kontekst sprawy). Trzy warstwy dla różnych pytań audytora.

## Atrybucja

Pattern (audit-bundle alongside deliverable) zainspirowany przez AnttiHero/lavern (Apache 2.0)
oraz własny wzór `matematic-video-governance`. Struktura, manifest i skrypt napisane od zera pod
AI Act i polskie realia kancelaryjne.

Pattern Merkle-chain upgrade (sekcja Roadmap) zainspirowany przez
[microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) (MIT, Microsoft Corp., 2026).
Cherry-pick wzorca, nie kodu - implementacja od zera w Node pod Postgres kancelarii.

Pattern per-decision proof receipt (sekcja Roadmap 2) zainspirowany przez
[ICME Preflight](https://docs.icme.io) (cloud-only SaaS, autor Houman Shadab, Stanford CodeX Fellow,
snapshot 2026-05-24) - patrz [hshadab/preflight-mike](https://github.com/hshadab/preflight-mike) (MIT)
oraz [ICME-Lab/icme-preflight-guardrail](https://github.com/ICME-Lab/icme-preflight-guardrail) (MIT).
NIE wpinamy ICME jako zależność (cloud-only narusza Art. 1 lokalności danych Patrona) -
cherry-pick wzorca tylko, lokalny offline solver + verifier napisany od zera. Patrz [ADR-0031 PATRON](https://github.com/matematicsolutions/patron/blob/main/governance/adr/0031-deterministyczna-walidacja-z-lokalnym-proof-receipt.md)
dla pełnych granic decyzji architektonicznej.
