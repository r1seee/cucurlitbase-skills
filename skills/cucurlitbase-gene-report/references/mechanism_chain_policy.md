# Mechanism Chain Policy

Use this reference when converting sentence-level evidence into an A-B-C style reasoning chain.

## Goal

The mechanism chain should make the inference path explicit:

`Gene -> evidence event -> mechanism context -> trait`

Example:

`PAL -> transcriptional evidence -> cell wall / lignin / pectin -> Cell wall structure`

## Rules

- Treat the chain as an interpretation scaffold, not as proof.
- Preserve the original sentence and Chinese translation next to the chain.
- Keep the evidence event grounded in sentence cues, such as qRT-PCR, RNA-seq, QTL, GWAS, mutant, overexpression, or background mention.
- Use conservative wording when the sentence does not contain functional perturbation evidence.
- Do not infer a biochemical pathway solely from the gene symbol unless the sentence or external annotation supports it.

## Evidence Event Mapping

- qRT-PCR, RNA-seq, transcriptome, expression: `transcriptional evidence`
- QTL, GWAS, locus, linkage, candidate gene: `mapped candidate locus`
- knockout, overexpression, silencing, transgenic, CRISPR: `functional perturbation`
- review, reported, known, background mention: `literature mention`
- no clear cue: `unspecified evidence event`

## Report Integration

The Evidence Table must include `Mechanism Chain`.

The narrative should summarize chains at two levels:

- Sentence level: explain the strongest individual chains.
- Section level: aggregate repeated chains into a mechanism hypothesis and state what validation is missing.

## Boundary

Do not write `Gene A regulates trait B` from a chain alone. That wording requires functional perturbation or equivalent causal evidence.
