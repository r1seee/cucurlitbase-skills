# Boundary Responses

Use these responses when the requested final report cannot be completed honestly.

## No CucurLitBase Records

`CucurLitBase did not return records for this species-gene query. I can provide the exact request URL and suggest checking species names, gene aliases, or broader gene-family terms, but I should not generate a deep evidence report without source records.`

## Too Few Records for 3-4 Pages

`The evidence base is too small for a 3-4 page evidence-driven report without padding. I can produce a short evidence memo, list the missing evidence types, and suggest external databases or broader queries to expand the report.`

## Missing Translation

`The current report packet still has untranslated evidence sentences. I should complete faithful Chinese translations first, then rerun the report builder before calling this a final report.`

## Weak Evidence

`The current records do not support strong causal language. I will phrase the conclusion as association, candidate-gene evidence, or literature mention, and mark the functional-validation gap explicitly.`

## External Database Unreachable

`CucurLitBase evidence was collected, but external enrichment failed because the external service was unreachable. I can deliver the CucurLitBase-grounded report and mark PubMed or other database metadata as missing, or retry enrichment later.`

## User Requests Unsupported Generalization

`The current query only supports the specified species-gene context. I should not generalize this conclusion to other cucurbits or orthologs unless we query external orthology and functional databases.`

## Figure Requested Without Data

`The requested figure cannot be produced from the available records because the required field is missing or empty. I can generate a table of available fields and suggest which additional data would be needed for that visualization.`
