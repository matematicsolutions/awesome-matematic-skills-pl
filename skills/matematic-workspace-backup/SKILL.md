---
name: matematic-workspace-backup
description: Konfiguracja szyfrowanego backupu Google Workspace dla kancelarii prawnych przez gogcli + age + prywatne repo Git. Używaj gdy klient-kancelaria pyta o RODO art. 32, ciągłość Workspace, ochronę przed lockout/ransomware, lub gdy MateMatic robi audyt zgodności backup'u. Trigger keywords - "backup Workspace", "art. 32 RODO", "ciągłość Workspace", "kancelaria backup Gmail/Drive", "lockout Google", "DR drill".
---

# matematic-workspace-backup

> Skill MateMatic dla wdrożeń backup'u Google Workspace w kancelariach prawnych.
> Komponenty: gogcli (steipete/gogcli, MIT) + age (X25519) + prywatne repo Git.
> Pozycjonowanie: edukator (nie sprzedawca) - nie odsprzedajemy gogcli, uczymy klienta z niego korzystać.

## Kiedy używać tego skilla

- Klient-kancelaria pyta "jak zapewnić ciągłość Workspace" / "co gdy Google nas zablokuje"
- Audyt zgodności art. 32 RODO dla kancelarii na Google Workspace
- Wdrożenie pilotażowe backup'u u nowego klienta (po podpisanej umowie)
- Konfiguracja safety profile dla AI agenta w kancelarii (read-only sandbox)
- DR drill (kwartalny, regression coverage)
- Recovery z encrypted shards po incydencie

## Komponenty i wymagania

**Narzędzia:**
- gogcli v0.14.0+ (Windows/macOS/Linux) - https://github.com/steipete/gogcli
- age (built-in w gogcli)
- Git + prywatne repo (GitHub/GitLab/self-hosted Gitea)
- Google Workspace Admin Console (do Service Account + DWD)
- Google Cloud Console (do OAuth client credentials)

**Wymagania klienta-kancelarii:**
- Workspace Admin (nie Personal Gmail)
- Komputer dedykowany do backupu (nie laptop użytkownika kancelarii)
- Password manager 2FA dla klucza age (1Password / Bitwarden Premium)
- Prywatne repo Git z 2FA require + branch protection

## Safety Tiers (KRYTYCZNE - dane kancelarii)

Przed każdą operacją ustal tier i zastosuj regułę:

| Tier | Operacje | Reguła |
|------|----------|--------|
| **R - Read-only** | `gog backup status`, `gog backup verify`, pre-engagement audit checklist | Bez potwierdzenia. Wykonaj od razu. |
| **M - Mutating** | `gog backup push --query --max 25` (bounded), konfiguracja Service Account, setup age key | Pokaż plan operacji. Czekaj na potwierdzenie słowne. |
| **D - Destructive** | `gog backup push --services all` (full), `Remove-Item -Recurse -Force` (cleanup plaintext po DR drill) | Użytkownik musi wpisać dosłownie: **"potwierdzam"** zanim wykonasz. |

> Dane kancelarii = tajemnica adwokacka / radcowska. Błąd w `--services all` bez bounded testu lub usunięcie bez weryfikacji = incydent RODO.

---

## Workflow 7-etapowy

### Etap 1 - Pre-engagement audit (1h)

Wypełnij checklist z klientem-kancelarią:
- [ ] Workspace plan (Business Standard / Plus / Enterprise) - wpływa na limity API
- [ ] Liczba użytkowników w domenie
- [ ] Polityka retencji emaili / Drive (jeśli istnieje)
- [ ] Czy są obecne backupy? (jakiekolwiek - SyncBackup, third-party, Google Vault?)
- [ ] Polityka tajemnicy zawodowej (czy klucz po stronie kancelarii zaakceptowany?)
- [ ] Inspektor Ochrony Danych (IOD) - powiadomiony?
- [ ] Wewnętrzny audytor - powiadomiony?

### Etap 2 - Google Cloud + Workspace setup (2h)

Wykonuje **Workspace Admin kancelarii** (NIE MateMatic - tajemnica zawodowa).
Referuj do wewnętrznego template `SETUP_MATEMATIC.md` (dostarczanego przez MateMatic per zlecenie, dostosuj per klient).

Wynik:
- OAuth client JSON
- Service Account JSON
- DWD allowlist scope confirmation

### Etap 3 - Instalacja lokalna (1h)

Per klient:
1. Pobierz gogcli v0.14.0 binary z signed releases
2. Verify SHA256 checksum
3. Install do `C:\Tools\gogcli\` lub `~/Tools/gogcli/`
4. Init backup repo lokalnie + remote (prywatne)
5. Generate age key + secure backup do 1Password / fizyczny seif

### Etap 4 - Bounded first backup (30 min)

ZAWSZE bounded test przed `--services all`:
```powershell
gog backup push --services gmail --account admin@kancelaria.pl --query "newer_than:7d" --max 25
gog backup status
gog backup verify
```

Sanity check `manifest.json` - **musi być cleartext metadata only**:
- ✅ export_time, service_names, account_hashes, shard_paths, row_counts, byte_sizes, hashes
- ❌ NIE bodies, subjects, senders, Drive filenames, contacts, event titles

### Etap 5 - Full backup + schedule (3h)

Po udanym bounded:
```powershell
gog backup push --services all --account admin@kancelaria.pl
```

Schedule (Windows Task Scheduler / cron):
- Daily 03:00 - `gog backup push --services all`
- Weekly poniedziałek 04:00 - `gog backup verify`
- Quarterly DR drill - manual SOP

### Etap 6 - Safety profile dla AI agentów (1h)

Skopiuj `safety-profiles/matematic-readonly.yaml` (baseline z bundle MateMatic) i dostosuj per kancelaria (np. dodaj `--account` allowlist dla konkretnych kont, jeśli sub-team-y).

Build dedykowanego binary:
```bash
./build-safe.sh safety-profiles/lawfirm-readonly.yaml -o bin/gog-lawfirm-readonly
```

Wymaga Go toolchain. Alternatywa runtime-only:
```powershell
gog --enable-commands gmail.search,gmail.get,calendar.events.list,drive.list ...
```

### Etap 7 - DR drill template + handover (2h)

DR drill kwartalny - template SOP:
1. Random sample decrypt: `gog backup cat data/gmail/<hash>/labels.jsonl.gz.age --pretty`
2. Full export: `gog backup export --out drill-2026Q2 --gmail-format markdown`
3. Sanity: czytelność, daty, no errors
4. Log: data, % files OK, time-to-recovery, anomalie
5. Cleanup plaintext: `Remove-Item -Recurse -Force drill-2026Q2`

Handover do klienta:
- Runbook PDF (per kancelaria customizowany)
- DR drill log template
- Lista checków bezpieczeństwa pre-prod
- Kontakt MateMatic dla quarterly review

## Trzyfilarowy filtr MateMatic dla tego skilla

✅ **Co bierzemy z gogcli:**
- Architektura age + private Git + lokalny klucz
- Safety profiles fail-closed embedded
- Bounded backup pattern (`--query --max`)
- Manifest cleartext metadata-only

⚠️ **Czego NIE rekomendujemy:**
- Ślepe `--services all` bez bounded testu
- Klucz age w niesprawdzonym password manager
- Public Git repo dla shards
- Runtime allowlist zamiast embedded safety profile (production)
- Przechowywanie OAuth/SA JSON w repo

🔧 **Własna warstwa MateMatic:**
- Mapowanie na art. 32 RODO + tajemnica zawodowa (art. 6 ust. 1 ustawy Prawo o adwokaturze, art. 3 ust. 3-5 ustawy o radcach prawnych)
- DR drill template kwartalny
- AI agent sandbox checklist
- Pytania audytowe do dostawców LegalTech (5-7 pytań sprawdzających)
- Anti-patterns kancelarii (red pen)

## Obowiazkowa informacja dla klienta

Każde użycie skilla wymaga jawnego komunikatu klientowi:
> "Narzędzie gogcli to projekt open-source Petera Steinbergera (MIT, https://github.com/steipete/gogcli). MateMatic Solutions Sp. z o.o. nie jest autorem narzędzia ani autorem powiązanym. Świadczymy usługi konfiguracji, audytu i edukacji - vendor-agnostic. Klient samodzielnie zarządza kluczami szyfrowania i tokenami OAuth."

## Granica MateMatic / kancelaria-klient

- **MateMatic robi:** konfigurację, safety profile, audyt, DR drill template, szkolenie zespołu
- **MateMatic NIE robi:** dostępu do plaintext bodies klienta, trzymania klucza age klienta, uruchamiania `gog backup export` na produkcyjnych danych klienta
- **Kancelaria-klient robi:** trzyma klucz age, uruchamia backup, czyta plaintext, decyduje o retention

## Status

- v1.0.0 (2026-05-27)
- Gotowosc do wdrozenia produkcyjnego: po pierwszym wdrozeniu pilotazowym (lessons learned wracaja do skilla jako patch)
