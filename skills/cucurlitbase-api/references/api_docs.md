# CucurLitBase Verified API Notes

This file records only endpoints verified on May 20, 2026 against:

- Base site: `http://117.72.82.63:9003/CucurLitBase/`
- Data API page: `http://117.72.82.63:9003/CucurLitBase/data-api`

## Verified listing endpoints

Use these to discover valid query values before searching when user input may be approximate.

| Endpoint | Parameters | Verified response shape |
| --- | --- | --- |
| `specieslisting/` | none | list of `{name, sciName}` |
| `traitlisting/` | none | list of `{tag, name, complete}` |
| `genelisting/` | none | list of `{name, description}` |
| `pmidlisting/` | none | list of `{PMID}` |

## Verified evidence query endpoints

These endpoints return lists of evidence records. The common fields are usually:

- `Species`
- `sciName`
- `Gene`
- `pmid`
- `BFTName`
- `Sentence`

`searchbygene/` also returned:

- `Sequences`
- `SequencesCDS`

### Single-filter queries

| Endpoint | Query parameter |
| --- | --- |
| `searchbygene/` | `gene` |
| `searchbypmid/` | `pmid` |
| `searchbyspecies/` | `species` |
| `searchbytrait/` | `trait` |

### Two-filter queries

| Endpoint | Query parameters |
| --- | --- |
| `searchbygeneandpmid/` | `gene`, `pmid` |
| `searchbyspeciesandgene/` | `species`, `gene` |
| `searchbyspeciesandpmid/` | `species`, `pmid` |
| `searchbytraitandgene/` | `trait`, `gene` |
| `searchbytraitandpmid/` | `trait`, `pmid` |
| `searchbytraitandspecies/` | `trait`, `species` |

## Verified examples

These were checked live and returned JSON.

```text
searchbygene/?gene=4CL
searchbytrait/?trait=Texture
searchbyspeciesandgene/?species=Watermelon&gene=4-beta-glucanases
```

## Practical guidance

- Prefer listing endpoints first when entity spelling may vary.
- Treat response schemas as partially heterogeneous. Do not assume every query returns `Sequences` or `SequencesCDS`.
- The current script intentionally supports only verified endpoints. If the site adds new combinations later, update both this file and `scripts/query_cucurlitbase.py`.
