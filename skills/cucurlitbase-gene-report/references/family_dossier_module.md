# Gene Family Dossier Module

Use this optional module when the user asks for isoforms, family members, genomic locations, orthologs, conserved domains, or experimental prioritization beyond CucurLitBase evidence.

This is especially useful for gene-family names such as `PAL`, `4CL`, `ACS`, `C4H`, or `POD`, where CucurLitBase records may refer to a family-level symbol rather than a single locus.

## When to add this module

Add a family-level dossier when:

- the gene query is a family symbol rather than a stable locus ID
- the final conclusion depends on which isoform or paralog is involved
- the user asks for follow-up experiments or candidate prioritization
- the report is intended for project planning rather than a short evidence digest

Do not add this module when the user only wants a quick CucurLitBase evidence summary.

## Required dossier sections

Use these subsections under a top-level `## Gene Family Dossier` section:

### Family Definition

State whether the query is a single gene, gene family, enzyme class, or ambiguous symbol.

### Candidate Isoforms and Loci

List candidate gene IDs, locus IDs, chromosome positions, and aliases. Include source database names and URLs.

### Protein Domain and Functional Annotation

Summarize conserved domains, enzyme class, GO terms, pathway membership, and UniProt or NCBI annotations when available.

### Orthology and Paralogy

Summarize within-species paralogs and cross-species orthologs. Do not assume one-to-one orthology without evidence.

### Evidence-to-Isoform Mapping

Map each CucurLitBase evidence sentence to a specific isoform only when the paper or external database supports that mapping. Otherwise mark it as family-level evidence.

### Experimental Prioritization

Rank candidate isoforms for follow-up experiments using:

- CucurLitBase evidence density
- trait relevance
- expression or perturbation evidence
- genomic position near relevant QTL or locus
- domain completeness
- ortholog support

## External sources

Use external sources only when live access is available or the user provides local files.

Suitable sources include:

- NCBI Gene / NCBI Datasets
- UniProt
- Ensembl Plants or Gramene
- Cucurbit Genomics Database if available
- PubMed abstracts or full texts
- GO / KEGG / Reactome where relevant

If external lookup fails, keep the dossier as a planned follow-up section and say which evidence is missing.
