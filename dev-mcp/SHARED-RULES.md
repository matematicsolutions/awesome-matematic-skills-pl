## Wspólne reguły wtyczki dev-mcp (Dev-mcp)

Te reguły obowiązują w każdym skillu tej wtyczki, także gdy sam skill milczy. Są skopiowane do każdego skilla, więc działają zarówno po instalacji całej wtyczki, jak i pojedynczego skilla.

Plugin to narzędzia deweloperskie MateMatic: spec-driven development, kanon budowy MCP serverów, recenzent PR dla LegalTech, generator instalatora marketplace. Skierowany do osób budujących, nie do prawnika końcowego.

### Reguły

- **Wynik to projekt.** Specyfikacje, recenzje i instalatory są punktem wyjścia, sprawdza je człowiek przed użyciem.
- **Recenzja nie zastępuje testów.** Recenzent PR wskazuje ryzyka (org scoping, audit_log, grounding, PII w logach); nie gwarantuje poprawności - kod nadal trzeba przetestować.
- **Sekrety.** Przy budowie MCP i recenzji kodu nie umieszczaj kluczy ani danych klienta w przykładach, logach ani promptach.

### Zakres pluginu

Plugin daje warsztat deweloperski (advanced). Nie jest narzędziem do pracy prawnej - do tego są pozostałe pluginy huba.
