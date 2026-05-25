# CucurLitBase Skills

This repository contains Codex skills for querying and analyzing CucurLitBase. It is intended to be installed as source skill folders, not as a zip package.

## What Is Included

- `cucurlitbase-api`: queries the live CucurLitBase REST API for species, traits, genes, PMIDs, evidence records, and strict ASCII trait trees.
- `cucurlitbase-report`: converts CucurLitBase query results into a stable, user-facing evidence summary.
- `cucurlitbase-gene-report`: generates researcher-facing gene evidence reports with PubMed metadata, paper titles, evidence tables, figures, DOCX rendering, same-trait peer-gene comparison, sentence-level mechanism chains, and external database enrichment guidance.

## Repository Layout

```text
skills/
  cucurlitbase-api/
  cucurlitbase-report/
  cucurlitbase-gene-report/
README.md
.gitignore
```

The repository should not store generated report outputs, temporary files, or zip archives. Install the skills directly from the `skills/` directory.

## Installation

Clone the repository:

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

Restart or open a new Codex conversation so the skills are discovered.

## Skill Usage Examples

After installation, use the skills through natural-language requests in Codex.

### API Queries

Example prompts:

- `Use cucurlitbase-api to list all supported species.`
- `Use cucurlitbase-api to show the CucurLitBase trait tree.`
- `Use cucurlitbase-api to search Watermelon + PAL and include the direct API link.`
- `Use cucurlitbase-api to find records for trait Texture in Bitter melon.`
- `Use cucurlitbase-api to query PMID 31829140.`

### Fixed-Format Evidence Summaries

Example prompts:

- `Use cucurlitbase-report to summarize the CucurLitBase results for Watermelon + PAL.`
- `Use cucurlitbase-report to convert this CucurLitBase JSON result into the standard report format.`

### Deep Gene Reports

Example prompts:

- `Use cucurlitbase-gene-report to generate a deep report for Watermelon PAL.`
- `Use cucurlitbase-gene-report to create a DOCX report for Watermelon PAL, including figures and evidence table.`
- `Use cucurlitbase-gene-report to analyze Watermelon PAL and include same-trait peer genes.`
- `Use cucurlitbase-gene-report to add external database enrichment when CucurLitBase evidence is sparse.`

Expected report features:

- Chinese academic section headings.
- Evidence table with original sentence, Chinese translation, paper title, journal, year, PMID, evidence strength, mechanism category, and mechanism chain.
- Numbered figures with captions and in-text `Fig. x` references.
- Trait distribution, mechanism distribution, evidence-strength distribution, publication timeline, trait-mechanism heatmap, trait-strength heatmap, and PMID-trait matrix.
- Same-trait peer-gene comparison when relevant.
- Conservative claim language based on evidence strength.
- Optional external enrichment from official sources such as UniProt/Swiss-Prot and NCBI when CucurLitBase evidence is insufficient.

## Design Boundaries

- CucurLitBase remains the primary evidence source.
- External databases are supplemental and must be clearly separated from CucurLitBase literature evidence.
- GeneCards is not treated as a default automated source because structured access has licensing and applicability constraints.
- BFT trait trees should only be drawn from real trait hierarchy data; do not infer hierarchy from trait names.
- Mechanism chains are reasoning scaffolds, not causal proof. Causal claims require functional perturbation or equivalent evidence.

## Development Notes

- Keep `SKILL.md` concise and place detailed behavior rules in `references/`.
- Keep reusable deterministic logic in `scripts/`.
- Do not commit generated outputs, temporary test folders, or zip archives.
- Validate changed skills with the Codex `skill-creator` quick validation script before release.
