# CucurLitBase Report Output Contract

Use exactly this section order for user-facing report answers:

1. `## Query`
2. `## API Links`
3. `## Summary`
4. `## Results`
5. `## Evidence`
6. `## Notes`

Required link fields inside `## API Links`:

- `api_page`
- `request_url`

For evidence reports:

- keep `Species`, `Gene`, `BFTName`, and `pmid` as separate columns
- show up to five representative evidence sentences unless the user asks for more
- say explicitly if results were truncated by `--limit`

For catalog/listing reports:

- keep the same outer section order
- use a table in `## Results`
- explain in `## Notes` that this is a directory listing rather than evidence
