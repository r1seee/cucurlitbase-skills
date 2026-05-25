# CucurLitBase Skill Manual

## 1. Purpose

This skill set is designed for two distinct but connected jobs:

- `cucurlitbase-api`: fetch live data from the CucurLitBase REST API
- `cucurlitbase-report`: present the fetched data in a stable, fixed-format report

Use the API skill when the task is primarily retrieval.
Use the report skill when the task is primarily presentation consistency.

## 2. Skill Split

| Skill | Primary role | Typical output |
| --- | --- | --- |
| `cucurlitbase-api` | browse catalogs, run one-filter or two-filter queries, return JSON/summary/report | raw JSON, compact summary, or fixed report |
| `cucurlitbase-report` | keep the user-facing layout stable across turns | fixed report only |

## 3. Supported Scenarios

### 3.1 Catalog discovery

Use when the user does not yet know the exact valid values.

Examples:

- view supported species
- view the trait taxonomy
- inspect the gene directory
- inspect the PMID catalog

### 3.2 Evidence lookup

Use when the user already has one or two query keys.

Supported single filters:

- `gene`
- `species`
- `trait`
- `pmid`

Supported two-filter combinations:

- `gene + pmid`
- `gene + species`
- `pmid + species`
- `gene + trait`
- `pmid + trait`
- `species + trait`

### 3.3 Fixed-format evidence delivery

Use when the user wants:

- a trait report
- a species report
- a gene evidence brief
- consistent output across multiple turns
- direct API links included in the answer

## 4. Standard Trigger Phrases

These are recommended user utterances that should trigger the skill reliably.

### 4.1 Trigger `cucurlitbase-api`

- `用 cucurlitbase 查一下有哪些 species`
- `用 cucurlitbase 看 trait taxonomy`
- `查一下 Watermelon 和 4-beta-glucanases 的证据`
- `查 trait=Texture, species=Bitter melon`
- `给我 4CL 的原始 json`
- `列出 CucurLitBase 支持的 PMID`
- `帮我生成这个查询对应的 API 链接`

### 4.2 Trigger `cucurlitbase-report`

- `把这个查询结果整理成固定格式报告`
- `给我一个 trait report`
- `按统一模板输出 species report`
- `不要自由发挥，按固定版式总结`
- `输出里保留 API 跳转链接`
- `把 CucurLitBase 结果整理得每次都一样`

## 5. Recommended Decision Rule

1. If the user is exploring valid values, start with `cucurlitbase-api` in `list` mode.
2. If the user has one or two exact filters, use `cucurlitbase-api` in `search` mode.
3. If the user wants hierarchy, use `list traits --output tree`.
4. If the user cares about stable presentation, use `--output report` or invoke `cucurlitbase-report`.
5. If the user explicitly asks for raw machine-readable data, return JSON instead of the report.

## 6. Output Contract

When using fixed reports, keep this order:

1. `## Query`
2. `## API Links`
3. `## Summary`
4. `## Results`
5. `## Evidence` for search mode
6. `## Notes`

The `## API Links` section must include:

- `api_page`
- `request_url`

`request_url` is the direct API jump link for the exact query.

## 7. Output Layers

Current output layers are:

- `json`
- `summary`
- `report`
- `tree`

Use them like this:

- `json`: raw machine-readable records
- `summary`: quick exploration
- `report`: stable user-facing delivery
- `tree`: ASCII hierarchy for `list traits`

Read [output_layers.md](output_layers.md) for the design rationale.

## 8. Non-Goals

This skill set currently does not cover:

- three-filter or higher-order query composition
- cross-database federation
- automatic semantic parsing into arbitrary hidden endpoints
- downstream statistical analysis beyond simple summarization

## 9. Example Commands

```bash
python scripts/query_cucurlitbase.py list traits --output report --limit 20
python scripts/query_cucurlitbase.py list traits --output tree --limit -1
python scripts/query_cucurlitbase.py list traits --output tree --tree-include-tags --limit -1
python scripts/query_cucurlitbase.py search --trait Texture --species "Bitter melon" --output report --limit 10
python scripts/query_cucurlitbase.py search --gene 4CL --output json --limit 5
```

## 10. Capability Coverage Matrix

Use the labels:

- `covered`
- `partially covered`
- `not covered`

| Scenario | Status | Notes |
| --- | --- | --- |
| List All Traits | covered | `list traits --output tree` provides a strict ASCII tree reconstructed from hierarchical tags |
| List All Species | covered | `list species` returns species and scientific names |
| Search by Trait | covered | supported as `search --trait <value>` |
| Trait and Gene | covered | supported as `search --trait <value> --gene <value>` |
| Trait and Species | covered | supported as `search --trait <value> --species <value>` |
| Trait and Paper | covered | supported as `search --trait <value> --pmid <value>` |
| Search by Species | covered | supported as `search --species <value>` |
| Species and Gene | covered | supported as `search --species <value> --gene <value>` |
| Species and Paper | covered | supported as `search --species <value> --pmid <value>` |
| Search by Gene | covered | supported as `search --gene <value>` |
| Gene and Paper | covered | supported as `search --gene <value> --pmid <value>` |
| Search by PMID | partially covered | supported as `search --pmid <value>`, but returns database-linked evidence records rather than full PubMed metadata enrichment |

## 11. Boundary Responses

Read [boundary_responses.md](boundary_responses.md) for standard fallback phrasing when a requested task is out of scope.

## 12. Design Supplement

Read [database_skill_design_supplement.md](database_skill_design_supplement.md) for the reusable design lessons extracted from this skill, especially the distinction between exact retrieval, aggregation, and normalization policy.

## 13. Sharing the Skill

To share this skill with another user, give them the skill folders:

- `cucurlitbase-api`
- `cucurlitbase-report`

They should place them under their own Codex skill directory:

```text
<their CODEX_HOME>/skills/
```

On a default Windows setup, that is usually:

```text
C:\Users\<username>\.codex\skills\
```

Recommended sharing unit:

- share the whole folder, not individual files
- keep `SKILL.md`, `agents/`, `scripts/`, and `references/` together
- do not remove the query script, because the documentation assumes it exists

