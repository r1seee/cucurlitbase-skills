# Database Skill Design Supplement

## 1. Why this supplement exists

The base skill manual explains how to use the current CucurLitBase skills.
This supplement extracts the reusable design lessons for building database-oriented skills for other data sources.

The key lesson from the `Watermelon -> top gene` example is:

- statistical selection and exact retrieval are not always the same task
- entity normalization policy must be explicit

In CucurLitBase, `PAL` and `PaL` were counted together during analysis, but the exact query endpoint only returned records for the exact gene string used in the request.

## 2. Minimal required parts for a database skill

Every reusable database skill should have these parts:

### 2.1 Trigger definition

File: `SKILL.md`

Purpose:

- define when the skill should trigger
- define what the data source is
- define which user intents it covers

Without a precise trigger description, the skill will either under-trigger or over-trigger.

### 2.2 Executable query layer

File: `scripts/query_<db>.py`

Purpose:

- map user intent to verified endpoints
- validate supported parameter combinations
- perform network requests
- standardize output modes

This is usually the most important reusable part of a database skill.

### 2.3 Verified API reference

File: `references/api_docs.md`

Purpose:

- record which endpoints are actually verified
- record parameter names
- record observed response shapes
- separate known capabilities from guessed capabilities

This prevents the skill from presenting unverified assumptions as supported features.

### 2.4 Output contract

File: `references/output_contract.md` or embedded report rules

Purpose:

- keep user-facing output stable
- require key sections and link fields
- reduce format drift across turns

If consistency matters, this should be explicit rather than implied.

## 3. Recommended but optional parts

### 3.1 UI metadata

File: `agents/openai.yaml`

Purpose:

- improve discoverability
- provide consistent display names and default prompts

### 3.2 Usage manual

File: `references/usage_manual.md`

Purpose:

- document supported scenarios
- document trigger phrases
- document scope boundaries

### 3.3 Separate report skill

Example:

- `db-api`
- `db-report`

Purpose:

- separate retrieval from presentation
- keep JSON/raw access independent from fixed-format reporting

Use this split when both retrieval flexibility and presentation consistency matter.

## 4. The normalization problem

Database skills should define an explicit normalization policy for entity comparison.

Typical normalization axes:

- case normalization
- alias merging
- whitespace normalization
- punctuation normalization
- identifier-to-name mapping

Without this, the following inconsistency appears:

1. aggregate analysis says entity `X` has the most evidence
2. exact retrieval by `X` returns only a subset
3. users think the skill is wrong
4. the real issue is that normalization policy was undefined

## 5. Separate task types clearly

A database skill should distinguish at least these task types:

### 5.1 Catalog discovery

Examples:

- list species
- list traits
- browse supported identifiers

### 5.2 Exact retrieval

Examples:

- gene = `4CL`
- species = `Watermelon`
- trait + species = `Texture + Bitter melon`

### 5.3 Aggregation or ranking

Examples:

- top gene by evidence count in Watermelon
- most frequent trait in a species
- papers with the most gene mentions

### 5.4 Report presentation

Examples:

- fixed trait report
- fixed species report
- evidence brief with direct request URL

These should not be treated as one undifferentiated operation.

## 6. Design rule for ranking tasks

When a request asks for:

- most frequent
- top
- highest count
- most evidence
- dominant entity

the skill should use a two-step workflow:

1. retrieve the candidate set
2. compute the ranking under an explicit normalization policy
3. only then run an exact or normalized report query

If step 3 cannot exactly reproduce step 2 because the source API only supports exact-string filters, report that limitation explicitly.

## 7. Capability statement should use three labels

When documenting or reviewing a database skill, classify each scenario as:

- `covered`
- `partially covered`
- `not covered`

Use `partially covered` when:

- the endpoint exists but the presentation is weaker than requested
- the aggregation works but exact retrieval cannot reproduce normalized grouping
- the skill returns database-linked data but not full external metadata

## 8. General template for future database skills

Recommended structure:

```text
db-name-api/
  SKILL.md
  agents/openai.yaml
  scripts/query_db_name.py
  references/api_docs.md
  references/usage_manual.md

db-name-report/
  SKILL.md
  agents/openai.yaml
  references/output_contract.md
```

Optional extension:

```text
references/normalization_policy.md
```

Add this when entity spelling variation is common.

## 9. Immediate next improvement for CucurLitBase

The next high-value improvement is not more trigger phrases.

It is one of:

- add a `--normalize-gene-case` analysis mode
- add a documented normalization policy for gene names
- add a report note when aggregate ranking and exact endpoint filters do not perfectly align

That lesson is portable to almost every database skill with semi-curated entity names.
