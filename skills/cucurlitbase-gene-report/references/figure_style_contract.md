# Figure Style Contract

Figures should be readable in Word reports and slides.

Default style:

- output format: PNG for DOCX embedding; SVG may be added later
- title: uppercase, bold, concise
- font: default matplotlib sans-serif unless a project font is provided
- color: restrained multi-hue palette, avoid single-color theme dominance
- labels: explicit axes and units where applicable
- export: at least 200 DPI

Required default figures for a deep gene report:

- publication timeline as a line chart with markers and light area fill; avoid a default bar chart unless the user explicitly asks for bars
- trait evidence distribution
- mechanism category distribution
- evidence strength distribution
- trait-mechanism heatmap
- trait-strength heatmap
- PMID-trait matrix

Caption and citation requirements:

- Number figures in the order they appear: `Fig. 1.`, `Fig. 2.`, `Fig. 3.`
- Put the caption immediately below the image in Markdown.
- State what is plotted, what query/evidence source produced it, and what the count means.
- Cite each numbered figure in the interpretation text, for example `Fig. 2 indicates...`.
- Do not cite a figure only in its caption; the interpretation section must use the figure label in prose.

Optional later figures:

- gene-trait-paper network
- BFT trait hierarchy with highlighted query trait or evidence trait set
- species comparison chart

BFT tree rule:

- Draw the BFT tree only from a real trait hierarchy returned by the database or provided by the user.
- Do not infer parent-child relationships from trait names.
- If the tree is unavailable, state the limitation and use trait distribution, trait-mechanism heatmap, and PMID-trait matrix instead.

Do not create decorative figures. Every figure must answer a report question.
