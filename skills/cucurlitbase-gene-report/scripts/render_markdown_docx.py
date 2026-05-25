#!/usr/bin/env python3
"""Render a final Markdown report into a thesis-like DOCX without extra packages."""

from __future__ import annotations

import argparse
import re
import zipfile
from dataclasses import dataclass
from html import escape
from pathlib import Path


@dataclass
class HeadingState:
    h1: int = 0
    h2: int = 0
    h3: int = 0

    def number(self, level: int) -> str:
        if level == 1:
            self.h1 += 1
            self.h2 = 0
            self.h3 = 0
            return str(self.h1)
        if level == 2:
            self.h2 += 1
            self.h3 = 0
            return f"{self.h1}.{self.h2}"
        self.h3 += 1
        return f"{self.h1}.{self.h2}.{self.h3}"


IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
EXISTING_NUMBER_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
URL_RE = re.compile(r"https?://\S+")
FIG_CAPTION_RE = re.compile(r"^Fig\.\s*\d+[\.:]\s+")
SOFT_BREAK_CHARS = set("/?&=._-:#")

STYLE_DIRECT = {
    "Normal": {
        "eastAsia": "SimSun",
        "ascii": "Times New Roman",
        "size": "21",
        "spacing_after": "120",
        "line": "360",
        "jc": "both",
        "first_line": "420",
    },
    "Title": {
        "eastAsia": "SimHei",
        "ascii": "Times New Roman",
        "size": "34",
        "bold": True,
        "spacing_before": "240",
        "spacing_after": "360",
        "jc": "center",
    },
    "Heading1": {
        "eastAsia": "SimHei",
        "ascii": "Times New Roman",
        "size": "30",
        "bold": True,
        "spacing_before": "320",
        "spacing_after": "180",
        "keep_next": True,
    },
    "Heading2": {
        "eastAsia": "Microsoft YaHei",
        "ascii": "Times New Roman",
        "size": "26",
        "bold": True,
        "spacing_before": "260",
        "spacing_after": "140",
        "keep_next": True,
    },
    "Heading3": {
        "eastAsia": "Microsoft YaHei",
        "ascii": "Times New Roman",
        "size": "22",
        "bold": True,
        "spacing_before": "200",
        "spacing_after": "100",
        "keep_next": True,
    },
    "Bullet": {
        "eastAsia": "SimSun",
        "ascii": "Times New Roman",
        "size": "21",
        "spacing_after": "80",
        "line": "320",
    },
    "Caption": {
        "eastAsia": "SimSun",
        "ascii": "Times New Roman",
        "size": "18",
        "italic": True,
        "spacing_after": "120",
        "jc": "center",
    },
    "TableText": {
        "eastAsia": "SimSun",
        "ascii": "Times New Roman",
        "size": "21",
        "spacing_before": "40",
        "spacing_after": "40",
        "line": "260",
    },
    "TableHeader": {
        "eastAsia": "Microsoft YaHei",
        "ascii": "Times New Roman",
        "size": "21",
        "bold": True,
        "spacing_before": "40",
        "spacing_after": "40",
        "line": "260",
    },
}


def strip_existing_number(text: str) -> str:
    return EXISTING_NUMBER_RE.sub("", text).strip()


def soft_break_long_tokens(text: str) -> str:
    """Insert zero-width break opportunities into URLs and long identifiers."""
    parts = re.split(r"(\s+)", text)
    result: list[str] = []
    for part in parts:
        if not part or part.isspace():
            result.append(part)
            continue
        if len(part) < 32 and not URL_RE.search(part):
            result.append(part)
            continue
        token: list[str] = []
        for char in part:
            token.append(char)
            if char in SOFT_BREAK_CHARS:
                token.append("\u200b")
        result.append("".join(token))
    return "".join(result)


def xml_run_props(style: str) -> str:
    config = STYLE_DIRECT.get(style, STYLE_DIRECT["Normal"])
    props = [
        f'<w:rFonts w:ascii="{config["ascii"]}" w:hAnsi="{config["ascii"]}" w:eastAsia="{config["eastAsia"]}"/>',
        f'<w:sz w:val="{config["size"]}"/>',
    ]
    if config.get("bold"):
        props.append("<w:b/>")
    if config.get("italic"):
        props.append("<w:i/>")
    return f"<w:rPr>{''.join(props)}</w:rPr>"


def xml_paragraph(text: str, style: str = "Normal", align: str | None = None, indent_twips: int | None = None) -> str:
    config = STYLE_DIRECT.get(style, STYLE_DIRECT["Normal"])
    contains_url = bool(URL_RE.search(text))
    prepared_text = soft_break_long_tokens(text)
    p_props = [f'<w:pStyle w:val="{style}"/>']
    spacing = []
    if config.get("spacing_before"):
        spacing.append(f'w:before="{config["spacing_before"]}"')
    if config.get("spacing_after"):
        spacing.append(f'w:after="{config["spacing_after"]}"')
    if config.get("line"):
        spacing.append(f'w:line="{config["line"]}" w:lineRule="auto"')
    if spacing:
        p_props.append(f"<w:spacing {' '.join(spacing)}/>")
    final_align = align or ("left" if contains_url and style in {"Normal", "Bullet", "TableText"} else config.get("jc"))
    if final_align:
        p_props.append(f'<w:jc w:val="{final_align}"/>')
    if indent_twips is not None:
        p_props.append(f'<w:ind w:left="{indent_twips}" w:hanging="360"/>')
    elif config.get("first_line") and not contains_url:
        p_props.append(f'<w:ind w:firstLine="{config["first_line"]}"/>')
    if config.get("keep_next"):
        p_props.append("<w:keepNext/>")
    ppr = f"<w:pPr>{''.join(p_props)}</w:pPr>"
    return f'<w:p>{ppr}<w:r>{xml_run_props(style)}<w:t xml:space="preserve">{escape(prepared_text)}</w:t></w:r></w:p>'


def xml_image(rel_id: str, doc_id: int, width_emu: int = 5200000, height_emu: int = 3000000) -> str:
    return f"""<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="160" w:after="160"/></w:pPr><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{width_emu}" cy="{height_emu}"/><wp:docPr id="{doc_id}" name="Figure {doc_id}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{doc_id}" name="figure.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width_emu}" cy="{height_emu}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"""


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def is_table_start(lines: list[str], index: int) -> bool:
    return index + 1 < len(lines) and lines[index].strip().startswith("|") and TABLE_SEPARATOR_RE.match(lines[index + 1])


def collect_table(lines: list[str], index: int) -> tuple[list[str], list[list[str]], int]:
    headers = split_table_row(lines[index])
    rows: list[list[str]] = []
    index += 2
    while index < len(lines) and lines[index].strip().startswith("|"):
        row = split_table_row(lines[index])
        if len(row) < len(headers):
            row.extend([""] * (len(headers) - len(row)))
        rows.append(row[: len(headers)])
        index += 1
    return headers, rows, index


def cell(text: str, shading: str | None = None, width: int | None = None, style: str = "TableText") -> str:
    width_xml = f'<w:tcW w:w="{width}" w:type="dxa"/>' if width else ""
    shading_xml = f'<w:shd w:fill="{shading}"/>' if shading else ""
    props = f"<w:tcPr>{width_xml}{shading_xml}<w:vAlign w:val=\"top\"/></w:tcPr>"
    return f"<w:tc>{props}{xml_paragraph(text, style)}</w:tc>"


def xml_table(headers: list[str], rows: list[list[str]]) -> str:
    border = (
        '<w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="5000" w:type="pct"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="A6A6A6"/>'
        '<w:left w:val="single" w:sz="6" w:color="A6A6A6"/>'
        '<w:bottom w:val="single" w:sz="6" w:color="A6A6A6"/>'
        '<w:right w:val="single" w:sz="6" w:color="A6A6A6"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D9D9D9"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D9D9D9"/></w:tblBorders></w:tblPr>'
    )
    header_row = "<w:tr>" + "".join(cell(header, shading="DDEBF7", style="TableHeader") for header in headers) + "</w:tr>"
    body_rows = ["<w:tr>" + "".join(cell(value) for value in row) + "</w:tr>" for row in rows]
    return "<w:tbl>" + border + header_row + "".join(body_rows) + "</w:tbl>"


def xml_evidence_cards(headers: list[str], rows: list[list[str]]) -> str:
    parts: list[str] = []
    for idx, row in enumerate(rows, start=1):
        label = row[0] if row and row[0] else str(idx)
        parts.append(xml_paragraph(f"Evidence {label}", "Heading3"))
        card_rows = []
        for header, value in zip(headers, row):
            if value:
                card_rows.append(
                    "<w:tr>"
                    + cell(header, shading="F2F2F2", width=2200, style="TableHeader")
                    + cell(value, width=7600, style="TableText")
                    + "</w:tr>"
                )
        border = (
            '<w:tblPr><w:tblW w:w="5000" w:type="pct"/>'
            '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="BFBFBF"/>'
            '<w:left w:val="single" w:sz="6" w:color="BFBFBF"/>'
            '<w:bottom w:val="single" w:sz="6" w:color="BFBFBF"/>'
            '<w:right w:val="single" w:sz="6" w:color="BFBFBF"/>'
            '<w:insideH w:val="single" w:sz="4" w:color="D9D9D9"/>'
            '<w:insideV w:val="single" w:sz="4" w:color="D9D9D9"/></w:tblBorders></w:tblPr>'
        )
        parts.append("<w:tbl>" + border + "".join(card_rows) + "</w:tbl>")
    return "".join(parts)


def resolve_image(markdown_dir: Path, raw_path: str) -> Path | None:
    cleaned = raw_path.strip().strip("<>")
    candidate = Path(cleaned)
    if not candidate.is_absolute():
        candidate = markdown_dir / candidate
    candidate = candidate.resolve()
    return candidate if candidate.exists() else None


def render_body(markdown: str, markdown_dir: Path, title: str | None) -> tuple[str, list[tuple[str, Path]]]:
    lines = markdown.splitlines()
    body: list[str] = []
    rels: list[tuple[str, Path]] = []
    heading_state = HeadingState()
    first_title_done = bool(title)
    if title:
        body.append(xml_paragraph(title, "Title", align="center"))

    index = 0
    image_index = 1
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        heading = HEADING_RE.match(stripped)
        if heading:
            raw_level = len(heading.group(1))
            heading_text = strip_existing_number(heading.group(2))
            if raw_level == 1 and not first_title_done:
                body.append(xml_paragraph(heading_text, "Title", align="center"))
                first_title_done = True
            else:
                level = raw_level - 1 if raw_level > 1 else 1
                level = max(1, min(3, level))
                number = heading_state.number(level)
                body.append(xml_paragraph(f"{number} {heading_text}", f"Heading{level}"))
            index += 1
            continue

        if is_table_start(lines, index):
            headers, rows, index = collect_table(lines, index)
            body.append(xml_evidence_cards(headers, rows) if len(headers) > 6 else xml_table(headers, rows))
            continue

        image = IMAGE_RE.search(stripped)
        if image:
            fig = resolve_image(markdown_dir, image.group(1))
            if fig:
                rel_id = f"rId{image_index}"
                rels.append((rel_id, fig))
                body.append(xml_image(rel_id, image_index))
                image_index += 1
            else:
                body.append(xml_paragraph(f"[Missing image: {image.group(1)}]", "Caption"))
            index += 1
            continue

        if FIG_CAPTION_RE.match(stripped):
            body.append(xml_paragraph(stripped, "Caption"))
            index += 1
            continue

        if stripped.startswith("- "):
            body.append(xml_paragraph(stripped[2:], "Bullet", indent_twips=720))
        else:
            body.append(xml_paragraph(stripped, "Normal"))
        index += 1

    return "".join(body), rels


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr></w:rPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/><w:ind w:firstLine="420"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:spacing w:before="240" w:after="360"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimHei"/><w:b/><w:sz w:val="34"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:spacing w:before="320" w:after="180"/><w:keepNext/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimHei"/><w:b/><w:sz w:val="30"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:pPr><w:spacing w:before="260" w:after="140"/><w:keepNext/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="26"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:pPr><w:spacing w:before="200" w:after="100"/><w:keepNext/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Bullet"><w:name w:val="Bullet"/><w:pPr><w:spacing w:before="0" w:after="80" w:line="320" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:pPr><w:spacing w:before="60" w:after="120"/><w:jc w:val="center"/></w:pPr><w:rPr><w:i/><w:sz w:val="18"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:pPr><w:spacing w:before="40" w:after="40" w:line="260" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimSun"/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableHeader"><w:name w:val="Table Header"/><w:pPr><w:spacing w:before="40" w:after="40" w:line="260" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/></w:style>
</w:styles>"""


def render_docx(markdown_path: Path, output_path: Path, title: str | None = None) -> None:
    markdown = markdown_path.read_text(encoding="utf-8")
    body_xml, rels = render_body(markdown, markdown_path.parent, title)
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body_xml}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>"""
    relationships = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
    ]
    for rel_id, fig in rels:
        relationships.append(f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{fig.name}"/>')
    relationships.append("</Relationships>")
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="jpg" ContentType="image/jpeg"/><Default Extension="jpeg" ContentType="image/jpeg"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", root_rels)
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/_rels/document.xml.rels", "\n".join(relationships))
        for _, fig in rels:
            docx.write(fig, f"word/media/{fig.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Markdown report to a thesis-like DOCX.")
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--output-docx", required=True)
    parser.add_argument("--title")
    args = parser.parse_args()
    render_docx(Path(args.markdown).resolve(), Path(args.output_docx).resolve(), args.title)
    print(str(Path(args.output_docx).resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
