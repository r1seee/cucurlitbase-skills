# DOCX Format Contract

Use this contract for final report DOCX rendering.

## Markdown hierarchy

Write final reports with explicit Markdown hierarchy:

- `#` document title only
- `##` top-level sections, rendered as `1`, `2`, `3`
- `###` subsections, rendered as `1.1`, `1.2`, `2.1`
- `####` detailed subsections, rendered as `1.1.1`, `1.1.2`

Do not write all content under `##` headings. A final researcher-facing report should contain at least three `###` subsections.

## Typography

The bundled renderer applies:

- Title: SimHei / Times New Roman, 17 pt, bold, centered
- Level 1 heading: SimHei / Times New Roman, 15 pt, bold
- Level 2 heading: Microsoft YaHei / Times New Roman, 13 pt, bold
- Level 3 heading: Microsoft YaHei / Times New Roman, 11 pt, bold
- Body: SimSun / Times New Roman, 10.5 pt, justified, 1.5 line spacing
- Bullets: SimSun / Times New Roman, 10.5 pt
- Figure captions: SimSun / Times New Roman, 9 pt, italic, centered
- Tables and evidence cards: SimSun / Microsoft YaHei / Times New Roman, 10.5 pt, bordered, shaded header

The renderer writes both Word styles and direct run-level formatting. This is intentional because some Word-compatible viewers ignore custom style definitions unless the formatting is also present on the paragraph run.

Body paragraphs use first-line indentation. Headings, tables, captions, and evidence cards do not use first-line indentation. Blank Markdown lines are not rendered as empty Word paragraphs; spacing is controlled through paragraph styles.

Long URLs and long identifiers are handled specially. The renderer inserts zero-width break opportunities after URL separators such as `/`, `?`, `&`, `=`, `.`, `_`, `-`, `:`, and `#`. Paragraphs or table cells containing URLs are rendered left-aligned without first-line indentation to avoid large blank areas caused by full justification.

## Tables

Small Markdown tables are rendered as Word tables.

Wide evidence tables with more than six columns are automatically converted into evidence cards. This avoids unreadable, over-wide Word tables.

## Figures

Figures are centered and embedded at report width. The report text must explain each figure before or after the image; images alone are not enough.

Write numbered captions immediately after each figure:

```markdown
![publication_timeline](figures/publication_timeline.png)
Fig. 4. Publication timeline of evidence records by year.
```

The renderer recognizes `Fig. x.` lines as captions and applies the caption style. The analysis paragraph should cite each figure with the same label, for example `Fig. 4`.

## Required command

Render final Markdown with:

```bash
python scripts/render_markdown_docx.py --markdown outputs/example/final_report.md --output-docx outputs/example/final_report.docx
```

Then run the quality gate:

```bash
python scripts/check_gene_report_quality.py --report-md outputs/example/final_report.md --evidence-json outputs/example/data/evidence_enriched.json
```
