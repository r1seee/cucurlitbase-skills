#!/usr/bin/env python3
"""Query verified CucurLitBase REST API endpoints."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

DEFAULT_BASE_URL = "http://117.72.82.63:9003/CucurLitBase"

LIST_ENDPOINTS = {
    "species": "specieslisting/",
    "traits": "traitlisting/",
    "genes": "genelisting/",
    "pmids": "pmidlisting/",
}

SEARCH_ENDPOINTS = {
    ("gene",): "searchbygene/",
    ("pmid",): "searchbypmid/",
    ("species",): "searchbyspecies/",
    ("trait",): "searchbytrait/",
    ("gene", "pmid"): "searchbygeneandpmid/",
    ("gene", "species"): "searchbyspeciesandgene/",
    ("pmid", "species"): "searchbyspeciesandpmid/",
    ("gene", "trait"): "searchbytraitandgene/",
    ("pmid", "trait"): "searchbytraitandpmid/",
    ("species", "trait"): "searchbytraitandspecies/",
}

SEARCH_FIELDS = ("gene", "species", "trait", "pmid")


def fetch_json(url: str, timeout: int) -> Any:
    try:
        with urlopen(url, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise SystemExit(f"HTTP error {exc.code} for {url}") from exc
    except URLError as exc:
        raise SystemExit(f"Network error for {url}: {exc.reason}") from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Response was not valid JSON for {url}") from exc


def trim_records(data: Any, limit: int | None) -> Any:
    if not isinstance(data, list):
        return data
    if limit is None or limit < 0:
        return data
    return data[:limit]


def unsupported_tree_message() -> str:
    return (
        "Current tree output only supports `list traits`. "
        "I can do one of these instead: "
        "(1) use `--output report` for a fixed report, "
        "(2) use `--output summary` for a compact overview, or "
        "(3) use `--output json` for raw machine-readable records."
    )


def data_api_page(base_url: str) -> str:
    return f"{normalize_base_url(base_url)}/data-api"


def markdown_escape(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def render_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(cell) for cell in row) + " |")
    return lines


def build_trait_tree_nodes(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for item in records:
        tag = str(item.get("tag", "")).strip()
        if not tag:
            continue
        node = {
            "tag": tag,
            "name": str(item.get("name", "")).strip(),
            "complete": str(item.get("complete", "")).strip(),
            "children": [],
        }
        nodes[tag] = node
        order.append(tag)

    roots: list[dict[str, Any]] = []
    for tag in order:
        node = nodes[tag]
        parts = tag.split(".")
        parent_node = None
        while len(parts) > 1:
            parts = parts[:-1]
            candidate = ".".join(parts)
            if candidate in nodes:
                parent_node = nodes[candidate]
                break
        if parent_node is not None:
            parent_node["children"].append(node)
        else:
            roots.append(node)
    return roots


def render_ascii_tree_lines(
    nodes: list[dict[str, Any]],
    include_tags: bool,
    prefix: str = "",
) -> list[str]:
    lines: list[str] = []
    for index, node in enumerate(nodes):
        is_last = index == len(nodes) - 1
        branch = "`-- " if is_last else "|-- "
        label = node["name"]
        if include_tags and node["tag"]:
            label = f"{node['tag']} {label}"
        lines.append(prefix + branch + label)
        child_prefix = prefix + ("    " if is_last else "|   ")
        lines.extend(
            render_ascii_tree_lines(
                node["children"],
                include_tags=include_tags,
                prefix=child_prefix,
            )
        )
    return lines


def render_trait_tree(
    base_url: str,
    request_url: str,
    data: Any,
    limit: int | None,
    include_tags: bool,
) -> str:
    records = data if isinstance(data, list) else []
    shown = trim_records(records, limit)
    roots = build_trait_tree_nodes(shown)
    tree_lines = render_ascii_tree_lines(roots, include_tags=include_tags)

    lines = [
        "# CucurLitBase Trait Tree",
        "",
        "## Query",
        "- mode: list",
        "- catalog: traits",
        f"- total_items: {len(records)}",
        f"- shown_items: {len(shown)}",
        "",
        "## API Links",
        f"- api_page: {data_api_page(base_url)}",
        f"- request_url: {request_url}",
        "",
        "## Tree",
    ]
    if tree_lines:
        lines.extend(tree_lines)
    else:
        lines.append("No trait nodes returned.")
    lines.extend(
        [
            "",
            "## Notes",
            "- This is an ASCII tree reconstructed locally from the trait `tag` hierarchy.",
            "- It is a presentation view, not a database-native tree endpoint.",
        ]
    )
    if limit is not None and limit >= 0:
        lines.append(f"- display_limit: {limit}")
    return "\n".join(lines)


def build_list_request_url(base_url: str, kind: str) -> str:
    endpoint = LIST_ENDPOINTS[kind]
    return f"{normalize_base_url(base_url)}/{endpoint}"


def build_search_request_url(base_url: str, filters: dict[str, str]) -> str:
    combo = tuple(sorted(filters))
    endpoint = SEARCH_ENDPOINTS[combo]
    query = urlencode(filters)
    return f"{normalize_base_url(base_url)}/{endpoint}?{query}"


def summarize_search_records(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    values = {
        "species": sorted({str(item["Species"]) for item in records if "Species" in item}),
        "genes": sorted({str(item["Gene"]) for item in records if "Gene" in item}),
        "traits": sorted({str(item["BFTName"]) for item in records if "BFTName" in item}),
        "pmids": sorted(
            {
                str(item.get("pmid", item.get("PMID")))
                for item in records
                if item.get("pmid") or item.get("PMID")
            }
        ),
    }
    return values


def render_list_report(
    kind: str,
    base_url: str,
    request_url: str,
    data: Any,
    limit: int | None,
) -> str:
    records = data if isinstance(data, list) else []
    shown = trim_records(records, limit)
    lines = [
        "# CucurLitBase Report",
        "",
        "## Query",
        f"- mode: list",
        f"- catalog: {kind}",
        f"- total_items: {len(records)}",
        f"- shown_items: {len(shown)}",
        "",
        "## API Links",
        f"- api_page: {data_api_page(base_url)}",
        f"- request_url: {request_url}",
        "",
        "## Summary",
        f"- returned_items: {len(records)}",
        f"- displayed_items: {len(shown)}",
    ]
    if limit is not None and limit >= 0:
        lines.append(f"- display_limit: {limit}")
    lines.extend(["", "## Results"])
    if not shown:
        lines.append("No items returned.")
    elif kind == "species":
        lines.extend(
            render_table(
                ["#", "name", "sciName"],
                [
                    [idx, item.get("name", ""), item.get("sciName", "")]
                    for idx, item in enumerate(shown, start=1)
                ],
            )
        )
    elif kind == "traits":
        lines.extend(
            render_table(
                ["#", "tag", "name", "complete"],
                [
                    [
                        idx,
                        item.get("tag", ""),
                        item.get("name", ""),
                        item.get("complete", ""),
                    ]
                    for idx, item in enumerate(shown, start=1)
                ],
            )
        )
    elif kind == "genes":
        lines.extend(
            render_table(
                ["#", "name", "description"],
                [
                    [idx, item.get("name", ""), item.get("description", "")]
                    for idx, item in enumerate(shown, start=1)
                ],
            )
        )
    else:
        lines.extend(
            render_table(
                ["#", "PMID"],
                [[idx, item.get("PMID", "")] for idx, item in enumerate(shown, start=1)],
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- This is a fixed-format catalog report.",
            "- Use `search` mode when the user wants evidence records rather than a directory listing.",
        ]
    )
    return "\n".join(lines)


def render_search_report(
    filters: dict[str, str],
    base_url: str,
    request_url: str,
    data: Any,
    limit: int | None,
) -> str:
    records = data if isinstance(data, list) else []
    shown = trim_records(records, limit)
    summary = summarize_search_records(records)
    filter_text = ", ".join(f"{key}={value}" for key, value in filters.items())

    lines = [
        "# CucurLitBase Report",
        "",
        "## Query",
        "- mode: search",
        f"- filters: {filter_text}",
        f"- total_records: {len(records)}",
        f"- shown_records: {len(shown)}",
        "",
        "## API Links",
        f"- api_page: {data_api_page(base_url)}",
        f"- request_url: {request_url}",
        "",
        "## Summary",
        f"- unique_species: {len(summary['species'])}",
        f"- unique_genes: {len(summary['genes'])}",
        f"- unique_traits: {len(summary['traits'])}",
        f"- unique_pmids: {len(summary['pmids'])}",
    ]
    if summary["species"]:
        lines.append(f"- species_values: {', '.join(summary['species'][:10])}")
    if summary["genes"]:
        lines.append(f"- gene_values: {', '.join(summary['genes'][:10])}")
    if summary["traits"]:
        lines.append(f"- trait_values: {', '.join(summary['traits'][:10])}")
    if summary["pmids"]:
        lines.append(f"- pmid_values: {', '.join(summary['pmids'][:10])}")
    if limit is not None and limit >= 0:
        lines.append(f"- display_limit: {limit}")

    lines.extend(["", "## Results"])
    if not shown:
        lines.append("No evidence records returned.")
    else:
        lines.extend(
            render_table(
                ["#", "Species", "Gene", "BFTName", "pmid"],
                [
                    [
                        idx,
                        item.get("Species", ""),
                        item.get("Gene", ""),
                        item.get("BFTName", ""),
                        item.get("pmid", item.get("PMID", "")),
                    ]
                    for idx, item in enumerate(shown, start=1)
                ],
            )
        )

    lines.extend(["", "## Evidence"])
    if not shown:
        lines.append("No representative evidence available.")
    else:
        for idx, item in enumerate(shown[:5], start=1):
            lines.append(
                f"{idx}. [{item.get('Species', '-')}] [{item.get('Gene', '-')}] "
                f"[{item.get('BFTName', '-')}] PMID={item.get('pmid', item.get('PMID', '-'))}"
            )
            sentence = item.get("Sentence", "").strip() or "-"
            lines.append(f"   sentence: {sentence}")

    lines.extend(
        [
            "",
            "## Notes",
            "- This is a fixed-format evidence report.",
            "- The request URL above is the direct API jump link for this query.",
            "- Response schemas may differ across endpoints; missing fields are left blank.",
        ]
    )
    return "\n".join(lines)


def build_summary(data: Any) -> dict[str, Any]:
    if not isinstance(data, list):
        return {"type": type(data).__name__, "value": data}

    summary: dict[str, Any] = {"count": len(data)}
    if not data:
        return summary

    if all(isinstance(item, dict) for item in data):
        keys = Counter()
        species = Counter()
        genes = Counter()
        pmids = Counter()
        traits = Counter()
        for item in data:
            for key in item:
                keys[key] += 1
            if "Species" in item:
                species[item["Species"]] += 1
            if "Gene" in item:
                genes[item["Gene"]] += 1
            if "pmid" in item:
                pmids[str(item["pmid"])] += 1
            if "PMID" in item:
                pmids[str(item["PMID"])] += 1
            if "BFTName" in item:
                traits[item["BFTName"]] += 1
            if "name" in item and "tag" in item:
                traits[item["name"]] += 1
            if "name" in item and "sciName" in item and "Species" not in item:
                species[item["name"]] += 1

        summary["keys"] = sorted(keys)
        if species:
            summary["top_species"] = species.most_common(5)
        if genes:
            summary["top_genes"] = genes.most_common(5)
        if pmids:
            summary["top_pmids"] = pmids.most_common(5)
        if traits:
            summary["top_traits"] = traits.most_common(5)
        summary["sample"] = data[:3]
        return summary

    summary["sample"] = data[:3]
    return summary


def emit_output(data: Any, output_format: str, limit: int | None) -> None:
    if output_format == "json":
        print(json.dumps(trim_records(data, limit), ensure_ascii=False, indent=2))
        return
    summary = build_summary(data if limit is None else trim_records(data, limit))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def cmd_list(args: argparse.Namespace) -> int:
    url = build_list_request_url(args.base_url, args.kind)
    if args.show_url:
        print(url, file=sys.stderr)
    data = fetch_json(url, args.timeout)
    if args.output == "tree":
        if args.kind != "traits":
            raise SystemExit(unsupported_tree_message())
        print(
            render_trait_tree(
                args.base_url,
                url,
                data,
                args.limit,
                include_tags=args.tree_include_tags,
            )
        )
        return 0
    if args.output == "report":
        print(render_list_report(args.kind, args.base_url, url, data, args.limit))
        return 0
    emit_output(data, args.output, args.limit)
    return 0


def collect_filters(args: argparse.Namespace) -> dict[str, str]:
    filters: dict[str, str] = {}
    for field in SEARCH_FIELDS:
        value = getattr(args, field)
        if value:
            filters[field] = value
    return filters


def supported_combinations() -> str:
    combos = []
    for combo in sorted(SEARCH_ENDPOINTS):
        combos.append(" + ".join(combo))
    return "; ".join(combos)


def cmd_search(args: argparse.Namespace) -> int:
    filters = collect_filters(args)
    if len(filters) not in {1, 2}:
        raise SystemExit(
            "Provide exactly one or two filters among --gene, --species, --trait, --pmid."
        )

    combo = tuple(sorted(filters))
    endpoint = SEARCH_ENDPOINTS.get(combo)
    if endpoint is None:
        raise SystemExit(
            "Unsupported filter combination. Supported combinations: "
            f"{supported_combinations()}"
        )

    url = build_search_request_url(args.base_url, filters)
    if args.show_url:
        print(url, file=sys.stderr)
    data = fetch_json(url, args.timeout)
    if args.output == "tree":
        raise SystemExit(unsupported_tree_message())
    if args.output == "report":
        print(render_search_report(filters, args.base_url, url, data, args.limit))
        return 0
    emit_output(data, args.output, args.limit)
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL for the CucurLitBase API (default: {DEFAULT_BASE_URL})",
    )
    common.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    common.add_argument(
        "--output",
        choices=("json", "summary", "report", "tree"),
        default="summary",
        help="Emit raw JSON, a compact summary, a fixed-format report, or a tree view (default: summary)",
    )
    common.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit returned records before printing (default: 20, -1 for all)",
    )
    common.add_argument(
        "--show-url",
        action="store_true",
        help="Print the resolved request URL to stderr",
    )
    parser = argparse.ArgumentParser(
        description="Query verified CucurLitBase REST API endpoints.",
        parents=[common],
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list", help="Browse verified listing endpoints.", parents=[common]
    )
    list_parser.add_argument("kind", choices=tuple(LIST_ENDPOINTS))
    list_parser.add_argument(
        "--tree-include-tags",
        action="store_true",
        help="When using --output tree for traits, prefix each node with its hierarchical tag.",
    )
    list_parser.set_defaults(func=cmd_list)

    search_parser = subparsers.add_parser(
        "search",
        help="Run one-filter or two-filter evidence queries.",
        parents=[common],
    )
    for field in SEARCH_FIELDS:
        search_parser.add_argument(f"--{field}")
    search_parser.set_defaults(func=cmd_search)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
