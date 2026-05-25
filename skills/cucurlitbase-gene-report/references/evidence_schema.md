# Evidence Schema

Each evidence record in `data/evidence_enriched.json` uses this schema.

Required fields:

- `index`: stable row index in the report packet
- `translation_key`: stable key used by `data/translations_template.json`
- `species`: common species name from CucurLitBase
- `scientific_name`: scientific name from CucurLitBase
- `gene`: gene string from CucurLitBase
- `trait`: trait or BFT name
- `pmid`: PubMed ID
- `title`: PubMed title when enrichment succeeds
- `journal`: PubMed journal when enrichment succeeds
- `year`: publication year when enrichment succeeds
- `doi`: DOI when available
- `pubmed_url`: direct PubMed URL
- `original_sentence`: source evidence sentence from CucurLitBase
- `translation_zh`: Chinese translation field; empty until a translation JSON is supplied
- `translation_status`: `provided` or `missing`
- `mechanism_category`: mechanism class assigned by rules or agent review
- `evidence_strength`: evidence strength class
- `mechanism_chain`: sentence-level A-B-C inference scaffold in the form `gene -> evidence event -> mechanism context -> trait`

Optional companion file:

- `data/trait_peer_genes.json`: generated when `--include-trait-peer-genes` is used. Contains same-species, same-trait peer genes, evidence-record counts, PMIDs, and the direct trait-species query URL.

Mechanism categories are intentionally broad in the first pass. For publication-grade analysis, the agent should audit each category against the original sentence and PubMed abstract when available.
Final reports must not contain `translation_status = missing`.
Mechanism chains must not be treated as causal proof unless the underlying sentence contains functional perturbation or equivalent causal evidence.
