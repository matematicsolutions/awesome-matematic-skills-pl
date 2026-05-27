# Konstytucja - Let It Be (matematic-anonimizacja-pl)

Wersja 1.0.0. Dokument definiuje twarde zasady projektu. Zmiana zasady wymaga bumpa wersji (SEMVER) i wpisu w [CHANGELOG.md](../CHANGELOG.md).

## Art. 1 - Lokalność i zero-cloud

Silnik działa wyłącznie lokalnie. Nie wysyła treści, danych osobowych ani telemetrii do żadnego API, modelu ani usługi zewnętrznej. Zero zależności zewnętrznych (`node:*` only). To warunek przydatności dla kancelarii związanej tajemnicą zawodową (PoA art. 6, URP art. 3).

## Art. 2 - Determinizm i reprodukowalność

Detekcja jest deterministyczna (regex + checksuma + gazetteer), bez modelu językowego. Ten sam wejściowy tekst daje zawsze ten sam wynik. Walidatory checksum są funkcjami czystymi (bez I/O). Audyt jest reprodukowalny.

## Art. 3 - Dwa tryby, jawna nieodwracalność

Projekt rozróżnia anonimizację (nieodwracalną, RODO motyw 26) od pseudonimizacji (odwracalnej, RODO art. 4 pkt 5). Tryb anonimizacji nie tworzy mapy i usuwa surowe wartości z wyniku API - nieodwracalność jest wymuszona kodem, nie konwencją.

## Art. 4 - Bramka "no PII leaves"

Po każdej podmianie sprawdzamy, czy żaden oryginał nie przetrwał w wyniku. Jeśli przetrwał, operacja jest przerywana. Komunikat błędu (`ResidualPIIError.message`) nigdy nie zawiera wartości danych osobowych - tylko licznik. Wartości są dostępne wyłącznie w polu `.samples` do logu incydentalnego.

## Art. 5 - Minimalność audytu

Audit log zapisuje liczniki, hashe i typy encji - nigdy treści ani wartości PII. Log jest czytelny dla Inspektora bez deszyfrowania (AI Act art. 12, CELEX 32024R1689).

## Art. 6 - Narzędzie wspomaga, nie zastępuje prawnika

Skill jest pomocą, nie gwarancją. Ograniczenia (fleksja, zakres gazetteera, brak detekcji adresów) są jawnie udokumentowane w README i SKILL.md. Odpowiedzialność za weryfikację dokumentu pozostaje po stronie człowieka.

## Art. 7 - Atrybucja patternu i niezależność treści

Logika polskich PII pochodzi z własnej biblioteki MateMatic `pl-entities` (Patron). Wzorce operacyjne (TTL, source_hash, audit log, archiwum AES-GCM) to cherry-pick patternu z gregmos/PII-Shield (MIT, snapshot 2026-05-22). Treść napisana od zera pod polski rynek - nie jest to tłumaczenie 1:1. Późniejsze zmiany licencji upstream nie są automatycznie wciągane. Szczegóły: [THIRD_PARTY_INSPIRATIONS.md](../THIRD_PARTY_INSPIRATIONS.md).
