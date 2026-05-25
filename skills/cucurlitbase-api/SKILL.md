---
name: cucurlitbase-api
description: Query the live CucurLitBase REST API for cucurbit literature evidence. Use when Codex needs current data from `http://117.72.82.63:9003/CucurLitBase/` to browse supported species, traits, genes, or PMIDs; to render the trait catalog as a strict ASCII tree; to run one-filter or two-filter evidence queries among `gene`, `species`, `trait`, and `pmid`; or to answer requests like "list supported species", "show the trait taxonomy", "look up evidence for gene X", or "return the direct API query link".
---

# CucurLitBase API

Use this skill to query CucurLitBase through verified REST endpoints instead of guessing website contents from memory.

## Quick Start

Run the bundled script:

```bash
python scripts/query_cucurlitbase.py list species
python scripts/query_cucurlitbase.py list traits --limit 10
python scripts/query_cucurlitbase.py list traits --output tree --limit -1
python scripts/query_cucurlitbase.py search --gene 4CL --output json --limit 5
python scripts/query_cucurlitbase.py search --species Watermelon --gene 4-beta-glucanases
python scripts/query_cucurlitbase.py search --trait Texture --species "Bitter melon" --output report --limit 10
```

Read [references/api_docs.md](references/api_docs.md) only when you need the verified endpoint map or response-field caveats.
Read [references/usage_manual.md](references/usage_manual.md) when you need the formal scenario map or standard trigger phrases.
Read [references/output_layers.md](references/output_layers.md) when you need to decide which output surface to use.
Read [references/boundary_responses.md](references/boundary_responses.md) when the requested task is outside the current skill boundary.
Read [references/database_skill_design_supplement.md](references/database_skill_design_supplement.md) when adapting this pattern to other database skills or when reasoning about normalization, ranking, and exact retrieval boundaries.

## Workflow

1. Decide whether the user needs discovery or evidence retrieval.
2. If the user asks for the trait hierarchy, use `list traits --output tree`.
3. If the user may not know exact entity names, call `list` first.
4. If the user already has one or two exact filters, call `search` directly.
5. Default to `--output report` for user-facing answers so the section layout stays stable.
6. Keep distinctions between `Species`, `Gene`, `BFTName`, `pmid`, and `Sentence` explicit.
7. If the user asks for unsupported filter combinations, say so plainly and do not invent endpoints.

## Supported Tasks

### Browse catalogs

- `list species`
- `list traits`
- `list genes`
- `list pmids`

Use this when the user asks things like:

- "Show me the trait taxonomy in CucurLitBase"
- "List supported species first"
- "Give me the PMID catalog"

### Retrieve evidence by filters

Supported one-filter queries:

- `--gene`
- `--species`
- `--trait`
- `--pmid`

Supported two-filter queries:

- `gene + pmid`
- `gene + species`
- `pmid + species`
- `gene + trait`
- `pmid + trait`
- `species + trait`

Example:

```bash
python scripts/query_cucurlitbase.py search --trait Texture --species "Bitter melon" --output report --limit 10
```

## Output Handling

- Default to `--output summary` for exploration.
- Default to `--output report` for user-facing evidence delivery.
- Use `--output tree` for a strict ASCII hierarchy of `list traits`.
- Use `--output json` when the user needs raw records or when you need exact field names.
- Use `--limit -1` only when the user truly needs the full result set.
- If the result count is large, summarize counts and representative examples instead of dumping everything.

## Fixed Report Format

When using `--output report`, preserve the section order exactly:

1. `## Query`
2. `## API Links`
3. `## Summary`
4. `## Results`
5. `## Evidence` for search mode, or catalog rows for list mode
6. `## Notes`

The `## API Links` section must include:

- `api_page`
- `request_url`

This means the output includes a direct API jump link for the exact query.

## Guardrails

- Treat the API as live data. Re-query instead of relying on stale memory.
- Do not assume all endpoints share identical fields.
- Do not invent unsupported three-filter queries.
- Do not imply that tree output is available for every task; it currently supports the trait catalog only.
- If the site becomes unreachable, report the network failure clearly and stop at that boundary.

## Resources

- Script entrypoint: [scripts/query_cucurlitbase.py](scripts/query_cucurlitbase.py)
- Verified endpoint notes: [references/api_docs.md](references/api_docs.md)
- Usage manual and trigger phrases: [references/usage_manual.md](references/usage_manual.md)
- Output layering guide: [references/output_layers.md](references/output_layers.md)
- Boundary response patterns: [references/boundary_responses.md](references/boundary_responses.md)
- Reusable database-skill design notes: [references/database_skill_design_supplement.md](references/database_skill_design_supplement.md)
