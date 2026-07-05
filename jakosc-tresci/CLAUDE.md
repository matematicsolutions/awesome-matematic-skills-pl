# Jakość treści - reguły wspólne

Ten plik to siatka bezpieczeństwa pluginu. Obowiązuje, nawet gdy konkretny skill milczy.

Te skille edytują polski tekst - usuwają wzorce pisania AI (humanizer-pl) i recenzują copy pod kątem treści i tonu (marko-pl-content). To narzędzia redakcyjne, nie porada prawna i nie źródło faktów.

## Reguły

- **Zero zmyślania.** Skille zmieniają słowa i strukturę, nigdy faktów, liczb, cytatów ani źródeł. Jeśli teza nie ma źródła, naprawą jest podanie źródła, nie pewniejsze sformułowanie.
- **Brand-safety.** Humanizer poprawia prozę; nie jest narzędziem do omijania detektorów AI. MateMatic uczy transparentności AI - celem jest lepszy tekst, nie ukrywanie, że użyto AI.
- **Bramka człowieka.** Wynik to draft. Zanim pójdzie na zewnątrz, sprawdza go człowiek.

## Zakres pluginu

Neutralny jurysdykcyjnie i tematycznie. Bez konektorów, nic nie wysyła na zewnątrz. Do weryfikacji prawnej (grounding, czerwony zespół, scoring) użyj pluginu `fundament-weryfikacyjny`.
