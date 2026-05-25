# Depth Expansion Contract

Use this contract to expand a generated `report.md` into a researcher-facing `final_report.md`.

## Purpose

The final report must read like a compact literature review and experiment-planning dossier. It should not only list records. It must explain how the evidence changes the biological interpretation, what remains unsupported, and which follow-up experiments are justified.

## Title Policy

Use Chinese academic headings throughout the report. English is allowed only for gene symbols, species names, database names, methods, and fixed figure labels such as `Fig. 1`.

Recommended heading style:

- `查询范围与证据来源`
- `摘要与结论边界`
- `证据基础与来源结构`
- `图表结果与时间分布解释`
- `性状证据主线`
- `机制证据综合`
- `研究局限与后续验证方案`
- `附录：来源链接`

Do not use conversational or rhetorical headings, including:

- `最强可辩护结论`
- `为什么选择 X`
- `一句话总结`
- `亮点`
- `看图说话`
- `你需要知道什么`

## Minimum Analytical Depth

For a normal evidence set, the final report should satisfy these minimums:

- `摘要与结论边界`: at least 260 Chinese characters.
- `图表结果与时间分布解释`: at least 520 Chinese characters.
- `性状证据主线`: at least 650 Chinese characters.
- `机制证据综合`: at least 560 Chinese characters.
- `研究局限与后续验证方案`: at least 900 Chinese characters.
- Whole report: at least 4500 Chinese characters when the evidence set has enough records.

If CucurLitBase returns fewer than three records, reduce the length target explicitly and explain why the evidence base cannot support a full dossier.

## Required Analysis Pattern

Each major analytical section should contain:

- Claim: what the current evidence supports.
- Evidence: which PMID, journal, year, sentence, figure, or table supports it.
- Boundary: what the evidence does not establish.
- Interpretation: what the result implies for gene function, trait biology, or experiment planning.
- Follow-up: what should be checked next.

## Required Synthesis Units

Include these units when evidence is available:

- Paper-level synthesis: merge repeated records from the same PMID before drawing conclusions.
- Trait-level synthesis: identify the dominant trait line and compare it with minor trait lines.
- Mechanism-level synthesis: separate heuristic labels from experimentally supported mechanisms.
- Evidence-strength synthesis: distinguish functional validation, expression evidence, genetic-candidate evidence, and background mention.
- Temporal synthesis: interpret the publication timeline as record distribution, not as true field-wide trend.
- Experimental-priority synthesis: propose follow-up experiments ranked by evidence strength and biological tractability.

## BFT Tree Rule

Use a BFT tree figure only when a real trait hierarchy is available from CucurLitBase or a user-provided trait tree file. Do not fabricate parent-child relationships from trait names.

When the tree is available:

- Highlight the queried trait or observed trait set.
- Show the path from high-level phenotype category to terminal trait.
- Explain whether evidence is concentrated in one branch or scattered across branches.

When the tree is unavailable:

- State that the report cannot draw a strict BFT hierarchy.
- Use trait distribution and trait-mechanism heatmaps instead.
