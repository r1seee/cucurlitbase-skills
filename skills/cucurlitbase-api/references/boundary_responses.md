# Boundary Responses

Use these response patterns when the requested task is outside the current skill boundary.

## 1. Unsupported filter combination

```text
Current skill support is limited to verified one-filter and two-filter combinations.
Your request requires an unsupported combination: <request>.
I can do one of these instead:
1. run a broader verified query first
2. filter the returned results locally
3. return raw JSON for downstream processing
```

## 2. Tree view unavailable for this task

```text
Current tree output only supports `list traits`.
I can do one of these instead:
1. use `--output report` for a fixed report
2. use `--output summary` for a compact overview
3. use `--output json` for raw machine-readable records
```

## 3. Database returns a flat list instead of a native tree

```text
The database does not expose a native tree endpoint for this view.
I can reconstruct a tree locally from the hierarchical tags, but that is a presentation layer built from flat API records.
```

## 4. Aggregate ranking differs from exact retrieval

```text
I used a local normalization rule for aggregation, but the exact API endpoint only accepts the raw query string.
As a result, the ranked winner and the exact reproducible API report may not contain exactly the same record count.
I will show both the aggregation rule and the exact request URL.
```

## 5. External metadata not provided by this skill

```text
This skill returns database-linked records only.
It does not enrich the result with external PubMed metadata or other third-party annotations.
If you need that, the workflow needs an additional metadata enrichment step.
```

## 6. Unsupported visualization request

```text
This skill does not yet implement the requested visualization mode for this task.
I can return the result as one of these available views instead:
- `summary`
- `report`
- `tree` for trait catalogs only
- `json`
```

## 7. Network or site unavailability

```text
The live database endpoint is currently unreachable, so I cannot verify the result against the source.
I can either stop here, retry later, or show the last known query shape without claiming a live result.
```

## 8. Strict boundary rule

When declining or narrowing scope:

- say exactly which capability is missing
- name the closest supported alternative
- do not imply the unsupported capability already exists
