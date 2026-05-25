---
name: cucurlitbase-gene-report
description: Build deep researcher-facing CucurLitBase gene reports for a species plus gene query. Use when the user wants a multi-page DOCX/Markdown literature evidence report with CucurLitBase records, PubMed journal/year/title enrichment, paper titles, sentence-level mechanism chains, same-trait peer-gene comparison, mechanism classification, evidence strength, figures, source links, thesis-like DOCX formatting, external database enrichment guidance, and optional gene-family dossier sections for isoforms, loci, orthologs, domains, and follow-up experiment prioritization.
---

# CucurLitBase Gene Report

Use this skill when the user wants a research-style report for one gene in one species, not a short API answer.

## Workflow

1. Run the report builder script with `--species`, `--gene`, and `--output-dir`.
2. Inspect `data/evidence_enriched.json`.
3. Complete all missing `translation_zh` fields yourself when producing a final report. Do not deliver a final report with empty translations.
4. Rerun the builder with `--translations-json` after translations are filled.
5. Audit heuristic mechanism category and evidence strength labels.
6. Read `references/final_report_playbook.md`, `references/depth_expansion_contract.md`, and `references/docx_format_contract.md`, then expand `report.md` into researcher-level Chinese analysis with `##`, `###`, and optional `####` hierarchy.
7. If the query uses a family-level symbol or the user asks for isoforms, loci, orthologs, domains, or experiment priorities, read `references/family_dossier_module.md` and add a gene-family dossier section.
8. Render expanded `final_report.md` with `scripts/render_markdown_docx.py`.
9. Run `scripts/check_gene_report_quality.py` before delivery.
10. Keep `final_report.docx`, `final_report.md`, `report.docx`, `report.md`, `figures/`, and `data/` together as the report packet.

## Quick Start

```bash
python scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_deep --limit -1
```

For same-trait peer-gene comparison:

```bash
python scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_deep --limit -1 --include-trait-peer-genes
```

Expected outputs:

- `report.docx`
- `report.md`
- `data/evidence_enriched.json`
- `data/translations_template.json`
- `data/query.json`
- `figures/*.png`
- `cache/pubmed/*.json`

For final report rendering:

```bash
python scripts/render_markdown_docx.py --markdown outputs/watermelon_pal_deep/final_report.md --output-docx outputs/watermelon_pal_deep/final_report.docx
python scripts/check_gene_report_quality.py --report-md outputs/watermelon_pal_deep/final_report.md --evidence-json outputs/watermelon_pal_deep/data/evidence_enriched.json
```

## Report Standard

Read these references before changing the report behavior:

- [references/report_contract_gene_deep.md](references/report_contract_gene_deep.md)
- [references/evidence_schema.md](references/evidence_schema.md)
- [references/figure_style_contract.md](references/figure_style_contract.md)
- [references/normalization_policy.md](references/normalization_policy.md)
- [references/finalization_workflow.md](references/finalization_workflow.md)
- [references/final_report_playbook.md](references/final_report_playbook.md)
- [references/depth_expansion_contract.md](references/depth_expansion_contract.md)
- [references/external_database_enrichment.md](references/external_database_enrichment.md)
- [references/mechanism_chain_policy.md](references/mechanism_chain_policy.md)
- [references/scenario_selection_guide.md](references/scenario_selection_guide.md)
- [references/docx_format_contract.md](references/docx_format_contract.md)
- [references/family_dossier_module.md](references/family_dossier_module.md)
- [references/boundary_responses.md](references/boundary_responses.md)
- [references/usage_manual.md](references/usage_manual.md)

## Current Boundaries

- PubMed enrichment uses NCBI ESummary and may fail if network access is unavailable.
- DOCX generation uses a minimal OpenXML writer because `python-docx` may not be installed.
- `translation_zh` is a required final-report field. The deterministic script leaves it empty unless a translation JSON is supplied; the agent must complete it before final delivery.
- Mechanism classification and evidence strength are first-pass labels. Audit them before writing biological claims.
- A final answer must contain analysis: trait interpretation, mechanism interpretation, evidence-strength caveats, timeline interpretation, and follow-up research gaps.
- A final single-gene report must follow the storyline: query scope -> executive claim -> evidence/source map with evidence table -> figures and timeline interpretation -> trait mainline -> mechanism synthesis -> gaps.
- A final report must contain real heading hierarchy. If `final_report.md` only uses `##` headings, fix the Markdown before rendering.
- A final report must expose journal names and publication years in the evidence table or evidence cards, plus a `期刊来源与证据可靠性概览` subsection.
- The Evidence Table must include `Paper Title` and `Mechanism Chain`.
- If the user needs comparison under the same phenotype, run the builder with `--include-trait-peer-genes` and discuss other genes associated with the target trait.
- If CucurLitBase evidence is sparse, read `references/external_database_enrichment.md` and use official programmatic sources such as UniProt and NCBI before adding external claims.
- Do not create a standalone `Literature Timeline` section; integrate timeline interpretation into the figure analysis.
- Number every embedded figure as `Fig. x.`, write a caption immediately below it, and cite the same figure label in the analysis prose.
- Use Chinese academic headings consistently. Avoid headings such as `最强可辩护结论`, `为什么选择 PAL`, `一句话总结`, and `亮点`.
- Avoid template-like or conversational writing patterns, especially `不是...而是...`, `值得注意的是`, and `我们可以看到`; use evidence-calibrated academic prose.
- Use a BFT tree only when a real trait hierarchy is available. Do not fabricate hierarchy from trait names.
- If no records, too few records, weak evidence, missing translations, or unreachable external services block a final report, use `references/boundary_responses.md` instead of padding unsupported claims.

## Resources

- Script: [scripts/build_gene_report.py](scripts/build_gene_report.py)
- Renderer: [scripts/render_markdown_docx.py](scripts/render_markdown_docx.py)
- Quality gate: [scripts/check_gene_report_quality.py](scripts/check_gene_report_quality.py)
- Deep report contract: [references/report_contract_gene_deep.md](references/report_contract_gene_deep.md)
- Evidence schema: [references/evidence_schema.md](references/evidence_schema.md)
- Figure style: [references/figure_style_contract.md](references/figure_style_contract.md)
- Normalization policy: [references/normalization_policy.md](references/normalization_policy.md)
- Finalization workflow: [references/finalization_workflow.md](references/finalization_workflow.md)
- Final report playbook: [references/final_report_playbook.md](references/final_report_playbook.md)
- Depth expansion contract: [references/depth_expansion_contract.md](references/depth_expansion_contract.md)
- External database enrichment: [references/external_database_enrichment.md](references/external_database_enrichment.md)
- Mechanism chain policy: [references/mechanism_chain_policy.md](references/mechanism_chain_policy.md)
- Scenario selection guide: [references/scenario_selection_guide.md](references/scenario_selection_guide.md)
- DOCX format contract: [references/docx_format_contract.md](references/docx_format_contract.md)
- Gene family dossier module: [references/family_dossier_module.md](references/family_dossier_module.md)
- Boundary responses: [references/boundary_responses.md](references/boundary_responses.md)
- Usage manual: [references/usage_manual.md](references/usage_manual.md)
