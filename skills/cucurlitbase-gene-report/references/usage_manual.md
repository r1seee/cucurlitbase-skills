# CucurLitBase Gene Report Usage Manual

## Purpose

Build a researcher-facing report packet for one species plus one gene.

This skill is for questions like:

- "生成 Watermelon PAL 的深度调研报告"
- "帮我整理西瓜中 PAL 基因的文献证据、机制分类和图表"
- "我要一个 3-4 页 Word 量级的基因调研报告"

## Minimal command

```bash
python scripts/build_gene_report.py --species Watermelon --gene PAL --output-dir outputs/watermelon_pal_deep --limit -1
```

## Generated packet

The output directory contains:

- `report.docx`
- `report.md`
- `data/evidence_enriched.json`
- `data/translations_template.json`
- `data/query.json`
- `figures/*.png`
- `cache/pubmed/*.json`

## Recommended workflow

1. Run the builder.
2. Check `data/evidence_enriched.json`.
3. Fill `data/translations_template.json` with faithful Chinese translations. When Codex is using the skill, Codex should perform this step unless the user asks to translate manually.
4. Rerun the builder with `--translations-json`.
5. Audit mechanism categories and evidence strength.
6. Expand `report.md` into `final_report.md` with trait interpretation, mechanism interpretation, evidence-strength caveats, timeline interpretation, and specific research gaps. Use `###` subsections so the DOCX has `1.1`-style hierarchy.
7. Render `final_report.md` to `final_report.docx`.
8. Run the quality gate.
9. Deliver the full packet, not only the DOCX, when auditability matters.

The first script run is an evidence-and-analysis draft. The final report must not contain empty translations, translation placeholders, or a shallow "Research Gaps" section.
For family-level symbols such as `PAL`, add the optional gene family dossier when isoforms, loci, orthologs, domains, or experiment prioritization matter.

## Finalization commands

```bash
python scripts/render_markdown_docx.py --markdown outputs/watermelon_pal_deep/final_report.md --output-docx outputs/watermelon_pal_deep/final_report.docx
python scripts/check_gene_report_quality.py --report-md outputs/watermelon_pal_deep/final_report.md --evidence-json outputs/watermelon_pal_deep/data/evidence_enriched.json
```

## Sharing this skill

Share the whole folder:

```text
cucurlitbase-gene-report/
```

It should be placed under:

```text
<CODEX_HOME>/skills/
```

For a complete CucurLitBase skill suite, share these folders together:

- `cucurlitbase-api`
- `cucurlitbase-report`
- `cucurlitbase-gene-report`

Do not share only `SKILL.md`; the scripts and references are required.
