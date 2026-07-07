# Standard wdrożenia w kancelarii

Wspólny standard dla wszystkich skilli w tym repo. Zanim materiały produkcyjne trafią do pracy, kancelaria przechodzi te decyzje. Dotyczy danych, umów i śladu audytowego.

## Decyzje przed pierwszym użyciem

- **Mapa danych - trzy kosze, na piśmie.** Które kategorie danych wchodzą do narzędzia, a które zostają poza nim:

  | Kosz | Przykład | Linia |
  |---|---|---|
  | Wolny | publiczne ustawy i orzeczenia, własne szablony, dane zanonimizowane | wolno przetwarzać |
  | Warunkowy | akta zlecenia, projekty umów | tylko po spełnieniu warunków umownych i anonimizacyjnych (punkty niżej) |
  | Zakazany | dane szczególnie wrażliwe, materiał bez podstawy przetwarzania | nigdy |

  Linię zapisuje się w wewnętrznej instrukcji kancelarii - nie w głowie wspólnika.
- **Umowa powierzenia (RODO art. 28)** - z każdym dostawcą, który przetwarza dane osobowe. Sprawdź retencję, podpowierzenie i przekazywanie poza EOG.
- **Anonimizacja na wejściu** - ustal, kiedy dane osobowe zastępuje się znacznikami lokalnie, zanim cokolwiek wyjdzie do API.
- **Próg poufności** - reguła, przy której materiału nie wnosi się do narzędzia wcale. Domyślnie: przy wątpliwości nie przekazuj.

## Ślad audytowy

Każdy wynik wysokiej stawki zostawia ślad: model, data, źródła, klasa pewności, kto zatwierdził. Skill `legal-ai-audit-bundle` pakuje to w artefakt zgodny z aktem o sztucznej inteligencji (art. 12, prowadzenie rejestru). To dowód należytej staranności, nie biurokracja - przyda się, gdy ktoś zapyta, na czym oparto rozstrzygnięcie.

## Podział ról

- Prawnik bierze odpowiedzialność zawodową za wynik i jest bramką przed wysyłką.
- Narzędzie przygotowuje projekt i ślad rozumowania.
- Administrator danych odpowiada za umowy powierzenia i mapę danych.

## Bramka człowieka - nazwana, nie domyślna

„Człowiek sprawdza wynik" nie działa, dopóki nie wiadomo **kto sprawdza co**. Minimum do zapisania:

- wszystko co wychodzi na zewnątrz (klient, sąd, urząd, druga strona) sprawdza wskazany prawnik,
- wyliczenia terminów weryfikuje osoba odpowiedzialna za kalendarz - wobec akt, nie wobec outputu,
- sygnatury i cytaty przechodzą `citation-grounding-pl` przed wysyłką (mechanicznie, jednoprzebiegowo),
- łańcuch kontroli zapisany w instrukcji - wtedy da się go wykazać i wyegzekwować.

## Pilotaż na fixture'ach, nie na aktach

Zanim do narzędzia trafi realny materiał: zbuduj materiał ćwiczebny (fixture - sprzeczności
jak w realnym zleceniu, bez ukrytej modelowej odpowiedzi) i listę kryteriów **behawioralnych**
(„dobry output robi X: podnosi sprzeczność, taguje wyliczenie, nie potwierdza przepisu
z pamięci" - nie „dochodzi do wyniku Y"), potem przepuść skill przez fixture i porównaj wynik
z kryteriami. [`examples/`](../examples/) w tym repo ma na razie jeden ogólny przykład
łańcucha walidacji, nie gotowe fixture'y per skill. Ten sam przebieg po każdej aktualizacji
skilla to test regresji: widać, czy zachowanie się nie zepsuło.

## Konektory - tylko niezbędne

Zasada najmniejszych uprawnień: podłączaj wyłącznie konektory, których skille faktycznie
używają. Konektor orzeczniczy (SAOS) to kręgosłup dyscypliny źródeł - bez niego skille
oznaczają powołania jako `[z pamięci - sprawdź]` zamiast je weryfikować. Agenci tła
dodatkowo wg modelu trójpoziomowego ([`przepisy-agentow/`](../przepisy-agentow/README.md)):
czytelnik niezaufanych akt bez sieci, Write tylko u redaktora.

## Czego ten standard NIE robi

- Nie zastępuje oceny skutków dla ochrony danych (DPIA), gdy jest wymagana.
- Nie negocjuje umowy powierzenia za kancelarię - wskazuje tylko, że jest konieczna.
- Nie przesądza, czy konkretny dostawca spełnia wymogi - to ocena kancelarii.
