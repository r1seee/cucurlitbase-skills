# Deep Gene Report Contract

Use this contract for a researcher-facing species plus gene report.

## Default Target

- length: 4-7 Word pages for `deep` reports when enough evidence is available
- outputs: `report.docx`, `report.md`, `final_report.docx`, `final_report.md`, `figures/`, `data/evidence_enriched.json`
- language: Chinese narrative with original English evidence preserved
- hierarchy: `#` title, `##` sections, `###` subsections, optional `####` detailed subsections
- DOCX: render with `scripts/render_markdown_docx.py`, not ad hoc manual conversion
- figures: each embedded image must have a numbered `Fig. x.` caption and at least one prose citation using the same label

## Required Sections

1. 查询范围与证据来源
2. 摘要与结论边界
3. 证据基础与来源结构
   - 证据数量概览
   - 期刊来源与证据可靠性概览
   - 期刊-PMID 对照表
   - 文本证据表
4. 图表结果与时间分布解释
5. 性状证据主线
6. 机制证据综合
7. 研究局限与后续验证方案
8. 附录：来源链接

Optional section:

- 基因家族补充分析, required when the query is family-level or the user asks for isoforms, loci, orthologs, conserved domains, or experiment priority.
- BFT 性状层级定位, required only when a real BFT hierarchy is available.
- 同表型相关基因背景, recommended when `--include-trait-peer-genes` is used.
- 外源数据库补充证据, recommended when CucurLitBase evidence is sparse or the user requests protein/domain/pathway context.

## Required Evidence Table Fields

- Original Sentence
- Chinese Translation
- Paper Title
- Mechanism Category
- Evidence Strength
- Mechanism Chain
- PMID
- Journal
- Year
- Source URL

## Journal and Source Requirements

- Every text-evidence row must include journal name, publication year, PMID, and source URL when PubMed enrichment succeeds.
- The `期刊来源与证据可靠性概览` section must summarize journal distribution and show which PMIDs came from which journals.
- Do not hide journal names only in appendix links.

## Analysis Storyline

1. Establish query scope and evidence boundary.
2. Give the main biological interpretation and claim strength.
3. Present the evidence base first: quantitative overview, journal/PMID map, and evidence table.
4. Present figures and timeline interpretation before the detailed biological analysis.
5. Move from trait evidence to mechanism synthesis.
6. End with gaps, next experiments, and source links.

Do not create a standalone `Literature Timeline` chapter. Timeline interpretation belongs under `图表结果与时间分布解释`.

## Agent Responsibilities After Running the Script

- Complete empty `translation_zh` fields with faithful Chinese translation.
- Rerun the builder with `--translations-json` so the final `report.md` and `report.docx` contain translations.
- Preserve `Paper Title` and `Mechanism Chain` in the final evidence table.
- Use `mechanism_chain_policy.md` to distinguish sentence-grounded reasoning chains from causal conclusions.
- Use `external_database_enrichment.md` when the CucurLitBase evidence base is too small for a full mechanism report.
- Audit mechanism category and evidence strength.
- Expand executive summary, trait analysis, mechanism synthesis, timeline interpretation, and research gaps into researcher-level prose.
- Explain figures in prose; do not treat images as self-explanatory.
- Cite numbered figures in the analysis text, not only in captions.
- Use `###` subsections so the DOCX renderer can create `1.1`-style hierarchy.
- Keep all claims traceable to PMID and original sentence.
- Avoid conversational or template-like phrasing such as `不是...而是...`, `值得注意的是`, and `我们可以看到`.

## Depth Requirements

Read `depth_expansion_contract.md`. The final report should include paper-level, trait-level, mechanism-level, evidence-strength, temporal, and experimental-priority synthesis. Do not deliver a report that only restates the evidence table.

Do not present heuristic categories as final biological truth without review.
Do not deliver a final report with translation placeholders, empty translation fields, or shallow bullet-point gaps.
