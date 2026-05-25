# Finalization Workflow

The script creates a reproducible evidence-and-analysis packet. A final researcher-facing report still needs an agent pass because faithful translation and biological synthesis require language understanding and claim auditing.

Hard rule: do not deliver a final report if `translation_status = missing` remains in `data/evidence_enriched.json` or in the evidence table.

## 1. Run the builder

```bash
python scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_deep --limit -1
```

## 2. Complete translations

Open `data/translations_template.json`.

For each key:

- translate the original sentence faithfully into Chinese
- preserve gene names, trait names, abbreviations, and experimental terms
- do not add interpretation inside the translation field

Then rerun the builder with:

```bash
python scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_final --limit -1 --translations-json outputs/watermelon_pal_deep/data/translations_template.json
```

If the user is interacting through Codex, Codex should fill the translations directly as part of using the skill. The phrase "agent completion" means the Codex agent performs this step; it should not be left for the end user unless the user explicitly wants to review translations manually.

## 3. Audit mechanism labels

The script labels mechanisms with broad keyword rules. Before final delivery:

- inspect `mechanism_category`
- inspect `evidence_strength`
- downgrade weak claims
- keep direct evidence separate from expression association or background mention

## 4. Expand narrative sections

The generated `report.md` contains automatic analysis, but final delivery should still strengthen it:

- rewrite the executive summary in Chinese
- expand trait-level and mechanism-level synthesis into researcher-level prose
- add caveats for uncertain categories and weak evidence
- explain why the figures matter instead of merely showing them
- turn "Research Gaps and Follow-up" into a concrete research plan
- keep PMID and original sentence traceability

Minimum final-report analysis:

- What trait signal is most concentrated, and whether that concentration is meaningful or database-driven.
- Which mechanism category is plausible, which is only a sorting label, and which records need manual review.
- Whether evidence supports causal language, association language, or only candidate-gene language.
- What the year distribution suggests and what it does not prove.
- What external databases or experiments are needed next.

## 5. Deliver report packet

Final packet should include:

- `report.docx`
- `report.md`
- `figures/`
- `data/evidence_enriched.json`
- `data/query.json`

Do not deliver DOCX alone when the user needs auditability.
