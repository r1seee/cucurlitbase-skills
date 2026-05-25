# Scenario Selection Guide

Use this guide to choose CucurLitBase report scenarios that make the database most useful.

## Strong Scenarios

These scenarios fit CucurLitBase well because the database is organized around species, genes, traits, PMIDs, and evidence sentences.

1. Species + gene deep dossier
   - Best when the user has a target gene and wants literature evidence, mechanisms, and follow-up experiments.

2. Species + trait research map
   - Best when the user studies a crop phenotype such as watermelon stress resistance.
   - Output should rank genes, PMIDs, mechanisms, and evidence strength under the trait.

3. Trait + gene mechanism audit
   - Best for checking whether a claimed gene-trait relationship is directly supported.

4. Trait-centered peer-gene comparison
   - Best for asking whether the target gene is central or peripheral under the same phenotype.
   - Use `searchbytraitandspecies/` to find other genes associated with the same trait and species.

5. PMID-centered evidence verification
   - Best for checking whether one paper truly supports a gene-trait claim.

## Weaker Scenarios

These can be supported, but require careful caveats:

- Broad gene function reports with no species or trait context.
- Pathway-level claims without external database enrichment.
- BFT tree reports when the hierarchy is unavailable.
- Isoform/locus reports without external gene ID normalization.

## Recommended Expansion Direction

For database usefulness, prioritize these subskills next:

1. `species-trait-report`: analyze one species and one phenotype, rank associated genes and papers.
2. `trait-peer-gene-comparison`: compare a target gene against other genes under the same trait.
3. `pmid-evidence-audit`: verify whether a specific paper supports a claimed gene-trait-mechanism relationship.
4. `external-enrichment-tool`: normalize gene/protein IDs and fetch UniProt/NCBI/InterPro context.

The current `cucurlitbase-gene-report` should call the trait-peer-gene comparison as a module, not replace the main single-gene report.
