# Output Layers

This skill does not use one universal answer shape for every task.
Instead, it separates outputs into explicit layers.

## 1. Why layered outputs exist

Different database tasks need different output surfaces:

- machine processing needs raw JSON
- quick exploration needs a short summary
- user-facing delivery needs a stable report
- hierarchical catalogs may need a tree

If all of these are forced into one format, the skill becomes unstable and confusing.

## 2. Current output modes

### 2.1 `json`

Purpose:

- preserve raw records
- support downstream scripting
- avoid presentation loss

Use when:

- the user asks for raw JSON
- exact field inspection matters
- another tool will consume the output

### 2.2 `summary`

Purpose:

- give a compact overview
- show counts, keys, and representative values

Use when:

- the user is exploring the database
- you need quick triage before a deeper query

### 2.3 `report`

Purpose:

- provide a stable user-facing response
- keep fixed section order
- include direct API jump links

Use when:

- the user wants a clean evidence report
- consistency across turns matters

### 2.4 `tree`

Purpose:

- show hierarchy instead of a flat table
- make trait taxonomy readable at a glance

Current scope:

- only supports `list traits`
- rendered as an ASCII tree
- built locally from the trait `tag` hierarchy

## 3. Implementation pattern

The layered-output pattern is implemented in three places:

1. CLI argument layer
   - `--output json|summary|report|tree`
2. execution layer
   - query script dispatches by output mode
3. contract layer
   - report mode uses a fixed section contract
   - tree mode uses a hierarchy reconstruction contract

## 4. Design rule for future database skills

When extending this pattern to another database, do not ask:

- "What is the one true output?"

Ask instead:

- "Which output layer matches this user intent?"

Recommended minimal set:

- `json`
- `summary`
- `report`

Optional views:

- `tree`
- `chart`
- `debug`

## 5. Future extension

If chart output is added later, it should be a new explicit layer rather than being mixed into `report`.
