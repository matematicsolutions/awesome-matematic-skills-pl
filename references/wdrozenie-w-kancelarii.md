# Standard wdrożenia w kancelarii

Wspólny standard dla wszystkich skilli w tym repo. Zanim materiały produkcyjne trafią do pracy, kancelaria przechodzi te decyzje. Dotyczy danych, umów i śladu audytowego.

## Decyzje przed pierwszym użyciem

- **Mapa danych** - które kategorie danych w ogóle wchodzą do narzędzia, a które zostają poza nim (objęte tajemnicą, szczególnie wrażliwe).
- **Umowa powierzenia (RODO art. 28)** - z każdym dostawcą, który przetwarza dane osobowe. Sprawdź retencję, podpowierzenie i przekazywanie poza EOG.
- **Anonimizacja na wejściu** - ustal, kiedy dane osobowe zastępuje się znacznikami lokalnie, zanim cokolwiek wyjdzie do API.
- **Próg poufności** - reguła, przy której materiału nie wnosi się do narzędzia wcale. Domyślnie: przy wątpliwości nie przekazuj.

## Ślad audytowy

Każdy wynik wysokiej stawki zostawia ślad: model, data, źródła, klasa pewności, kto zatwierdził. Skill `legal-ai-audit-bundle` pakuje to w artefakt zgodny z aktem o sztucznej inteligencji (art. 12, prowadzenie rejestru). To dowód należytej staranności, nie biurokracja - przyda się, gdy ktoś zapyta, na czym oparto rozstrzygnięcie.

## Podział ról

- Prawnik bierze odpowiedzialność zawodową za wynik i jest bramką przed wysyłką.
- Narzędzie przygotowuje projekt i ślad rozumowania.
- Administrator danych odpowiada za umowy powierzenia i mapę danych.

## Czego ten standard NIE robi

- Nie zastępuje oceny skutków dla ochrony danych (DPIA), gdy jest wymagana.
- Nie negocjuje umowy powierzenia za kancelarię - wskazuje tylko, że jest konieczna.
- Nie przesądza, czy konkretny dostawca spełnia wymogi - to ocena kancelarii.
