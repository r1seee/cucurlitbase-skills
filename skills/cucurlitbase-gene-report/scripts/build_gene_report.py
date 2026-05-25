#!/usr/bin/env python3
"""Build a deep CucurLitBase gene research report draft."""

from __future__ import annotations

import argparse
import json
import textwrap
import zipfile
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import matplotlib.pyplot as plt

BASE_URL = "http://117.72.82.63:9003/CucurLitBase"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

MECHANISM_RULES = {
    "cell wall / lignin / pectin": [
        "cell wall",
        "lignin",
        "pectin",
        "cellulose",
        "polygalacturonase",
        "pectinesterase",
        "expansin",
        "cuticle",
        "wax",
    ],
    "hormone signaling": [
        "ethylene",
        "auxin",
        "abscisic",
        "gibberellin",
        "jasmonic",
        "salicylic",
        "hormone",
    ],
    "stress response": [
        "salt",
        "chilling",
        "heat",
        "drought",
        "water stress",
        "alkali",
        "temperature",
        "oxidative",
    ],
    "disease resistance": [
        "disease",
        "pathogen",
        "virus",
        "fusarium",
        "resistance",
        "infection",
        "mildew",
        "nematode",
    ],
    "pigment / flavonoid / carotenoid": [
        "color",
        "flavonoid",
        "carotenoid",
        "lycopene",
        "anthocyanin",
        "chlorophyll",
        "pigment",
    ],
    "sugar and primary metabolism": [
        "sugar",
        "sucrose",
        "glucose",
        "fructose",
        "metabolism",
        "amino acid",
        "citrulline",
    ],
    "development / morphology": [
        "flowering",
        "seed",
        "fruit development",
        "morphology",
        "trichome",
        "spine",
        "node",
        "shape",
        "size",
    ],
}

STRENGTH_RULES = [
    ("functional validation", ["knockout", "overexpression", "crispr", "silencing", "mutant", "transgenic"]),
    ("expression evidence", ["expression", "qrt-pcr", "upregulated", "downregulated", "transcriptome", "rna-seq"]),
    ("genetic candidate", ["qtl", "gwas", "candidate gene", "linkage", "locus"]),
    ("background mention", ["reported", "known", "review", "previous study"]),
]

FIGURE_CAPTIONS = {
    "trait_distribution": "查询基因相关性状证据分布。计数单位为 CucurLitBase 证据记录，而非独立实验数量。",
    "mechanism_distribution": "机制类别证据分布。机制标签来自规则化初筛，需结合原文方法进一步校正。",
    "evidence_strength_distribution": "证据强度分布。该图用于区分功能验证、表达证据、遗传候选和背景提及。",
    "publication_timeline": "证据记录发表年份分布。折线反映数据库记录密度，不能直接等同于领域研究热度。",
    "trait_mechanism_heatmap": "性状与机制类别交叉热图。颜色深度表示对应组合的证据记录数量。",
    "trait_strength_heatmap": "性状与证据强度交叉热图。该图用于判断各性状结论的证据等级边界。",
    "pmid_trait_matrix": "PMID 与性状证据矩阵。该图用于识别同一论文是否贡献多条性状记录。",
}


def fetch_json(url: str, timeout: int = 30) -> Any:
    try:
        with urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise SystemExit(f"HTTP error {exc.code}: {url}") from exc
    except URLError as exc:
        raise SystemExit(f"Network error for {url}: {exc.reason}") from exc


def query_cucurlitbase(species: str, gene: str, timeout: int) -> tuple[str, list[dict[str, Any]]]:
    params = urlencode({"gene": gene, "species": species})
    url = f"{BASE_URL}/searchbyspeciesandgene/?{params}"
    data = fetch_json(url, timeout=timeout)
    if not isinstance(data, list):
        raise SystemExit("CucurLitBase returned non-list JSON for gene report query.")
    return url, data


def query_trait_species(species: str, trait: str, timeout: int) -> tuple[str, list[dict[str, Any]]]:
    params = urlencode({"trait": trait, "species": species})
    url = f"{BASE_URL}/searchbytraitandspecies/?{params}"
    data = fetch_json(url, timeout=timeout)
    if not isinstance(data, list):
        raise SystemExit("CucurLitBase returned non-list JSON for trait-species query.")
    return url, data


def first_article_id(item: dict[str, Any], id_type: str) -> str:
    for article_id in item.get("articleids", []):
        if article_id.get("idtype") == id_type:
            return article_id.get("value", "")
    return ""


def pubmed_cache_path(cache_dir: Path, pmid: str) -> Path:
    return cache_dir / "pubmed" / f"{pmid}.json"


def fetch_pubmed_batch(pmids: list[str], cache_dir: Path, timeout: int) -> dict[str, dict[str, Any]]:
    cache_dir.joinpath("pubmed").mkdir(parents=True, exist_ok=True)
    result: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for pmid in pmids:
        path = pubmed_cache_path(cache_dir, pmid)
        if path.exists():
            result[pmid] = json.loads(path.read_text(encoding="utf-8"))
        else:
            missing.append(pmid)

    if missing:
        query = urlencode({"db": "pubmed", "id": ",".join(missing), "retmode": "json"})
        payload = fetch_json(f"{PUBMED_SUMMARY_URL}?{query}", timeout=timeout)
        records = payload.get("result", {})
        for pmid in missing:
            item = records.get(pmid, {})
            normalized = {
                "pmid": pmid,
                "title": item.get("title", ""),
                "journal": item.get("fulljournalname") or item.get("source", ""),
                "year": (item.get("pubdate", "")[:4] if item.get("pubdate") else ""),
                "doi": first_article_id(item, "doi"),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
            pubmed_cache_path(cache_dir, pmid).write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            result[pmid] = normalized
    return result


def classify_mechanism(sentence: str, trait: str) -> str:
    text = f"{sentence} {trait}".lower()
    scores = []
    for category, keywords in MECHANISM_RULES.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text)
        if score:
            scores.append((score, category))
    if not scores:
        return "unclear / requires manual review"
    scores.sort(key=lambda item: (-item[0], item[1]))
    return scores[0][1]


def classify_strength(sentence: str) -> str:
    text = sentence.lower()
    for label, keywords in STRENGTH_RULES:
        if any(keyword.lower() in text for keyword in keywords):
            return label
    return "literature mention"


def infer_mechanism_chain(record: dict[str, Any], mechanism_category: str, evidence_strength: str) -> str:
    gene = str(record.get("Gene", "") or "target gene")
    trait = str(record.get("BFTName", "") or "target trait")
    sentence = str(record.get("Sentence", "") or "").lower()
    if evidence_strength == "functional validation":
        link = "functional perturbation"
    elif evidence_strength == "expression evidence":
        link = "expression change"
    elif evidence_strength == "genetic candidate":
        link = "genetic association"
    else:
        link = "literature mention"

    if mechanism_category == "unclear / requires manual review":
        mechanism = "unspecified biological context"
    else:
        mechanism = mechanism_category

    if any(keyword in sentence for keyword in ["qtl", "gwas", "locus", "linkage"]):
        link = "mapped candidate locus"
    elif any(keyword in sentence for keyword in ["qrt-pcr", "rna-seq", "transcriptome", "expression"]):
        link = "transcriptional evidence"
    elif any(keyword in sentence for keyword in ["knockout", "overexpression", "silencing", "transgenic", "crispr"]):
        link = "functional perturbation"

    return f"{gene} -> {link} -> {mechanism} -> {trait}"


def load_translations(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("Translation JSON must map evidence keys to Chinese text.")
    return {str(key): str(value) for key, value in payload.items()}


def enrich_records(
    records: list[dict[str, Any]],
    pubmed: dict[str, dict[str, Any]],
    translations: dict[str, str],
) -> list[dict[str, Any]]:
    enriched = []
    for idx, record in enumerate(records, start=1):
        pmid = str(record.get("pmid") or record.get("PMID") or "")
        sentence = str(record.get("Sentence") or "")
        key = f"{pmid}|{record.get('Gene', '')}|{sentence}"
        meta = pubmed.get(pmid, {})
        mechanism_category = classify_mechanism(sentence, str(record.get("BFTName", "")))
        evidence_strength = classify_strength(sentence)
        enriched.append(
            {
                "index": idx,
                "translation_key": key,
                "species": record.get("Species", ""),
                "scientific_name": record.get("sciName", ""),
                "gene": record.get("Gene", ""),
                "trait": record.get("BFTName", ""),
                "pmid": pmid,
                "title": meta.get("title", ""),
                "journal": meta.get("journal", ""),
                "year": meta.get("year", ""),
                "doi": meta.get("doi", ""),
                "pubmed_url": meta.get("pubmed_url", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"),
                "original_sentence": sentence,
                "translation_zh": translations.get(key, ""),
                "translation_status": "provided" if translations.get(key) else "missing",
                "mechanism_category": mechanism_category,
                "evidence_strength": evidence_strength,
                "mechanism_chain": infer_mechanism_chain(record, mechanism_category, evidence_strength),
            }
        )
    return enriched


def ensure_dirs(output_dir: Path) -> dict[str, Path]:
    paths = {"data": output_dir / "data", "figures": output_dir / "figures", "cache": output_dir / "cache"}
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def plot_bar(counter: Counter, title: str, xlabel: str, output: Path) -> None:
    labels = [item[0] for item in counter.most_common()]
    values = [item[1] for item in counter.most_common()]
    if not labels:
        return
    plt.figure(figsize=(9, max(3.8, 0.38 * len(labels))))
    bars = plt.barh(range(len(labels)), values, color="#2F6F6D")
    plt.yticks(range(len(labels)), labels, fontsize=9)
    plt.xlabel(xlabel, fontsize=10)
    plt.title(title.upper(), fontsize=13, weight="bold")
    plt.gca().invert_yaxis()
    for bar, value in zip(bars, values):
        plt.text(value + 0.05, bar.get_y() + bar.get_height() / 2, str(value), va="center")
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def plot_years(records: list[dict[str, Any]], output: Path) -> None:
    years = Counter(item["year"] or "unknown" for item in records)
    labels = sorted(years, key=lambda value: (value == "unknown", value))
    values = [years[label] for label in labels]
    if not labels:
        return
    x = list(range(len(labels)))
    plt.figure(figsize=(8.6, 4.4))
    plt.plot(x, values, color="#184E77", linewidth=2.6, marker="o", markersize=7, markerfacecolor="#F2CC8F", markeredgecolor="#184E77")
    plt.fill_between(x, values, [0] * len(values), color="#A8DADC", alpha=0.35)
    plt.xlabel("Publication year")
    plt.ylabel("Evidence records")
    plt.title("PUBLICATION TIMELINE", fontsize=13, weight="bold")
    plt.xticks(x, labels, rotation=35, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    for pos, value in zip(x, values):
        plt.text(pos, value + 0.06, str(value), ha="center", va="bottom", fontsize=9)
    plt.ylim(bottom=0, top=max(values) + 0.8)
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def plot_matrix(row_labels: list[str], col_labels: list[str], values: list[list[int]], title: str, output: Path) -> None:
    if not row_labels or not col_labels:
        return
    fig_width = max(7.0, 0.75 * len(col_labels) + 2.5)
    fig_height = max(4.2, 0.36 * len(row_labels) + 1.8)
    plt.figure(figsize=(fig_width, fig_height))
    plt.imshow(values, aspect="auto", cmap="YlGnBu")
    plt.colorbar(label="Evidence records")
    plt.xticks(range(len(col_labels)), col_labels, rotation=35, ha="right", fontsize=8)
    plt.yticks(range(len(row_labels)), row_labels, fontsize=8)
    plt.title(title.upper(), fontsize=13, weight="bold")
    for row_idx, row in enumerate(values):
        for col_idx, value in enumerate(row):
            if value:
                plt.text(col_idx, row_idx, str(value), ha="center", va="center", fontsize=8, color="#1A1A1A")
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def plot_trait_mechanism_heatmap(records: list[dict[str, Any]], output: Path) -> None:
    traits = [trait for trait, _ in Counter(item["trait"] or "unknown trait" for item in records).most_common(18)]
    mechanisms = [name for name, _ in Counter(item["mechanism_category"] for item in records).most_common(10)]
    values = [
        [
            sum(1 for item in records if (item["trait"] or "unknown trait") == trait and item["mechanism_category"] == mechanism)
            for mechanism in mechanisms
        ]
        for trait in traits
    ]
    plot_matrix(traits, mechanisms, values, "Trait mechanism evidence map", output)


def plot_trait_strength_heatmap(records: list[dict[str, Any]], output: Path) -> None:
    traits = [trait for trait, _ in Counter(item["trait"] or "unknown trait" for item in records).most_common(18)]
    strengths = [name for name, _ in Counter(item["evidence_strength"] for item in records).most_common()]
    values = [
        [
            sum(1 for item in records if (item["trait"] or "unknown trait") == trait and item["evidence_strength"] == strength)
            for strength in strengths
        ]
        for trait in traits
    ]
    plot_matrix(traits, strengths, values, "Trait evidence strength map", output)


def plot_pmid_trait_matrix(records: list[dict[str, Any]], output: Path) -> None:
    traits = [trait for trait, _ in Counter(item["trait"] or "unknown trait" for item in records).most_common(16)]
    pmids = [
        pmid
        for pmid, _ in Counter(item["pmid"] or "unknown PMID" for item in records).most_common(18)
    ]
    pmid_labels = []
    for pmid in pmids:
        years = sorted({item["year"] for item in records if (item["pmid"] or "unknown PMID") == pmid and item.get("year")})
        pmid_labels.append(f"{pmid} ({years[0]})" if years else pmid)
    values = [
        [
            sum(1 for item in records if (item["pmid"] or "unknown PMID") == pmid and (item["trait"] or "unknown trait") == trait)
            for trait in traits
        ]
        for pmid in pmids
    ]
    plot_matrix(pmid_labels, traits, values, "PMID trait evidence matrix", output)


def build_figures(records: list[dict[str, Any]], figures_dir: Path) -> list[Path]:
    outputs: list[Path] = []
    specs = [
        (Counter(item["trait"] for item in records), "Trait evidence distribution", "Evidence records", "trait_distribution.png"),
        (Counter(item["mechanism_category"] for item in records), "Mechanism category distribution", "Evidence records", "mechanism_distribution.png"),
        (Counter(item["evidence_strength"] for item in records), "Evidence strength distribution", "Evidence records", "evidence_strength_distribution.png"),
    ]
    for counter, title, xlabel, filename in specs:
        path = figures_dir / filename
        plot_bar(counter, title, xlabel, path)
        if path.exists():
            outputs.append(path)
    timeline = figures_dir / "publication_timeline.png"
    plot_years(records, timeline)
    if timeline.exists():
        outputs.append(timeline)
    matrix_specs = [
        (plot_trait_mechanism_heatmap, "trait_mechanism_heatmap.png"),
        (plot_trait_strength_heatmap, "trait_strength_heatmap.png"),
        (plot_pmid_trait_matrix, "pmid_trait_matrix.png"),
    ]
    for plotter, filename in matrix_specs:
        path = figures_dir / filename
        plotter(records, path)
        if path.exists():
            outputs.append(path)
    return outputs


def build_figure_refs(figures: list[Path]) -> dict[str, str]:
    return {fig.stem: f"Fig. {idx}" for idx, fig in enumerate(figures, start=1)}


def caption_for_figure(fig: Path, refs: dict[str, str]) -> str:
    label = refs.get(fig.stem, "Fig.")
    caption = FIGURE_CAPTIONS.get(fig.stem, fig.stem.replace("_", " ").capitalize())
    return f"{label}. {caption}"


def collect_trait_peer_genes(
    species: str,
    records: list[dict[str, Any]],
    target_gene: str,
    timeout: int,
    trait_limit: int,
    record_limit: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    traits = [trait for trait, _ in Counter(item["trait"] or "" for item in records if item.get("trait")).most_common(trait_limit)]
    target_norm = target_gene.lower()
    peers: list[dict[str, Any]] = []
    urls: list[str] = []
    for trait in traits:
        url, raw_records = query_trait_species(species, trait, timeout=timeout)
        urls.append(url)
        counter: Counter[str] = Counter()
        pmids_by_gene: dict[str, set[str]] = {}
        for raw in raw_records[:record_limit]:
            gene = str(raw.get("Gene") or "").strip()
            if not gene or gene.lower() == target_norm:
                continue
            counter[gene] += 1
            pmids_by_gene.setdefault(gene, set()).add(str(raw.get("pmid") or raw.get("PMID") or ""))
        for gene, count in counter.most_common(12):
            peers.append(
                {
                    "trait": trait,
                    "peer_gene": gene,
                    "evidence_records": count,
                    "pmids": sorted(pmid for pmid in pmids_by_gene.get(gene, set()) if pmid),
                    "request_url": url,
                }
            )
    return peers, urls


def build_trait_peer_sections(peer_genes: list[dict[str, Any]]) -> list[str]:
    lines = ["### 5.2 同表型相关基因背景"]
    if not peer_genes:
        lines.append("当前报告未检索到同表型相关基因背景，或该模块未启用。正式调研时，可基于目标基因涉及的主要 trait 调用 CucurLitBase 的 `trait + species` 查询，以判断该表型下是否存在更高频或更直接的候选基因。")
        return lines
    rows = [
        [
            item["trait"],
            item["peer_gene"],
            item["evidence_records"],
            ", ".join(item.get("pmids", [])[:8]),
            item["request_url"],
        ]
        for item in peer_genes
    ]
    lines.append(
        "同表型相关基因用于建立比较背景。若目标基因在某一 trait 下证据较少，而其他基因具有更多功能验证或遗传定位证据，报告应把目标基因定位为该表型网络中的候选成员，而不应孤立地放大单基因结论。"
    )
    lines.append(md_table(["Trait", "Peer gene", "Evidence records", "PMIDs", "Trait-species query URL"], rows))
    return lines


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    def clean(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").strip()

    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(clean(cell) for cell in row) + " |")
    return "\n".join(lines)


def count_phrase(counter: Counter, top: int = 5) -> str:
    items = [(name, count) for name, count in counter.most_common(top) if name]
    if not items:
        return "no classified evidence"
    return "; ".join(f"{name}: {count}" for name, count in items)


def pct(part: int, whole: int) -> str:
    if whole <= 0:
        return "0.0%"
    return f"{part / whole * 100:.1f}%"


def cite_pmids(records: list[dict[str, Any]], limit: int = 8) -> str:
    pmids = sorted({item["pmid"] for item in records if item.get("pmid")})
    if not pmids:
        return "no PMID"
    suffix = "" if len(pmids) <= limit else f"; +{len(pmids) - limit} more"
    return ", ".join(pmids[:limit]) + suffix


def representative_sentence(records: list[dict[str, Any]]) -> str:
    ranked = sorted(records, key=lambda item: (item["evidence_strength"] == "literature mention", len(item["original_sentence"])))
    if not ranked:
        return ""
    sentence = ranked[0]["original_sentence"].strip()
    if len(sentence) > 260:
        sentence = sentence[:257].rstrip() + "..."
    return sentence


def build_interpretive_analysis(records: list[dict[str, Any]]) -> list[str]:
    total = len(records)
    trait_counts = Counter(item["trait"] for item in records)
    mechanism_counts = Counter(item["mechanism_category"] for item in records)
    strength_counts = Counter(item["evidence_strength"] for item in records)
    years = Counter(item["year"] or "unknown" for item in records)
    journals = Counter(item["journal"] or "unknown" for item in records)
    top_trait, top_trait_n = trait_counts.most_common(1)[0] if trait_counts else ("none", 0)
    top_mechanism, top_mechanism_n = mechanism_counts.most_common(1)[0] if mechanism_counts else ("none", 0)
    direct_n = strength_counts.get("functional validation", 0)
    expression_n = strength_counts.get("expression evidence", 0)
    candidate_n = strength_counts.get("genetic candidate", 0)
    missing_translation_n = sum(1 for item in records if item.get("translation_status") != "provided")

    interpretable_years = sorted(year for year in years if year != "unknown")
    if interpretable_years:
        year_span = f"{interpretable_years[0]}-{interpretable_years[-1]}"
        peak_year = max(interpretable_years, key=lambda year: years[year])
        timeline_text = (
            f"文献时间跨度为 {year_span}，记录峰值年份为 {peak_year}。这只能说明数据库中证据记录的时间分布，"
            "不能直接等同于该基因研究热度或真实发表量，原因是同一论文可能贡献多条 trait-gene 证据。"
        )
    else:
        timeline_text = "PubMed 元数据中缺少可用年份，无法给出可靠时间线判断。"

    return [
        "## 3. 证据基础与来源结构",
        "### 3.1 证据数量概览",
        f"本次检索获得 {total} 条 CucurLitBase 证据记录，覆盖 {len(trait_counts)} 个 trait、{len({item['pmid'] for item in records})} 个 PMID、{len(journals)} 个期刊来源。计数结果应被理解为 evidence-record density，不能直接代表效应大小、因果强度或生物学重要性排序。",
        f"Trait 层面，证据最集中的条目是 `{top_trait}`，占 {top_trait_n}/{total} ({pct(top_trait_n, total)})。如果该比例明显高于其他 trait，报告应优先讨论该 trait 与目标基因的关系；如果分布较分散，则更合理的解释是该基因可能被不同研究在多个表型背景下提及，需要进一步区分直接功能证据和背景关联。",
        f"机制层面，当前规则将最多证据归入 `{top_mechanism}`，占 {top_mechanism_n}/{total} ({pct(top_mechanism_n, total)})。该分类来自关键词启发式，适合用来组织阅读顺序，但不能替代人工判断。最终报告应逐条检查原文句子和论文摘要，确认 trait、基因和机制之间是否存在清楚的因果链条。",
        f"证据强度层面，功能验证记录 {direct_n} 条，表达证据 {expression_n} 条，遗传候选证据 {candidate_n} 条。若功能验证比例较低，应避免使用“调控”“决定”“导致”等强因果措辞；可以使用“相关”“候选”“可能参与”等保守表达，并明确指出证据级别。",
        timeline_text,
        f"翻译状态方面，仍有 {missing_translation_n} 条证据句缺少中文翻译。最终报告不得保留空翻译或占位文本；agent 必须基于 `original_sentence` 逐条生成忠实中文翻译，解释性内容只放在分析段落中。",
    ]


def build_trait_sections(records: list[dict[str, Any]]) -> list[str]:
    lines = ["## 5. 性状证据主线", "### 5.1 性状证据分层"]
    by_trait: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        by_trait.setdefault(item["trait"] or "unknown trait", []).append(item)
    for trait, related in sorted(by_trait.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        mechanisms = Counter(item["mechanism_category"] for item in related)
        strengths = Counter(item["evidence_strength"] for item in related)
        lines.append(
            f"- `{trait}`: {len(related)} 条记录，涉及机制分类 {count_phrase(mechanisms, 3)}，证据强度分布 {count_phrase(strengths, 3)}，PMID: {cite_pmids(related)}。代表性原文证据：{representative_sentence(related)}"
        )
        lines.append(
            "  分析要点：先判断该 trait 是否由目标基因的功能改变直接支持，再判断是否只是表达变化、定位候选或文献背景提及。若同一 trait 同时出现功能验证和表达证据，应把功能验证作为主证据，把表达证据作为机制或时空表达补充。"
        )
    return lines


def build_mechanism_sections(records: list[dict[str, Any]]) -> list[str]:
    lines = ["## 6. 机制证据综合", "### 6.1 机制证据分组"]
    by_mechanism: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        by_mechanism.setdefault(item["mechanism_category"], []).append(item)
    for mechanism, related in sorted(by_mechanism.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        traits = Counter(item["trait"] for item in related)
        strengths = Counter(item["evidence_strength"] for item in related)
        lines.append(
            f"- `{mechanism}`: {len(related)} 条记录，关联 trait 为 {count_phrase(traits, 5)}，证据强度为 {count_phrase(strengths, 4)}，PMID: {cite_pmids(related)}。"
        )
        lines.append(
            "  解释边界：该机制标签是整理证据的阅读框架，尚不能视为最终机制结论。最终结论需要满足三个条件：原文明确连接 gene 和 trait；论文方法支持该连接；同一机制下的多条证据不存在明显互相矛盾。"
        )
        lines.append(
            "  深度分析要求：正式报告应进一步核查该机制组内的核心 PMID，提取实验材料、处理条件、发育阶段、测量指标和统计设计。若证据来自转录组或 qRT-PCR，应讨论其与表型变化的时间顺序；若证据来自遗传定位，应讨论候选区间、共分离关系和同源基因干扰；若证据来自功能扰动，应优先分析扰动方向、表型响应和是否存在互补验证。"
        )
    return lines


def build_journal_sections(records: list[dict[str, Any]]) -> list[str]:
    lines = ["### 3.2 期刊来源与证据可靠性概览"]
    by_journal: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        by_journal.setdefault(item["journal"] or "unknown journal", []).append(item)
    journal_counts = Counter(item["journal"] or "unknown journal" for item in records)
    year_counts = Counter(item["year"] or "unknown" for item in records)
    lines.append(
        f"本节先评估证据来源，再进入性状和机制分析。本批证据覆盖 {len(by_journal)} 个期刊来源。期刊分布为 {count_phrase(journal_counts, 8)}。年份分布为 {count_phrase(year_counts, 8)}。"
    )
    lines.append(
        "期刊名和年份是证据可追溯性的核心字段：最终报告中每条文本证据都应保留 journal、year、PMID 和 PubMed URL，不能只保留原文句子。"
    )
    rows = []
    for journal, related in sorted(by_journal.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        rows.append(
            [
                journal,
                ", ".join(sorted({item["year"] or "unknown" for item in related})),
                len(related),
                cite_pmids(related),
                ", ".join(sorted({item["trait"] or "unknown trait" for item in related})[:5]),
            ]
        )
    lines.append("### 3.3 期刊-PMID 对照表")
    lines.append(md_table(["Journal", "Year(s)", "Evidence records", "PMIDs", "Trait coverage"], rows))
    return lines


def build_figure_interpretation(records: list[dict[str, Any]], figure_refs: dict[str, str]) -> list[str]:
    trait_counts = Counter(item["trait"] for item in records)
    mechanism_counts = Counter(item["mechanism_category"] for item in records)
    strength_counts = Counter(item["evidence_strength"] for item in records)
    years = Counter(item["year"] or "unknown" for item in records)
    top_trait, top_trait_n = trait_counts.most_common(1)[0] if trait_counts else ("none", 0)
    top_mechanism, top_mechanism_n = mechanism_counts.most_common(1)[0] if mechanism_counts else ("none", 0)
    top_strength, top_strength_n = strength_counts.most_common(1)[0] if strength_counts else ("none", 0)
    trait_fig = figure_refs.get("trait_distribution", "Fig. 1")
    mechanism_fig = figure_refs.get("mechanism_distribution", "Fig. 2")
    strength_fig = figure_refs.get("evidence_strength_distribution", "Fig. 3")
    timeline_fig = figure_refs.get("publication_timeline", "Fig. 4")
    trait_mechanism_fig = figure_refs.get("trait_mechanism_heatmap", "Fig. 5")
    trait_strength_fig = figure_refs.get("trait_strength_heatmap", "Fig. 6")
    pmid_trait_fig = figure_refs.get("pmid_trait_matrix", "Fig. 7")
    interpretable_years = sorted(year for year in years if year != "unknown")
    if interpretable_years:
        timeline = f"时间线覆盖 {interpretable_years[0]} 到 {interpretable_years[-1]}，峰值年份为 {max(interpretable_years, key=lambda year: years[year])}。"
    else:
        timeline = "时间线缺少可解释年份，说明 PubMed 元数据或 PMID 映射需要补充。"
    return [
        "### 4.1 图表综合解读",
        f"- {trait_fig} 显示 `{top_trait}` 是当前记录数最高的 trait，记录数为 {top_trait_n}。该图用于确定报告主线和人工阅读优先级；若高频 trait 主要来自同一 PMID，最终报告应降低其权重，并把结论限定为数据库记录密度较高。",
        f"- {mechanism_fig} 显示 `{top_mechanism}` 是当前最高频的机制标签，记录数为 {top_mechanism_n}。该图反映关键词规则整理后的证据组织方式，最终机制判断仍需回到原文方法、摘要和实验设计进行复核。",
        f"- {strength_fig} 显示 `{top_strength}` 是当前最多的证据类型，记录数为 {top_strength_n}。该图直接约束结论措辞；功能扰动证据不足时，应采用候选、相关或可能参与等审慎表述。",
        f"- {timeline_fig} 总结文献记录的年份分布。{timeline} 该图适合辅助安排文献阅读顺序，但单独的记录数量不能证明研究热度或领域趋势。",
        f"- {trait_mechanism_fig} 将性状与机制标签交叉展示，适合识别报告中应优先展开的 `trait-mechanism` 组合。若某一组合计数较高，正文需要进一步判断这些记录来自独立论文、同一论文的多条摘录，还是同一实验体系的重复描述。",
        f"- {trait_strength_fig} 将性状与证据强度并列展示，适合约束每个性状结论的语气。高频性状若主要由表达证据或背景提及构成，结论应停留在相关性或候选层面；只有功能扰动、遗传分离或互补验证充分时，才适合写成较强机制结论。",
        f"- {pmid_trait_fig} 用于检查论文层面的证据集中度。若多个 trait 主要由少数 PMID 支撑，报告应按论文级证据单元归并讨论，避免把同一研究中的多条数据库记录误解为多项独立发现。",
    ]


def build_gap_sections(records: list[dict[str, Any]]) -> list[str]:
    strength_counts = Counter(item["evidence_strength"] for item in records)
    trait_counts = Counter(item["trait"] for item in records)
    mechanism_counts = Counter(item["mechanism_category"] for item in records)
    weak_n = strength_counts.get("literature mention", 0) + strength_counts.get("background mention", 0)
    unclear_n = mechanism_counts.get("unclear / requires manual review", 0)
    lines = [
        "## 7. 研究局限与后续验证方案",
        "### 7.1 证据局限",
        f"1. 证据强度缺口：当前有 {weak_n} 条记录属于文献提及或背景性证据，功能验证记录为 {strength_counts.get('functional validation', 0)} 条。后续阅读应先把证据分成 direct functional validation、expression-only、genetic candidate 和 background mention 四类，再决定哪些结论可以写成因果表述。",
        f"2. Trait 定义缺口：数据库记录覆盖 {len(trait_counts)} 个 trait，其中高频 trait 为 {count_phrase(trait_counts, 5)}。同一 trait 名称可能包含不同实验条件、发育阶段或测量指标，最终报告应补充每篇论文中的表型测量方式，避免把名称相同但实验语境不同的证据合并成一个结论。",
        f"3. 机制链条缺口：机制分类分布为 {count_phrase(mechanism_counts, 6)}，其中 `{unclear_n}` 条记录仍需人工复核。对于每个机制类别，建议补查摘要或全文中的实验方法，确认是否包含突变体、转基因、表达谱、代谢测定、定位分析或互作证据。",
        "4. 基因标准化缺口：同一基因可能存在大小写、同源基因、家族成员、物种特异编号和别名问题。后续应把 CucurLitBase gene 字段与外部数据库中的 gene ID、protein accession、ortholog 信息对齐，避免把基因家族证据误写成单一基因证据。",
        "### 7.2 后续研究设计",
        "5. 外部数据库补充：若报告目标是支持课题设计，应继续补 UniProt/NCBI Gene/Ensembl Plants/GO/KEGG 或 Gramene 等信息，形成 gene structure、protein domain、subcellular localization、GO function、pathway position 和 ortholog conservation 的独立小节。",
        "6. 实验建议：优先选择证据密度最高且存在功能验证缺口的 trait，设计 qRT-PCR、组织/时期表达分析、候选基因单倍型分析、过表达或敲除验证、代谢/形态指标测定。实验建议必须与上文证据强度对应，不能从背景提及直接跳到强机制假设。",
        "7. 文献阅读优先级：先读同时包含目标 gene、明确 trait、可识别实验方法和可追溯 PMID 的论文；再读只提供表达变化或候选定位的论文；最后处理背景性提及。这样可以减少把综述性句子或数据库注释误当作实验结论的风险。",
        "8. 报告扩展方向：正式调研报告应补充每篇核心论文的研究材料、处理条件、表型测量指标、统计设计和主要结论。若同一 PMID 贡献多条记录，应合并为论文级证据单元，再讨论该论文对目标基因的真实支持程度。",
        "9. 结论约束：在没有功能扰动或遗传分离证据前，结论应保持为候选基因或关联证据。只有当原文提供突变体、转基因、基因编辑、互补实验或等价功能验证时，才适合把该基因写成某 trait 的直接调控因子。",
        "10. 数据库覆盖缺口：CucurLitBase 是报告的核心证据来源，但不能保证覆盖所有相关论文。最终报告若用于课题立项或实验设计，应补充关键词检索、同义基因名检索和物种学名检索，并记录哪些外部检索没有发现额外证据。",
        "11. 图表复核缺口：性状分布、机制分布和证据强度图只能说明当前数据库记录的结构。正式报告应结合 PMID-性状矩阵判断证据是否集中于少数论文，并结合性状-机制热图判断哪些组合具有继续阅读价值。若高密度组合缺少功能验证，后续实验优先级应从机制确认而非结论强化开始。",
        "12. BFT 层级缺口：若 CucurLitBase 或用户没有提供真实 BFT 层级树，报告不应臆造 trait 的上下位关系。此时只能讨论当前记录中的 trait 名称分布，并把 BFT 树列为后续数据补充任务；若后续取得层级树，应定位目标 trait 所在分支，分析证据是否集中在单一表型分支或跨多个表型系统扩散。",
        "13. 实验优先级缺口：后续研究计划应把证据强度、实验可操作性和生物学解释价值同时纳入排序。优先级最高的实验通常是能把候选关系推进到功能关系的设计，例如目标组织和关键时期的表达验证、基因家族成员区分、瞬时表达或稳定遗传转化、表型定量指标复测以及与通路标志物的联合测定。",
    ]
    return lines


def build_markdown(
    species: str,
    gene: str,
    request_url: str,
    records: list[dict[str, Any]],
    figures: list[Path],
    trait_peer_genes: list[dict[str, Any]] | None = None,
) -> str:
    trait_counts = Counter(item["trait"] for item in records)
    mechanism_counts = Counter(item["mechanism_category"] for item in records)
    strength_counts = Counter(item["evidence_strength"] for item in records)
    journals = Counter(item["journal"] or "unknown" for item in records)
    years = Counter(item["year"] or "unknown" for item in records)
    figure_refs = build_figure_refs(figures)

    lines = [
        f"# {species} {gene} 文献证据深度分析报告",
        "",
        "## 1. 查询范围与证据来源",
        f"- Species: {species}",
        f"- Gene: {gene}",
        f"- Generated: {date.today().isoformat()}",
        f"- CucurLitBase request URL: {request_url}",
        "- External enrichment: PubMed ESummary when reachable",
        "",
        "## 2. 摘要与结论边界",
        f"本报告围绕 `{species}` 中 `{gene}` 的 CucurLitBase 证据进行整理，共获得 {len(records)} 条 evidence records。报告中的计数、图表和分类用于帮助研究者确定优先阅读顺序和证据薄弱点，不能被直接解释为效应大小或因果强度。",
        f"按 trait 计数，主要证据集中在 {count_phrase(trait_counts, 5)}。按机制启发式分类，主要证据集中在 {count_phrase(mechanism_counts, 5)}。按证据强度分类，分布为 {count_phrase(strength_counts, 5)}。",
        "研究判断应遵循从证据到结论的顺序：先看原文句子是否明确连接 gene 与 trait，再看论文方法是否支持因果判断，最后再决定是否需要外部数据库补充结构、功能、通路和同源关系信息。",
        "因此，本摘要只给出证据支持范围内的工作性结论。若数据库记录主要来自表达变化、候选定位或综述性提及，报告应把目标基因表述为候选因子或相关证据对象；若记录包含突变体、转基因、基因编辑、互补实验或明确的遗传分离证据，才适合进入较强机制表述。",
        "正式研究使用时，应把同一 PMID 下的多条记录先合并为论文级证据单元，再评价这些论文之间是否相互独立。该步骤可以避免把数据库摘录数量误读为独立实验证据数量，也有助于确定后续实验设计应补充功能验证、表达时空图谱，还是基因家族成员鉴定。",
        "",
    ]
    lines.extend(build_interpretive_analysis(records))
    lines.extend(
        [
        md_table(
            ["Metric", "Value"],
            [
                ["Evidence records", len(records)],
                ["Unique traits", len(trait_counts)],
                ["Unique PMIDs", len({item["pmid"] for item in records})],
                ["Unique journals", len(journals)],
                ["Evidence strength", count_phrase(strength_counts, 8)],
                ["Publication years", ", ".join(sorted(years))],
            ],
        ),
        "",
        ]
    )
    lines.extend(build_journal_sections(records))
    lines.extend(
        [
            "",
            "### 3.4 文本证据表",
            md_table(
                [
                    "#",
                    "Trait",
                    "PMID",
                    "Journal",
                    "Year",
                    "Paper Title",
                    "Mechanism",
                    "Strength",
                    "Mechanism Chain",
                    "Original Sentence",
                    "Chinese Translation",
                    "Translation Status",
                ],
                [
                    [
                        item["index"],
                        item["trait"],
                        item["pmid"],
                        item["journal"],
                        item["year"],
                        item["title"],
                        item["mechanism_category"],
                        item["evidence_strength"],
                        item.get("mechanism_chain", ""),
                        item["original_sentence"],
                        item["translation_zh"],
                        item["translation_status"],
                    ]
                    for item in records
                ],
            ),
            "",
        ]
    )
    lines.extend(["## 4. 图表结果与时间分布解释"])
    for fig in figures:
        lines.append(f"![{fig.stem}]({fig.as_posix()})")
        lines.append(caption_for_figure(fig, figure_refs))
    lines.extend(build_figure_interpretation(records, figure_refs))
    lines.extend([""])
    lines.extend(build_trait_sections(records))
    lines.extend(["", *build_trait_peer_sections(trait_peer_genes or [])])
    lines.extend(["", *build_mechanism_sections(records)])
    lines.extend(build_gap_sections(records))
    lines.extend(["", "## 8. 附录：来源链接"])
    for item in records:
        lines.append(f"- PMID {item['pmid']}: {item['pubmed_url']}")
    return "\n".join(lines) + "\n"


def xml_paragraph(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    runs = [f'<w:r><w:t xml:space="preserve">{escape(part)}</w:t></w:r>' for part in (str(text).splitlines() or [""])]
    return f"<w:p>{style_xml}{''.join(runs)}</w:p>"


def xml_image(rel_id: str, width_emu: int = 5200000, height_emu: int = 3000000) -> str:
    return f"""<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{width_emu}" cy="{height_emu}"/><wp:docPr id="1" name="Figure"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="figure.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width_emu}" cy="{height_emu}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"""


def write_minimal_docx(path: Path, title: str, markdown: str, figures: list[Path]) -> None:
    body = [xml_paragraph(title, "Title")]
    rels: list[tuple[str, Path]] = []
    figure_map = {fig.as_posix(): fig for fig in figures}
    image_index = 1
    for line in markdown.splitlines():
        if line.startswith("# "):
            body.append(xml_paragraph(line[2:], "Title"))
        elif line.startswith("## "):
            body.append(xml_paragraph(line[3:], "Heading1"))
        elif line.startswith("!["):
            image_path = line.split("](", 1)[1].rstrip(")")
            fig = figure_map.get(image_path)
            if fig and fig.exists():
                rel_id = f"rId{image_index}"
                rels.append((rel_id, fig))
                body.append(xml_image(rel_id))
                image_index += 1
        elif line.startswith("Fig. "):
            body.append(xml_paragraph(line, "Caption"))
        elif line.strip():
            for chunk in textwrap.wrap(line, width=120) or [line]:
                body.append(xml_paragraph(chunk))
        else:
            body.append(xml_paragraph(""))

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{''.join(body)}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="900" w:right="900" w:bottom="900" w:left="900"/></w:sectPr></w:body></w:document>"""
    relationships = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for rel_id, fig in rels:
        relationships.append(f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{fig.name}"/>')
    relationships.append("</Relationships>")
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style></w:styles>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", root_rels)
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", styles_xml)
        docx.writestr("word/_rels/document.xml.rels", "\n".join(relationships))
        for _, fig in rels:
            docx.write(fig, f"word/media/{fig.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deep CucurLitBase gene report draft.")
    parser.add_argument("--species", required=True)
    parser.add_argument("--gene", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--limit", type=int, default=-1)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--translations-json")
    parser.add_argument("--include-trait-peer-genes", action="store_true")
    parser.add_argument("--peer-trait-limit", type=int, default=5)
    parser.add_argument("--peer-record-limit", type=int, default=300)
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    paths = {"data": output_dir / "data", "figures": output_dir / "figures", "cache": output_dir / "cache"}
    for directory in paths.values():
        directory.mkdir(parents=True, exist_ok=True)

    request_url, records = query_cucurlitbase(args.species, args.gene, timeout=args.timeout)
    if args.limit >= 0:
        records = records[: args.limit]
    pmids = sorted({str(item.get("pmid") or item.get("PMID") or "") for item in records if item.get("pmid") or item.get("PMID")})
    pubmed = fetch_pubmed_batch(pmids, paths["cache"], timeout=args.timeout) if pmids else {}
    enriched = enrich_records(records, pubmed, load_translations(args.translations_json))

    evidence_path = paths["data"] / "evidence_enriched.json"
    evidence_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    translations_template = {
        item["translation_key"]: "" for item in enriched if item.get("translation_key")
    }
    (paths["data"] / "translations_template.json").write_text(
        json.dumps(translations_template, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (paths["data"] / "query.json").write_text(
        json.dumps({"species": args.species, "gene": args.gene, "request_url": request_url, "record_count": len(enriched), "generated": date.today().isoformat()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    figures = build_figures(enriched, paths["figures"])
    trait_peer_genes: list[dict[str, Any]] = []
    trait_peer_urls: list[str] = []
    if args.include_trait_peer_genes and enriched:
        trait_peer_genes, trait_peer_urls = collect_trait_peer_genes(
            args.species,
            enriched,
            args.gene,
            timeout=args.timeout,
            trait_limit=args.peer_trait_limit,
            record_limit=args.peer_record_limit,
        )
    (paths["data"] / "trait_peer_genes.json").write_text(
        json.dumps({"records": trait_peer_genes, "request_urls": trait_peer_urls}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown = build_markdown(args.species, args.gene, request_url, enriched, figures, trait_peer_genes=trait_peer_genes)
    report_md = output_dir / "report.md"
    report_md.write_text(markdown, encoding="utf-8")
    report_docx = output_dir / "report.docx"
    write_minimal_docx(report_docx, f"{args.species} {args.gene} Deep Research Report", markdown, figures)
    print(json.dumps({"report_md": str(report_md), "report_docx": str(report_docx), "evidence_json": str(evidence_path), "translations_template": str(paths["data"] / "translations_template.json"), "trait_peer_genes": str(paths["data"] / "trait_peer_genes.json"), "figures": [str(path) for path in figures], "request_url": request_url, "record_count": len(enriched), "trait_peer_gene_count": len(trait_peer_genes)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
