# Resource Types - EU Publications Office

Full URI base: `http://publications.europa.eu/resource/authority/resource-type/`

Every code below was checked against the live SPARQL endpoint on 2026-10-19: the URI exists in the
resource-type authority table and the label is the table's English `skos:prefLabel`. A code that is
not in the table does not raise an error - the query simply returns nothing - so do not invent codes.
If you need a type that is not listed here, look it up first:

```sparql
SELECT ?l WHERE {
  <http://publications.europa.eu/resource/authority/resource-type/CODE>
    <http://www.w3.org/2004/02/skos/core#prefLabel> ?l
  FILTER(lang(?l) = "en")
}
```

An empty result means the code does not exist.

## Legislation

| Code | Label |
|---|---|
| `REG` | Regulation |
| `REG_IMPL` | Implementing regulation |
| `REG_DEL` | Delegated regulation |
| `DIR` | Directive |
| `DIR_IMPL` | Implementing directive |
| `DIR_DEL` | Delegated directive |
| `DEC` | Decision |
| `DEC_IMPL` | Implementing decision |
| `DEC_DEL` | Delegated decision |
| `DEC_FRAMW` | Framework decision |
| `RECO` | Recommendation |
| `OPIN` | Opinion |

## CJEU (Court of Justice of the EU)

| Code | Label |
|---|---|
| `JUDG` | Judgment |
| `ORDER` | Order |
| `OPIN_AG` | Opinion of the Advocate General |
| `VIEW_AG` | View of the Advocate General |
| `RULING` | Ruling |
| `INFO_JUDICIAL` | Judicial information |
| `DEC_NC` | Decision by national courts in the field of European Union law |
| `THIRDPARTY_PROCEED` | Third-party proceedings |

In a sample of 3 000 `cdm:case-law` works the most frequent types were `OPIN_AG`, `DEC_NC`, `JUDG`
and `ORDER`. To select case law as a whole, use the CDM class rather than a resource type:

| CDM class | Use |
|---|---|
| `cdm:case-law` | Case law (any document type) |
| `cdm:document_cjeu` | CJEU document |
| `cdm:summary_case-law` | Summary of case law |

## Other

| Code | Label |
|---|---|
| `CORRIGENDUM` | Corrigendum (always exclude with FILTER NOT EXISTS) |
| `PROP_REG` | Proposal for a regulation |
| `PROP_DIR` | Proposal for a directive |
| `PROP_DEC` | Proposal for a decision |
| `COMMUNIC` | Communication |
| `REPORT` | Report |
| `SWD` | Staff working document |
| `OJ` | Official Journal |

`COM`, `JOIN`, `SEC`, `OJ_L` and `OJ_C` are not codes in the resource-type table (checked
2026-10-19). For Commission documents use a type above (`PROP_REG`, `COMMUNIC`, `SWD` ...) or search
by the document number; for an Official Journal series filter on the OJ reference, not on the type.

## Usage examples

```sparql
-- Exclude corrigenda (best practice)
FILTER NOT EXISTS {
  ?work cdm:work_has_resource-type
        <http://publications.europa.eu/resource/authority/resource-type/CORRIGENDUM>
}

-- Multiple types with FILTER
FILTER(?type IN (
  <http://publications.europa.eu/resource/authority/resource-type/REG>,
  <http://publications.europa.eu/resource/authority/resource-type/DIR>
))
```
