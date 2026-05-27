# Generuje 22 SVG badges per skill do assets/badge-<slug>.svg
# Format: 200x60, lewy pasek kategorii (6px), tytul + krotki opis
# Kolory z DESIGN.md (Midnight Gold)

$ErrorActionPreference = 'Stop'

$outDir = Join-Path $PSScriptRoot '..\assets'
$outDir = (Resolve-Path $outDir).Path

# Kategorie -> kolor akcentu
$cat = @{
  walidacja    = @{ color = '#e3c373'; label = 'WALIDACJA OUTPUTU' }
  umowy        = @{ color = '#f0d080'; label = 'UMOWY' }
  orzecznictwo = @{ color = '#bac3fd'; label = 'ORZECZNICTWO' }
  narzedzia    = @{ color = '#7dd3a3'; label = 'NARZEDZIA' }
  higiena      = @{ color = '#f5c96c'; label = 'HIGIENA TEKSTU' }
  produkty     = @{ color = '#c6a85b'; label = 'PRODUKT' }
  metodologia  = @{ color = '#ffb4ab'; label = 'METODOLOGIA' }
}

# 22 skille: slug, kategoria, tytul, podtytul
$skills = @(
  @{ slug='legal-request-router-pl';     kat='walidacja';    title='Legal Request Router';   sub='triage zadania prawnego' },
  @{ slug='intake-sufficiency-pl';       kat='walidacja';    title='Intake Sufficiency';     sub='ocena wystarczalnosci briefu' },
  @{ slug='citation-grounding-pl';       kat='walidacja';    title='Citation Grounding';     sub='anty-halucynacja cytatu' },
  @{ slug='adversarial-legal-review-pl'; kat='walidacja';    title='Adversarial Review';     sub='czerwony zespol deliverable' },
  @{ slug='deliverable-fidelity-pl';     kat='walidacja';    title='Deliverable Fidelity';   sub='wiernosc analiza -> pismo' },
  @{ slug='legal-ai-audit-bundle';       kat='walidacja';    title='AI Audit Bundle';        sub='paczka zgodnosci AI Act art.12' },
  @{ slug='redline-docx-pl';             kat='umowy';        title='Redline DOCX PL';        sub='natywne Track Changes Word' },
  @{ slug='saos-orzecznictwo';           kat='orzecznictwo'; title='SAOS Orzecznictwo';      sub='API systemu SAOS' },
  @{ slug='szukaj-orzeczen-v2';          kat='orzecznictwo'; title='Szukaj Orzeczen v2';     sub='wyszukiwanie + raport tematyczny' },
  @{ slug='eu-sparql-search';            kat='orzecznictwo'; title='EU SPARQL Search';       sub='EUR-Lex + Cellar + CJEU' },
  @{ slug='legal-data-hunter-pl';        kat='orzecznictwo'; title='Legal Data Hunter';      sub='katalog zrodel prawa PL' },
  @{ slug='webwright-legal-pl';          kat='orzecznictwo'; title='Webwright Legal PL';     sub='MS / SN / TK przez Playwright' },
  @{ slug='markitdown';                  kat='narzedzia';    title='MarkItDown';             sub='dokument -> Markdown dla LLM' },
  @{ slug='opendataloader-pdf';          kat='narzedzia';    title='OpenDataLoader PDF';     sub='reading order + tabele' },
  @{ slug='matematic-workspace-backup';  kat='narzedzia';    title='Workspace Backup';       sub='gogcli + age dla RODO art.32' },
  @{ slug='let-it-be';                   kat='higiena';      title='Let It Be';              sub='anonimizacja PESEL/NIP/imion' },
  @{ slug='matematic-konstytucja-ai';    kat='produkty';     title='Konstytucja AI';         sub='produkt 15-40k PLN dla kancelarii' },
  @{ slug='matematic-expert-panel';      kat='produkty';     title='Expert Panel';           sub='produkt 5-15k PLN review' },
  @{ slug='matematic-spec-driven';       kat='metodologia';  title='Spec-Driven';            sub='4 fazy + Constitution Check' },
  @{ slug='matematic-mcp-fastmcp-instructions-pl'; kat='metodologia'; title='MCP FastMCP Kanon'; sub='5 elementow walidowanych na dograh' },
  @{ slug='matematic-patron-pr-review-pl';         kat='metodologia'; title='PATRON PR Review';   sub='14 sekcji LegalTech-specific' },
  @{ slug='matematic-marketplace-installer';       kat='metodologia'; title='Marketplace Installer'; sub='dystrybucja .bat dla kancelarii' }
)

function Escape-Xml($s) {
  return $s -replace '&','&amp;' -replace '<','&lt;' -replace '>','&gt;' -replace '"','&quot;'
}

foreach ($s in $skills) {
  $c = $cat[$s.kat]
  $titleEsc = Escape-Xml $s.title
  $subEsc   = Escape-Xml $s.sub
  $catLabel = $c.label
  $catColor = $c.color
  $aria     = Escape-Xml ("{0} - {1}" -f $s.title, $s.sub)

  $svg = @"
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="60" viewBox="0 0 200 60" role="img" aria-label="$aria">
  <title>$titleEsc</title>
  <desc>$subEsc</desc>
  <rect width="200" height="60" rx="6" fill="#0a1420"/>
  <rect width="200" height="60" rx="6" fill="none" stroke="#1a2433" stroke-width="1"/>
  <rect x="0" y="0" width="6" height="60" fill="$catColor"/>
  <text x="16" y="20" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="8" font-weight="500" fill="$catColor" letter-spacing="1.2">$catLabel</text>
  <text x="16" y="38" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13" font-weight="600" fill="#dae3f5">$titleEsc</text>
  <text x="16" y="52" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="9" fill="#7c8a9f">$subEsc</text>
  <text x="184" y="20" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="8" font-weight="500" fill="#e3c373" text-anchor="end" letter-spacing="1.0">PL</text>
</svg>
"@

  $path = Join-Path $outDir ("badge-{0}.svg" -f $s.slug)
  Set-Content -Path $path -Value $svg -Encoding utf8 -NoNewline
  Write-Host ("OK  {0}" -f (Split-Path $path -Leaf))
}

Write-Host ""
Write-Host ("Wygenerowano {0} badges w {1}" -f $skills.Count, $outDir)
