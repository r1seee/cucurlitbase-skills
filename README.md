# CucurLitBase Skills

CucurLitBase Skills provides a set of Codex skills for querying CucurLitBase and turning cucurbit literature evidence into structured, researcher-facing reports.

These skills are designed for users who want to explore species, traits, genes, papers, and gene-trait evidence in CucurLitBase without manually assembling API calls or reformatting evidence tables.

## Skill index

| Skill | Status | Purpose | Trigger keywords |
| --- | --- | --- | --- |
| `cucurlitbase-api` | Stable | Query CucurLitBase REST API for species, traits, genes, PMIDs, evidence records, and strict ASCII trait trees. | "list species", "trait tree", "search CucurLitBase", "API link", "PMID query" |
| `cucurlitbase-report` | Stable | Convert CucurLitBase query results into a fixed-format evidence summary with stable sections and source links. | "standard report", "summarize CucurLitBase results", "fixed format", "evidence summary" |
| `cucurlitbase-gene-report` | Advanced | Generate researcher-facing gene reports with PubMed metadata, evidence tables, figures, DOCX rendering, peer-gene comparison, mechanism chains, and enrichment guidance. | "deep gene report", "Watermelon PAL report", "same-trait peer genes", "mechanism chain", "DOCX report" |

### `cucurlitbase-api`

Use this skill for direct database exploration and evidence retrieval.

Typical tasks:

- List supported species, traits, genes, and PMIDs.
- Render the CucurLitBase trait catalog as an ASCII tree.
- Query evidence by gene, species, trait, PMID, or supported two-filter combinations.
- Return direct API links for reproducible queries.

### `cucurlitbase-report`

Use this skill when you want CucurLitBase query results summarized in a fixed, predictable format.

Typical tasks:

- Convert raw CucurLitBase JSON into a readable evidence summary.
- Keep query links, result counts, records, and caveats in a stable section order.
- Avoid inconsistent answer formats across repeated searches.

### `cucurlitbase-gene-report`

Use this skill for deep reports about one gene in one species.

Typical tasks:

- Generate a multi-section gene evidence report.
- Add PubMed metadata such as paper title, journal, publication year, DOI, and PMID.
- Preserve original evidence sentences and Chinese translations.
- Classify evidence strength and mechanism categories.
- Build sentence-level mechanism chains.
- Generate figures and render the report to DOCX.
- Compare the target gene with other genes under the same trait.
- Add external database enrichment guidance when CucurLitBase evidence is sparse.

## Installation

Clone this repository:

```powershell
git clone https://github.com/r1seee/cucurlitbase-skills.git
cd cucurlitbase-skills
```

Copy the skill folders into your local Codex skills directory:

```powershell
Copy-Item -Recurse -Force .\skills\cucurlitbase-api $env:USERPROFILE\.codex\skills\
Copy-Item -Recurse -Force .\skills\cucurlitbase-report $env:USERPROFILE\.codex\skills\
Copy-Item -Recurse -Force .\skills\cucurlitbase-gene-report $env:USERPROFILE\.codex\skills\
```

Start a new Codex conversation after installation so the skills can be discovered.

## Example Prompts

### Explore CucurLitBase

```text
Use cucurlitbase-api to list all supported species.
```

```text
Use cucurlitbase-api to show the trait hierarchy as an ASCII tree.
```

```text
Use cucurlitbase-api to search Watermelon + PAL and include the direct API link.
```

```text
Use cucurlitbase-api to find CucurLitBase records for Sugar content + PMID 31829140.
```

### Summarize Evidence

```text
Use cucurlitbase-report to summarize the CucurLitBase results for Watermelon + PAL in the standard format.
```

```text
Use cucurlitbase-report to turn this CucurLitBase JSON result into a user-facing evidence report.
```

### Generate Deep Gene Reports

```text
Use cucurlitbase-gene-report to generate a deep report for Watermelon PAL.
```

```text
Use cucurlitbase-gene-report to create a DOCX report for Watermelon PAL with figures, evidence table, and source links.
```

```text
Use cucurlitbase-gene-report to analyze Watermelon PAL and include same-trait peer genes.
```

```text
Use cucurlitbase-gene-report to add external database enrichment if CucurLitBase evidence is sparse.
```

## Deep Report Features

The deep gene report skill is designed to produce research-style outputs rather than short database summaries.

It can include:

- Chinese academic section headings.
- Query provenance and direct API links.
- Evidence table with original sentence, Chinese translation, paper title, journal, year, PMID, mechanism category, evidence strength, and mechanism chain.
- Numbered figures with captions and in-text `Fig. x` references.
- Trait distribution, mechanism distribution, evidence-strength distribution, publication timeline, trait-mechanism heatmap, trait-strength heatmap, and PMID-trait matrix.
- Same-trait peer-gene comparison.
- Research gaps and follow-up experiment suggestions.
- Optional external enrichment from official sources such as UniProt/Swiss-Prot and NCBI.

## Evidence Interpretation Boundaries

These skills help retrieve, organize, and interpret literature evidence, but they should not turn weak database mentions into strong biological claims.

Important boundaries:

- CucurLitBase is the primary evidence source.
- External databases provide supporting annotation and should be reported separately.
- Mechanism chains are reasoning scaffolds, not causal proof.
- Causal language requires functional perturbation, genetic validation, or equivalent evidence.
- BFT trait trees should only be drawn when real hierarchy data is available.
