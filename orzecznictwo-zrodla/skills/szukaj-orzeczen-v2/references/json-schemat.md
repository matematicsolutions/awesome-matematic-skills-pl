# Schemat JSON raportu tematycznego

Claude buduje ten JSON w Kroku D i zapisuje go przez `create_file`.

```json
{
  "meta": {
    "phrase": "pozbawienie władzy rodzicielskiej art. 111 kro",
    "subtitle": "dotyczących pozbawienia władzy rodzicielskiej (art. 111 KRO)",
    "total_judgments": 200,
    "total_groups": 6,
    "date_range": "2002-2025",
    "report_date": "11 marca 2026"
  },
  "summary": "Przeanalizowano 200 orzeczeń... [narracyjne podsumowanie 3-5 zdań]",
  "groups": [
    {
      "title": "Pozbawienie władzy rodzicielskiej - postępowania opiekuńcze",
      "count": 59,
      "percent": "30%",
      "date_from": "2014-05-15",
      "date_to": "2025-08-20",
      "description": "Bezpośrednie postępowania opiekuńcze prowadzone na podstawie art. 111 KRO...",
      "patterns": [
        {"pattern": "kurator", "count": 30, "pct_group": "51%", "pct_total": "15%"},
        {"pattern": "zaniedbanie", "count": 28, "pct_group": "47%", "pct_total": "14%"}
      ],
      "judgments": [
        {
          "lp": 1,
          "case_number": "III Nsm 109/25",
          "date": "2025-08-20",
          "type": "Postanowienie",
          "court": "Sąd Rejonowy w Raciborzu / III Wydział Rodzinny",
          "keywords_bases": "władza rodzicielska | art. 111§1 kro"
        }
      ],
      "legal_acts": [
        {"act": "Kodeks rodzinny i opiekuńczy", "count": 46, "pct": "78%"}
      ],
      "courts": [
        {"court": "Sąd Rejonowy dla m. st. Warszawy", "count": 37, "pct": "63%"}
      ]
    }
  ],
  "cross_patterns": {
    "global_legal_acts": [
      {"act": "Kodeks rodzinny i opiekuńczy", "count": 183, "pct": "92%"}
    ],
    "top_judges": [
      {"judge": "Barbara Ciwińska", "count": 42, "pct": "21%"}
    ],
    "global_courts": [
      {"court": "Sąd Rejonowy dla m. st. Warszawy", "count": 51, "pct": "26%"}
    ],
    "search_contexts": [
      "1. Zaniedbanie obowiązków wychowawczych (65 orzeczeń, 33%) - najczęstsza przesłanka...",
      "2. Instytucja kuratora (61 orzeczeń, 31%) - nadzory kuratorskie..."
    ],
    "conclusions": [
      "1. Zawężenie frazy do art. 111 KRO przyniosło wzrost precyzji...",
      "2. 82% orzeczeń wydano przez sądy rejonowe..."
    ]
  },
  "disclaimer": null
}
```

**Uwagi:**
- `disclaimer: null` → domyślne zastrzeżenia w DOCX
- `patterns` - wzorce text mining z treści orzeczeń grupy
- `judgments` - pełna lista (nie pomijaj żadnego!)
- `legal_acts`, `courts` - top 5-8, sortowane malejąco
- `search_contexts` - lista numerowana, akapit na kontekst
- `conclusions` - lista numerowana, akapit na wniosek
