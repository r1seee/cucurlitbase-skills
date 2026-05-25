# Final Report Playbook

Use this playbook when turning the generated evidence packet into a final researcher-facing Chinese report.

## Target Output

The final report should read like a compact literature investigation and experiment-planning dossier prepared for a biologist.

Minimum standard:

- 4-7 Word pages for deep reports when enough evidence is available.
- At least 4500 Chinese characters for normal evidence sets.
- At least 900 Chinese characters in `研究局限与后续验证方案`.
- Chinese analytical prose with original English evidence preserved in the table.
- Chinese academic headings throughout the report.
- Figures embedded, numbered, captioned, and cited in prose.
- PMID traceability for every substantive claim.
- Journal name and publication year shown for every text-evidence item.
- Paper title and sentence-level mechanism chain shown for every text-evidence item.

If CucurLitBase returns fewer than three records, state that the evidence base is limited and downgrade the report length expectation rather than padding unsupported claims.

## Heading Policy

Use Chinese academic headings consistently. English headings are not allowed except for fixed database names, gene symbols, method names, and `Fig. x` labels.

Required top-level headings:

1. 查询范围与证据来源
2. 摘要与结论边界
3. 证据基础与来源结构
4. 图表结果与时间分布解释
5. 性状证据主线
6. 机制证据综合
7. 研究局限与后续验证方案
8. 附录：来源链接

Avoid rhetorical or colloquial headings such as `最强可辩护结论`, `为什么选择 PAL`, `一句话总结`, `亮点`, and `看图说话`.

## Translation Rules

Translate every `original_sentence` into `translation_zh`.

Required behavior:

- Keep gene symbols, species names, trait names, abbreviations, and method terms stable.
- Translate the sentence faithfully; do not add interpretation inside the translation field.
- Put interpretation in the analysis sections.
- Mark uncertainty in the analysis, not by weakening the translation.
- Do not leave empty translations in the final report.

The script cannot call the Codex language model by itself. Therefore, when this skill is used inside Codex, Codex must perform the translation step before final delivery.

## Analysis Rules

The final narrative must answer these questions:

1. What is the dominant trait signal?
2. Does the dominant trait signal reflect strong biology, database record density, or repeated evidence from the same paper?
3. Which mechanism categories are plausible, and which are only heuristic sorting labels?
4. Does the evidence support causal language, association language, or candidate-gene language?
5. Are the strongest conclusions supported by functional validation, expression evidence, genetic mapping, or background mention?
6. What does the publication timeline suggest, and what does it not prove?
7. What external databases should be queried next for gene structure, protein function, pathway context, and ortholog conservation?
8. What experiments would a researcher reasonably design next?
9. Which journals and years support the strongest claims?
10. Are there other genes under the same trait that should be used as comparison background?
11. Does the sentence-level mechanism chain support only association, or does it support a causal statement?

Read `depth_expansion_contract.md` before writing the final report.

## Academic Writing Style

Write like a short experimental report or literature-review dossier.

Required style:

- Use paragraph logic: claim, evidence, limitation, implication.
- Prefer calibrated verbs: `supports`, `suggests`, `is associated with`, `is consistent with`, `requires validation`.
- State evidence boundaries explicitly when the database record does not support causal language.
- Vary sentence structure across sections; avoid repeating the same transition template.
- Keep interpretation separate from translation fields and table metadata.

Forbidden or discouraged style:

- Do not use `不是...而是...` contrast sentences.
- Avoid generic openings such as `值得注意的是` and `我们可以看到`.
- Avoid conversational phrases such as `简单来说`, `换句话说`, `这说明了`.
- Avoid empty methodological hedges. If uncertainty matters, name the exact missing evidence.
- Do not use slogan-like conclusions; each conclusion should be traceable to PMID-level evidence.

## Report Storyline

Use this order for the final single-gene report:

1. 查询范围与证据来源: define the species, gene, API URL, and evidence boundary.
2. 摘要与结论边界: state the main evidence-supported claim and the major limitation.
3. 证据基础与来源结构: show quantitative overview, journal/PMID map, and the evidence table before detailed interpretation.
4. 图表结果与时间分布解释: show the figures early and explain the publication timeline inside this section.
5. 性状证据主线: explain which phenotype/trait line carries the report.
6. 机制证据综合: connect evidence to pathways, regulation, or biochemical mechanisms.
7. 研究局限与后续验证方案: turn missing evidence into concrete next experiments.
8. 附录：来源链接: provide direct source links.

Do not create a standalone `Literature Timeline` section. Put timeline findings directly under `图表结果与时间分布解释`.

## Source Presentation Rules

Every evidence sentence must show:

- original sentence
- Chinese translation
- paper title
- sentence-level mechanism chain
- journal name
- publication year
- PMID
- source URL

The report must include a `期刊来源与证据可靠性概览` subsection under `证据基础与来源结构`. This subsection should summarize journal distribution, year distribution, and whether the strongest claims come from primary research, review articles, or contextual citations.

## Layout Rules

Write the final report with this Markdown hierarchy:

- `#` title
- `##` top-level sections
- `###` analytical subsections
- `####` fine-grained subsections when needed

The renderer turns this into `1`, `1.1`, and `1.1.1` numbering. If the Markdown only uses `##`, the DOCX can only contain one-level numbering.

Read `docx_format_contract.md` before rendering the final Word file.

## Optional Gene Family Dossier

For family-level symbols such as `PAL`, add a `## 基因家族补充分析` section when the user wants project-planning depth.

Use `family_dossier_module.md` to structure isoforms, genomic loci, orthologs, conserved domains, and experimental prioritization. Do not invent isoform IDs or locus positions without external evidence.

## Figure Interpretation

Every figure needs a prose explanation.

Each figure must have a caption immediately below the image:

```markdown
![trait_distribution](figures/trait_distribution.png)
Fig. 1. 查询基因相关性状证据分布。计数单位为 CucurLitBase 证据记录，而非独立实验数量。
```

Every numbered figure must be cited at least once in analysis prose, for example: `Fig. 1 显示...`.

Required default figures:

- Trait distribution: explain which trait dominates and whether it is supported by multiple PMIDs.
- Mechanism distribution: explain the top mechanism category and whether it remains heuristic.
- Evidence strength distribution: separate functional validation from expression-only and candidate-gene evidence.
- Publication timeline: report year span and peak year without treating record counts as field-wide publication volume.
- Trait-mechanism heatmap: identify high-density trait-mechanism combinations for detailed analysis.
- Trait-strength heatmap: determine which trait claims need conservative language.
- PMID-trait matrix: identify repeated records from the same paper.

## BFT Tree

A BFT tree is useful when the report analyzes a trait or when the query gene connects to several phenotype branches. Use it only when a real hierarchical trait list is available from CucurLitBase or provided by the user.

If no real hierarchy is available, do not fabricate parent-child relationships. State the limitation and use trait distribution plus trait-mechanism heatmaps instead.

## Same-Trait Peer Genes

When the report is intended for research planning, use `--include-trait-peer-genes` to add a `同表型相关基因背景` section.

This section should answer:

- Which other genes are associated with the same trait in the same species?
- Does the target gene have comparable evidence density, or is it peripheral relative to other genes?
- Are peer genes supported by stronger evidence types than the target gene?
- Should the target gene be studied as a primary candidate, pathway member, family member, or secondary comparison gene?

## External Database Enrichment

When CucurLitBase evidence is sparse, read `external_database_enrichment.md`.

Use official, programmatic sources first:

- UniProtKB / Swiss-Prot for protein annotation and reviewed status.
- NCBI E-utilities / NCBI Datasets for PubMed, Gene, Protein, Nucleotide, and taxonomy-linked records.
- InterPro / QuickGO when protein accessions are resolved.

Do not treat GeneCards as a default automated plant-gene source. Use it only as a manual or authorized source and state its applicability boundary.

## Claim Language

Use `regulates`, `controls`, or Chinese equivalents such as `调控` only when functional perturbation evidence is present.

Use `associated with`, `candidate for`, `may participate in`, or Chinese equivalents such as `相关`, `候选`, `可能参与` when evidence is expression-only, mapping-only, or background mention.

Use `证据不足以支持` when only weak mentions exist.

## Finalization Commands

After writing `final_report.md`, run:

```bash
python scripts/render_markdown_docx.py --markdown outputs/example/final_report.md --output-docx outputs/example/final_report.docx
```

Then run:

```bash
python scripts/check_gene_report_quality.py --report-md outputs/example/final_report.md --evidence-json outputs/example/data/evidence_enriched.json
```

Do not deliver the final report if the quality gate fails.
