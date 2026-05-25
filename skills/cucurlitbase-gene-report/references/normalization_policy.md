# Normalization Policy

Default policy for gene reports:

- exact API retrieval uses the raw gene string supplied by the user
- local aggregation may apply normalization only when explicitly stated
- case variants such as `PAL` and `PaL` must be reported if they affect counts
- aliases should not be merged unless a verified alias map is available

When reporting ranking or "most evidence" claims:

1. state whether normalization was used
2. state the exact API query used for reproducibility
3. state if the exact API result differs from normalized aggregation

For future databases, add a source-specific alias table before merging identifiers.
