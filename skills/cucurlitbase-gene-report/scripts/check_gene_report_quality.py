#!/usr/bin/env python3
"""Quality gate for final CucurLitBase gene reports."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = [
    "查询范围与证据来源",
    "摘要与结论边界",
    "证据基础与来源结构",
    "图表结果与时间分布解释",
    "性状证据主线",
    "机制证据综合",
    "研究局限与后续验证方案",
    "附录：来源链接",
]

BAD_PHRASES = [
    "待由 agent",
    "placeholder",
    "TODO",
    "TBD",
    "Chinese narrative synthesis should be completed",
]

BAD_STYLE_PATTERNS = [
    ("AI-like contrast pattern", r"不是[^。；\n]{0,60}而是"),
    ("generic attention opener", r"值得注意的是"),
    ("colloquial visual phrase", r"我们可以看到|可以看到"),
    ("over-generic simplification phrase", r"不能简单地?|不能简单将"),
]

FORBIDDEN_HEADING_PATTERNS = [
    r"最强可辩护结论",
    r"为什么选择",
    r"为什么.*重要",
    r"你需要知道",
    r"一句话",
    r"亮点",
    r"看图说话",
]

SECTION_DEPTH_MIN_CHARS = {
    "摘要与结论边界": 260,
    "图表结果与时间分布解释": 520,
    "性状证据主线": 650,
    "机制证据综合": 560,
    "研究局限与后续验证方案": 900,
}


def chinese_chars(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def heading_core(text: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", text).strip()


def section_text(markdown: str, section: str) -> str:
    pattern = re.compile(rf"^##\s+(?:\d+\.\s+)?{re.escape(section)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", markdown[match.end() :], flags=re.MULTILINE)
    if not next_match:
        return markdown[match.end() :]
    return markdown[match.end() : match.end() + next_match.start()]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_report(report_md: Path, evidence_json: Path, min_chinese_chars: int, min_gap_chars: int) -> dict[str, Any]:
    markdown = report_md.read_text(encoding="utf-8")
    evidence = load_json(evidence_json)
    issues: list[str] = []
    warnings: list[str] = []

    if not isinstance(evidence, list):
        issues.append("Evidence JSON must be a list.")
        evidence = []

    for section in REQUIRED_SECTIONS:
        pattern = re.compile(rf"^##\s+(?:\d+\.\s+)?{re.escape(section)}\s*$", re.MULTILINE)
        if not pattern.search(markdown):
            issues.append(f"Missing required section: {section}")

    required_substrings = [
        "期刊来源与证据可靠性概览",
        "文本证据表",
        "图表综合解读",
        "Paper Title",
        "Mechanism Chain",
    ]
    for required in required_substrings:
        if required not in markdown:
            issues.append(f"Missing required report component: {required}")

    if re.search(r"^##\s+(?:\d+\.\s+)?Literature Timeline\s*$", markdown, flags=re.MULTILINE):
        issues.append("Do not use a standalone Literature Timeline section; integrate it into figure analysis.")

    for phrase in BAD_PHRASES:
        if phrase in markdown:
            issues.append(f"Forbidden placeholder phrase remains: {phrase}")

    for label, pattern in BAD_STYLE_PATTERNS:
        if re.search(pattern, markdown):
            issues.append(f"Forbidden non-academic writing pattern found: {label}")

    for level, heading in re.findall(r"^(#{2,4})\s+(.+)$", markdown, flags=re.MULTILINE):
        clean_heading = heading_core(heading)
        if not re.search(r"[\u4e00-\u9fff]", clean_heading):
            issues.append(f"Non-Chinese analytical heading found: {clean_heading}")
        for pattern in FORBIDDEN_HEADING_PATTERNS:
            if re.search(pattern, clean_heading):
                issues.append(f"Non-academic or conversational heading found: {clean_heading}")

    missing_translations = [
        item.get("translation_key") or f"row-{idx}"
        for idx, item in enumerate(evidence, start=1)
        if not str(item.get("translation_zh", "")).strip() or item.get("translation_status") == "missing"
    ]
    if missing_translations:
        issues.append(f"Missing Chinese translations: {len(missing_translations)} records.")

    zh_count = chinese_chars(markdown)
    if zh_count < min_chinese_chars:
        issues.append(f"Report Chinese length is too short: {zh_count} < {min_chinese_chars} Chinese chars.")

    subsection_count = len(re.findall(r"^###\s+", markdown, flags=re.MULTILINE))
    if subsection_count < 3:
        issues.append(f"Report lacks hierarchical subsections: {subsection_count} < 3 markdown level-3 headings.")

    for section, required_chars in SECTION_DEPTH_MIN_CHARS.items():
        current = chinese_chars(section_text(markdown, section))
        if current < required_chars:
            issues.append(f"Section analysis is too shallow: {section} has {current} < {required_chars} Chinese chars.")

    gaps = section_text(markdown, "研究局限与后续验证方案")
    gap_count = chinese_chars(gaps)
    if gap_count < min_gap_chars:
        issues.append(f"Research Gaps section is too shallow: {gap_count} < {min_gap_chars} Chinese chars.")

    if "![trait_distribution]" not in markdown:
        warnings.append("Trait distribution figure is not referenced.")
    if "![mechanism_distribution]" not in markdown:
        warnings.append("Mechanism distribution figure is not referenced.")
    if "![publication_timeline]" not in markdown:
        warnings.append("Publication timeline figure is not referenced.")

    image_count = len(re.findall(r"^!\[[^\]]+\]\([^)]+\)\s*$", markdown, flags=re.MULTILINE))
    captions = re.findall(r"^(Fig\.\s+\d+)\.\s+.+$", markdown, flags=re.MULTILINE)
    if len(captions) < image_count:
        issues.append(f"Missing numbered figure captions: {len(captions)} < {image_count}.")
    for fig_ref in captions:
        if fig_ref not in markdown:
            issues.append(f"Missing figure reference in prose or caption: {fig_ref}.")
        elif markdown.count(fig_ref) < 2:
            issues.append(f"Figure is captioned but not cited in analysis prose: {fig_ref}.")

    if "https://pubmed.ncbi.nlm.nih.gov/" not in markdown:
        issues.append("No PubMed source links found.")

    return {
        "passed": not issues,
        "issues": issues,
        "warnings": warnings,
        "metrics": {
            "chinese_chars": zh_count,
            "research_gap_chinese_chars": gap_count,
            "evidence_records": len(evidence),
            "missing_translations": len(missing_translations),
            "markdown_level3_headings": subsection_count,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check final CucurLitBase gene report quality.")
    parser.add_argument("--report-md", required=True)
    parser.add_argument("--evidence-json", required=True)
    parser.add_argument("--min-chinese-chars", type=int, default=4500)
    parser.add_argument("--min-gap-chars", type=int, default=900)
    args = parser.parse_args()

    result = check_report(
        Path(args.report_md).resolve(),
        Path(args.evidence_json).resolve(),
        args.min_chinese_chars,
        args.min_gap_chars,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
