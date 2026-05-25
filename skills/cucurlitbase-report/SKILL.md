---
name: cucurlitbase-report
description: Turn CucurLitBase query results into a fixed-format user-facing report. Use when the user wants a stable evidence summary, trait report, species report, gene evidence brief, catalog report, or any CucurLitBase output whose section order and link fields should remain consistent across turns, especially for requests like "summarize this in a fixed template", "give me a trait report", or "keep the API jump link in the output".
---

# CucurLitBase Report

Use this skill only for presentation and reporting. Fetch data through the sibling `cucurlitbase-api` skill and keep the output format fixed.

## Quick Start

Use the installed main query script with `--output report`:

```bash
python ../cucurlitbase-api/scripts/query_cucurlitbase.py search --trait Texture --species "Bitter melon" --output report --limit 10
python ../cucurlitbase-api/scripts/query_cucurlitbase.py list traits --output report --limit 20
```

Read [references/output_contract.md](references/output_contract.md) when you need the exact section contract.
Read [../cucurlitbase-api/references/usage_manual.md](../cucurlitbase-api/references/usage_manual.md) when you need the scenario map or standard trigger phrases.

## Workflow

1. Identify whether the user wants a catalog report or an evidence report.
2. Use the sibling `cucurlitbase-api` script with `--output report`.
3. Preserve the section order from the script output.
4. If you need to add one sentence of interpretation, append it after the fixed report rather than rewriting the section layout.
5. Do not drop the API links section.

## Use Cases

- trait-centric evidence digests
- species plus trait reports
- gene lookup reports for end users
- standardized catalog reports for species, traits, genes, or PMIDs

## Guardrails

- Do not invent records that are absent from the API response.
- Do not silently remove `request_url`; it is the exact API jump link.
- Do not switch to free-form prose if the user explicitly wants stable formatting.
- If the user wants raw JSON instead of a report, use `cucurlitbase-api` directly and do not force this skill.
- If the user asks for a multi-page researcher-facing species-gene report with translation, figures, mechanism synthesis, or research gaps, route to `cucurlitbase-gene-report` instead of this brief fixed-format skill.

## Resources

- Output contract: [references/output_contract.md](references/output_contract.md)
- Data fetcher: `../cucurlitbase-api/scripts/query_cucurlitbase.py`
- Shared usage manual: [../cucurlitbase-api/references/usage_manual.md](../cucurlitbase-api/references/usage_manual.md)
