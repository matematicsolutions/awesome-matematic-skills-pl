---
name: matematic-marketplace-installer
description: Generuje skrypt instalacyjny MateMatic Marketplace dla prawników - Windows .bat (bez Git/npm). Użyj gdy - /marketplace install, "zainstaluj skille", "installer dla kancelarii", "jak zainstalować skille bez GitHub".
allowed-tools: Bash, Read, Write
license: Apache-2.0
data-residency: local
requires-human-approval: true
pii-egress: none
---

# MateMatic Marketplace Installer

Generuje gotowe skrypty instalacyjne skilli MateMatic dla docelowych użytkowników
(prawnicy, kancelarie) - bez wymagania Git, npm ani wiedzy technicznej.

## Safety Tiers

| Tier | Operacje | Reguła |
|------|----------|--------|
| **R** | Podgląd listy skilli do instalacji | Bez potwierdzenia |
| **M** | Generowanie skryptu .bat / .ps1 | Pokaż zawartość przed zapisem |
| **D** | Nadpisanie istniejących skilli w `~/.claude/skills/` | Użytkownik wpisuje "potwierdzam" |

## Tryby

### `/marketplace install [skill-slug]`
Generuje `install-matematic-skills.bat` gotowy do uruchomienia przez prawnika.

### `/marketplace list`
Wyświetla dostępne skille z awesome-matematic-skills-pl z opisem.

### `/marketplace check`
Sprawdza co jest już zainstalowane w `~/.claude/skills/`.

## Workflow generowania instalatora

1. Pobierz `marketplace.json` z `matematicsolutions/awesome-matematic-skills-pl` (ścieżka: `.claude-plugin/marketplace.json`)
2. Zapytaj które skille lub "wszystkie"
3. Wygeneruj `install-matematic-skills.bat` (patrz szablon poniżej)
4. Wygeneruj `README-instalacja.txt` z instrukcją krok po kroku
5. Dostarcz oba pliki gotowe do wysłania klientowi

## Szablon install-matematic-skills.bat

> **Szablon, nie gotowy plik.** Tryb `/marketplace install` podstawia trzy placeholdery przed zapisem `.bat` na dysk:
>
> - `__GIT_REF__` -> domyślnie tag najnowszej publikacji z `marketplace.json` (np. `refs/tags/v0.6.0`); klient może wymusić inny przez `--ref main` lub `--ref vX.Y.Z`. Pinowanie do taga = powtarzalna instalacja (audytowalna).
> - `__SKILL_SLUGS__` -> lista slugów wybranych skilli, oddzielona spacjami (np. `let-it-be redline-docx-pl saos-orzecznictwo`).
> - `__EXTRACTED_DIR__` -> nazwa katalogu po rozpakowaniu ZIP-a: dla taga `vX.Y.Z` to `awesome-matematic-skills-pl-X.Y.Z`, dla `main` to `awesome-matematic-skills-pl-main`.
>
> Surowy szablon poniżej **nie zadziała** uruchomiony bez podstawienia.

```batch
@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo MateMatic Marketplace Installer
echo ================================
echo Instaluje skille AI dla Claude Code
echo.

:: Katalog docelowy
set "SKILLS_DIR=%USERPROFILE%\.claude\skills"
if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"

:: Tymczasowy katalog pobrania
set "TMP_DIR=%TEMP%\matematic-install-%RANDOM%"
mkdir "%TMP_DIR%"

echo [1/4] Pobieranie skilli z MateMatic Marketplace...
:: __GIT_REF__ = refs/tags/vX.Y.Z (domyślnie najnowszy tag z marketplace.json) lub refs/heads/main (bleeding-edge).
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/matematicsolutions/awesome-matematic-skills-pl/archive/__GIT_REF__.zip' -OutFile '%TMP_DIR%\skills.zip' -UseBasicParsing"

if not exist "%TMP_DIR%\skills.zip" (
    echo BLAD: Nie udalo sie pobrac. Sprawdz polaczenie z Internetem.
    pause
    exit /b 1
)

echo [2/4] Rozpakowywanie...
powershell -Command "Expand-Archive -Path '%TMP_DIR%\skills.zip' -DestinationPath '%TMP_DIR%\extracted' -Force"

echo [3/4] Instalowanie skilli...
:: [LISTA SKILLI - generowana dynamicznie]
:: UWAGA: nazwa katalogu po Expand-Archive zalezy od ref ZIPa - dla taga vX.Y.Z bedzie "awesome-matematic-skills-pl-X.Y.Z", dla main "awesome-matematic-skills-pl-main". Tryb /marketplace install podstawia __EXTRACTED_DIR__.
:: Skille leza w pakietach: <plugin>\skills\<slug> (np. dokumenty\skills\redline-docx-pl) - szukamy sluga we wszystkich pakietach.
for %%S in (__SKILL_SLUGS__) do (
    set "SRC="
    for /d %%P in ("%TMP_DIR%\extracted\__EXTRACTED_DIR__\*") do if exist "%%P\skills\%%S\SKILL.md" set "SRC=%%P\skills\%%S"
    set "DST=%SKILLS_DIR%\%%S"
    if exist "!SRC!" (
        :: UWAGA: rd /s /q usuwa lokalne modyfikacje w skillu. Klient ostrzezony w README-instalacja.txt.
        if exist "!DST!" rd /s /q "!DST!"
        xcopy /e /i /q "!SRC!" "!DST!" >nul
        echo   OK: %%S
    ) else (
        echo   POMINIETY: %%S ^(nie znaleziono^)
    )
)

:: Zapis manifestu integralnosci skills-lock.json (SHA256 per zainstalowany skill) - patrz
:: sekcja "Integralnosc" ponizej. Self-contained (bez zewnetrznego pliku) - dziala tez u klienta
:: bez Git/npm. Hashuje TYLKO skille z tej instalacji (__SKILL_SLUGS__), nie cudze skille klienta.
echo [4/4] Zapis manifestu integralnosci...
powershell -Command ^
  "$e=[ordered]@{}; foreach ($s in ('__SKILL_SLUGS__' -split '\s+' | Where-Object { $_ })) { $f = Join-Path '%SKILLS_DIR%' (Join-Path $s 'SKILL.md'); if (Test-Path $f) { $h = (Get-FileHash $f -Algorithm SHA256).Hash.ToLower(); $e[$s] = [ordered]@{ source='matematicsolutions/awesome-matematic-skills-pl'; sourceType='github'; ref='__GIT_REF__'; skillPath=((Get-ChildItem '%TMP_DIR%\extracted\__EXTRACTED_DIR__' -Directory | Where-Object { Test-Path (Join-Path $_.FullName \"skills\$s\SKILL.md\") } | Select-Object -First 1 | ForEach-Object { $_.Name + '/skills/' + $s + '/SKILL.md' })); computedHash=\"sha256:$h\" } } }; $json = ([ordered]@{version=1; skills=$e} | ConvertTo-Json -Depth 6); [System.IO.File]::WriteAllText('%SKILLS_DIR%\..\skills-lock.json', $json, (New-Object System.Text.UTF8Encoding($false)))"

:: Czyszczenie
rd /s /q "%TMP_DIR%"

echo.
echo ================================
echo Instalacja zakonczona.
echo Uruchom nowa sesje Claude Code.
echo Skille beda dostepne jako /nazwa-skilla
echo ================================
pause
```

## Szablon README-instalacja.txt

```
INSTRUKCJA INSTALACJI - MateMatic Marketplace
=============================================

WYMAGANIA:
- Claude Code (pobierz z claude.ai/code)
- Polaczenie z Internetem

INSTALACJA:
1. Zweryfikuj zrodlo pliku - powinien pochodzic z oficjalnego release
   github.com/matematicsolutions/awesome-matematic-skills-pl/releases.
   Jezeli kancelaria ma polityke whitelistingu - zglos plik do IT przed otwarciem.
2. (ZALECANE dla kancelarii) Zweryfikuj sume SHA256:
   - Pobierz z release page plik `checksums.txt`.
   - W PowerShell w katalogu pobranego .bat uruchom:
       Get-FileHash -Algorithm SHA256 install-matematic-skills.bat
   - Porownaj z linia w checksums.txt. Jezeli niezgodne - NIE uruchamiaj, zglos
     wsparcie@matematic.co.
3. Kliknij dwukrotnie install-matematic-skills.bat
   (Windows SmartScreen moze pokazac ostrzezenie. Jezeli plik pochodzi z innego
    zrodla niz oficjalny release - NIE uruchamiaj. Jezeli jest z release i polityka
    kancelarii pozwala - kliknij "Wiecej informacji" -> "Uruchom i tak".
    Prawa administratora NIE sa wymagane - skrypt pisze do %USERPROFILE%.)
4. Poczekaj az pojawi sie "Instalacja zakonczona!"
5. Uruchom Claude Code od nowa
6. Sprawdz: wpisz /szukaj-orzeczen "dobro dziecka" - komenda jest dostepna

PROBLEMY:
- Jesli Windows blokuje skrypt: Wlasciwosci pliku -> Odblokuj
  (Tylko gdy plik pochodzi z oficjalnego release. W innym wypadku - zglos IT.)
- Jesli brak Internetu: sprawdz firewall firmowy

Wsparcie: support@matematic.co
```

## Uwagi techniczne

- Nie wymaga Git (używa `Invoke-WebRequest` + `Expand-Archive`)
- Nie wymaga npm/node
- Działa na Windows 10/11 z PowerShell 5.1+
- Skrypt **nadpisuje** istniejące skille o tych samych nazwach (lokalne modyfikacje skopiowanych skilli przepadają). Klient, który dostosował skill po instalacji, powinien zrobić kopię przed re-runem.
- Ścieżka docelowa: `%USERPROFILE%\.claude\skills\` (katalog skilli Claude Code w profilu użytkownika)
- **Reproducible install**: domyślny ref to **najnowszy tag** z `marketplace.json` (audytowalna wersja). Tryb `--ref main` pobiera `HEAD` (do testowania, nie do produkcji w kancelarii).
- **Weryfikacja integralności SHA256** (v0.6.1+): wraz z każdym release MateMatic publikuje plik `checksums.txt` jako asset release page zawierajacy SHA256 dla generowanego `install-matematic-skills.bat`. Klient kancelarii powinien:
  1. Pobrać `checksums.txt` z tej samej strony co .bat.
  2. Uruchomić `Get-FileHash -Algorithm SHA256 install-matematic-skills.bat` w PowerShell.
  3. Porównać hex z linią w `checksums.txt` (case-insensitive, lower-case standard).

  Workflow generowania `checksums.txt` jest częścią release pipeline MateMatic (`gh release upload vX.Y.Z install-matematic-skills.bat checksums.txt`). Klient dostaje hash spod tej samej autorytatywnej domeny `github.com/matematicsolutions/...` co plik instalacyjny - nie potrzebuje osobnego kanału.

  **Ograniczenie znane**: GitHub nie publikuje stabilnej sumy dla automatycznie generowanych `archive/refs/tags/...zip` (regeneruje przy każdym żądaniu). `checksums.txt` dotyczy konkretnie wygenerowanego `install-matematic-skills.bat` (deterministyczny output skilla), nie archiwum całego repo.

## Integralność (`skills-lock.json`)

Wzorzec zapożyczony z `tutti-os/tutti` (skills-lock.json: `source` + `sourceType` +
`skillPath` + `computedHash` SHA256 per skill). Uzupełnia `checksums.txt`: tamten chroni
plik `.bat` PRZED uruchomieniem, ten wykrywa, że zainstalowany skill cicho się zmienił
PO instalacji (wymiar „Supply chain" z `audyt-kodu-25-wymiarow-pl`).

Krok `[4/4]` w szablonie `.bat` liczy SHA256 `SKILL.md` każdego skilla z tej instalacji
i zapisuje `skills-lock.json` obok katalogu skilli (`%USERPROFILE%\.claude\skills-lock.json`),
razem z refem, z którego pobrano paczkę. Przy kolejnej instalacji lub audycie można
porównać hash i wykryć drift (ktoś ręcznie zmienił skill albo źródło podmieniło zawartość
pod tym samym slugiem), zamiast ufać, że „wygląda tak samo".

To narzędzie do wykrywania, NIE blokada - gdy hash się nie zgadza, poinformuj
użytkownika, nie przerywaj automatycznie instalacji (kancelaria nie ma kontekstu, żeby
ocenić, czy drift jest zamierzony).

Ręczne przeliczenie manifestu (np. audyt własnego katalogu skilli):
[scripts/write-skills-lock.ps1](scripts/write-skills-lock.ps1).
