<#
.SYNOPSIS
  Generuje/aktualizuje skills-lock.json (SHA256 per skill) po instalacji z Marketplace.
  Wzorzec zapozyczony z tutti-os/tutti (skills-lock.json) - integralnosc zamiast slepego
  zaufania do "co akurat lezy w katalogu skilli po ostatnim zipie".

.PARAMETER SkillsDir
  Katalog z zainstalowanymi skillami, np. "$env:USERPROFILE\.claude\skills"

.PARAMETER Slugs
  Opcjonalna lista slugow do ujecia w manifescie. Bez niej - wszystkie podkatalogi
  z SKILL.md (uwaga: wtedy wpis dostaje zrodlo Marketplace takze dla skilli spoza niego).

.PARAMETER LockFile
  Docelowy plik JSON, domyslnie <SkillsDir>\..\skills-lock.json

.PARAMETER Source
  Repo zrodlowe zapisywane w kazdym wpisie (domyslnie repo Marketplace MateMatic)

.PARAMETER Ref
  Ref, z ktorego pobrano paczke (np. refs/tags/v0.6.0). Opcjonalny.
#>
param(
    [Parameter(Mandatory = $true)][string]$SkillsDir,
    [string[]]$Slugs,
    [string]$LockFile = "$SkillsDir\..\skills-lock.json",
    [string]$Source = "matematicsolutions/awesome-matematic-skills-pl",
    [string]$Ref
)

if (-not (Test-Path $SkillsDir)) {
    Write-Error "SkillsDir nie istnieje: $SkillsDir"
    exit 1
}

$entries = [ordered]@{}

$dirs = Get-ChildItem -Path $SkillsDir -Directory
# -File przekazuje "a,b" jako jeden napis - rozbij na przecinkach i bialych znakach.
if ($Slugs) { $Slugs = @($Slugs | ForEach-Object { $_ -split '[,\s]+' } | Where-Object { $_ }) }
if ($Slugs) { $dirs = $dirs | Where-Object { $Slugs -contains $_.Name } }

$dirs | ForEach-Object {
    $slug = $_.Name
    $skillMd = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillMd) {
        $hash = (Get-FileHash -Path $skillMd -Algorithm SHA256).Hash.ToLower()
        $entry = [ordered]@{
            source       = $Source
            sourceType   = "github"
            skillPath    = "skills/$slug/SKILL.md"
            computedHash = "sha256:$hash"
        }
        if ($Ref) { $entry.Insert(2, "ref", $Ref) }
        $entries[$slug] = $entry
    }
}

if ($entries.Count -eq 0) {
    # Pusty manifest to nie sukces - nie ma czego pilnowac.
    Write-Error "Brak skilli z SKILL.md do ujecia w manifescie: $SkillsDir"
    exit 1
}

$lock = [ordered]@{
    version = 1
    skills  = $entries
}

$json = $lock | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($LockFile, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Zapisano $($entries.Count) wpisow do $LockFile"
