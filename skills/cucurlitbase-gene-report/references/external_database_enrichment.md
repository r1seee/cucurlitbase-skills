# External Database Enrichment

Use this reference when CucurLitBase evidence is sparse or when the user asks for a fuller gene dossier.

## Feasibility Summary

- UniProtKB / Swiss-Prot: feasible as a programmatic source. Use the official UniProt REST API. Prefer reviewed entries with `reviewed:true` when available, but do not assume a cucurbit gene has a reviewed Swiss-Prot record.
- NCBI: feasible as a programmatic source through E-utilities and NCBI Datasets. Use it for PubMed, Gene, Protein, Nucleotide, and taxonomy-linked metadata.
- GeneCards: not a default automated source for this plant-focused workflow. GeneCards is human-gene centric and programmatic access to the relational database is a licensed/commercial use case. Use only as a manual or authorized source when the user explicitly asks and the target is relevant.
- InterPro / QuickGO / STRING: feasible optional sources for domains, GO terms, and interaction context when UniProt/NCBI identifiers can be resolved.

## Trigger Conditions

Use external enrichment when one of these is true:

- CucurLitBase returns fewer than three evidence records.
- Evidence is mostly `literature mention` or `background mention`.
- The user asks for protein domain, pathway, ortholog, locus, isoform, or experiment-priority analysis.
- The gene symbol is family-level and CucurLitBase records cannot identify isoforms.

## Required Provenance

Every external claim must include:

- database name
- query string or accession
- URL
- retrieved identifier
- evidence type
- whether the source is reviewed/manual, computational, or literature-derived

Do not merge CucurLitBase evidence and external database annotations into one undifferentiated claim. Keep a separate section named `外源数据库补充证据`.

## Recommended Source Order

1. CucurLitBase: trait-gene-paper evidence.
2. PubMed / NCBI E-utilities: paper metadata, abstract, linked Gene/Protein records when available.
3. UniProtKB / Swiss-Prot / TrEMBL: protein name, organism, reviewed status, function comments, domains/features, cross-references.
4. InterPro / Pfam / QuickGO: domain and GO context when protein accession is resolved.
5. STRING or species-specific plant databases: interaction or orthology context, clearly marked as external and lower-priority unless experimentally supported.

## Report Integration

Add a section after `机制证据综合`:

```markdown
## 外源数据库补充证据
### UniProt/Swiss-Prot 蛋白功能注释
### NCBI Gene/Protein 标识符与序列信息
### 结构域、GO 与通路补充
### 外源证据与 CucurLitBase 文献证据的一致性
```

In the analysis, compare external annotations against CucurLitBase evidence:

- Concordant: external function/domain supports the same mechanism suggested by text evidence.
- Complementary: external source adds protein/domain context but does not directly validate the trait.
- Conflicting or weak: external annotation is broad, inferred, or from another species; keep conclusions conservative.

## Boundary Language

If external sources cannot resolve the gene:

`CucurLitBase 当前记录不足以支持完整机制报告，且外源数据库未能稳定解析该基因符号。报告保留 CucurLitBase 证据结论，并建议后续先完成基因 ID、蛋白 accession 和同源关系标准化。`

If GeneCards is requested:

`GeneCards 主要面向人类基因，且结构化数据库访问具有授权边界。本报告不把 GeneCards 作为默认自动化来源；如需使用，应作为人工核查或授权数据源，并明确其与植物基因证据之间的适用性差异。`
