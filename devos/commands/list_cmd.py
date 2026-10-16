"""
DeveloperOS CLI - Tool Registry & Ecosystem Directory
Lists all DeveloperOS suites, tools, categories, and live links.
Zero-dependency, offline-first execution with local registry fallback.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Embedded complete catalog for guaranteed 100% offline standalone usage
EMBEDDED_CATALOG: Dict[str, Any] = {
    "ecosystem": {
        "name": "DeveloperOS",
        "website": "https://developeros.in",
        "toolkit": "https://toolkit.developeros.in",
        "github": "https://github.com/developerOSindia",
    },
    "suites": [
        {
            "id": "suite-web-craft",
            "name": "Web & Frontend Craft Suite",
            "category": "web",
            "url": "https://web.toolkit.developeros.in",
            "description": "Essential web development utilities: CSS generators, meta-tag builders, HTML sanitizers.",
        },
        {
            "id": "suite-api-network",
            "name": "API & Network Suite",
            "category": "api",
            "url": "https://api.toolkit.developeros.in",
            "description": "HTTP request builders, cURL converters, JWT decoders, webhook debuggers.",
        },
        {
            "id": "suite-crypto-security",
            "name": "Cryptography & Security Suite",
            "category": "security",
            "url": "https://crypto.toolkit.developeros.in",
            "description": "Secure hashing algorithms, HMAC signatures, UUID/ULID generation, secret masking.",
        },
        {
            "id": "suite-data-convert",
            "name": "Data Conversion & Serialization Suite",
            "category": "data",
            "url": "https://data.toolkit.developeros.in",
            "description": "Bidirectional converters for JSON, YAML, TOML, XML, CSV, diff inspectors.",
        },
        {
            "id": "suite-cloud-devops",
            "name": "Cloud & DevOps Configuration Suite",
            "category": "devops",
            "url": "https://devops.toolkit.developeros.in",
            "description": "Dockerfile linters, Kubernetes manifest validators, cron humanizers, CIDR calculators.",
        },
        {
            "id": "suite-code-refactor",
            "name": "Code Refactoring & Syntax Suite",
            "category": "code",
            "url": "https://code.toolkit.developeros.in",
            "description": "Regex testers, AST inspectors, code minifiers, prettifiers, snippet generators.",
        },
        {
            "id": "suite-db-sql",
            "name": "Database & SQL Utilities Suite",
            "category": "database",
            "url": "https://sql.toolkit.developeros.in",
            "description": "SQL query formatters, mock schema builders, synthetic tabular data generators.",
        },
        {
            "id": "suite-media-assets",
            "name": "Media & Asset Processing Suite",
            "category": "media",
            "url": "https://media.toolkit.developeros.in",
            "description": "Base64 image encoders, SVG optimizers, color palette extractors, aspect ratio calculators.",
        },
        {
            "id": "suite-doc-specs",
            "name": "Documentation & Specifications Suite",
            "category": "documentation",
            "url": "https://docs.toolkit.developeros.in",
            "description": "Markdown previewers, OpenAPI 3.0 visualizers, changelog generators, README builders.",
        },
        {
            "id": "suite-perf-testing",
            "name": "Performance & Benchmark Suite",
            "category": "performance",
            "url": "https://perf.toolkit.developeros.in",
            "description": "Payload size calculators, regex execution benchmarks, network latency estimators.",
        },
    ],
    "flagship": [
        {
            "id": "api-sentinel",
            "name": "API Sentinel",
            "category": "flagship",
            "url": "https://sentinel.developeros.in",
            "description": "High-performance API health monitoring, contract validation, and mock server orchestration.",
        },
        {
            "id": "data-forge",
            "name": "Data Forge",
            "category": "flagship",
            "url": "https://forge.developeros.in",
            "description": "Multi-dialect relational schema designer, synthetic dataset synthesis, and SQL exporter.",
        },
        {
            "id": "diagram-studio",
            "name": "Diagram Studio",
            "category": "flagship",
            "url": "https://diagrams.developeros.in",
            "description": "Architecture diagrams, flowcharts, sequence charts, and visual C4 system models.",
        },
    ],
    "tools": [
        {
            "id": "web-meta-tag-generator",
            "name": "OpenGraph & Meta Tag Generator",
            "category": "web",
            "suite_id": "suite-web-craft",
            "url": "https://web.toolkit.developeros.in",
            "description": "Generate and preview valid HTML meta tags, OpenGraph cards, and Twitter Cards.",
        },
        {
            "id": "web-css-glassmorphism",
            "name": "CSS Glassmorphism & Shadow Builder",
            "category": "web",
            "suite_id": "suite-web-craft",
            "url": "https://web.toolkit.developeros.in",
            "description": "Interactive generator for modern CSS backdrop-filter, gradients, and box-shadows.",
        },
        {
            "id": "api-curl-to-python",
            "name": "cURL Command to Code Converter",
            "category": "api",
            "suite_id": "suite-api-network",
            "url": "https://api.toolkit.developeros.in",
            "description": "Parse raw cURL commands into clean Python (requests/httpx) and JavaScript (fetch) code.",
        },
        {
            "id": "api-jwt-inspector",
            "name": "Client-Side JWT Inspector",
            "category": "api",
            "suite_id": "suite-api-network",
            "url": "https://api.toolkit.developeros.in",
            "description": "Zero-dependency JWT claims inspector, header parser, and expiration validator.",
        },
        {
            "id": "crypto-hash-generator",
            "name": "Multi-Algorithm Hash Generator",
            "category": "security",
            "suite_id": "suite-crypto-security",
            "url": "https://crypto.toolkit.developeros.in",
            "description": "Compute SHA-256, SHA-512, MD5, and SHA-1 hashes from text strings or files.",
        },
        {
            "id": "crypto-uuid-ulid-gen",
            "name": "UUID / ULID Cryptographic Generator",
            "category": "security",
            "suite_id": "suite-crypto-security",
            "url": "https://crypto.toolkit.developeros.in",
            "description": "Generate secure RFC 4122 UUIDv4 and timestamp-ordered ULID identifiers.",
        },
        {
            "id": "data-json-yaml-converter",
            "name": "JSON <-> YAML <-> TOML Converter",
            "category": "data",
            "suite_id": "suite-data-convert",
            "url": "https://data.toolkit.developeros.in",
            "description": "Convert, format, and validate structured data between JSON, YAML, and TOML schemas.",
        },
        {
            "id": "data-csv-to-json",
            "name": "CSV to JSON / JSON to CSV Transformer",
            "category": "data",
            "suite_id": "suite-data-convert",
            "url": "https://data.toolkit.developeros.in",
            "description": "Tabular data transformer supporting custom delimiters, header auto-detection, and nested objects.",
        },
        {
            "id": "cloud-cron-parser",
            "name": "Cron Expression Explainer & Schedule Calculator",
            "category": "devops",
            "suite_id": "suite-cloud-devops",
            "url": "https://devops.toolkit.developeros.in",
            "description": "Decode complex cron schedules into plain English and preview upcoming trigger times.",
        },
        {
            "id": "cloud-cidr-calculator",
            "name": "IP & CIDR Subnet Calculator",
            "category": "devops",
            "suite_id": "suite-cloud-devops",
            "url": "https://devops.toolkit.developeros.in",
            "description": "Calculate subnet masks, broadcast addresses, usable IP ranges, and CIDR block hierarchies.",
        },
        {
            "id": "code-regex-tester",
            "name": "Regular Expression Tester & Match Explainer",
            "category": "code",
            "suite_id": "suite-code-refactor",
            "url": "https://code.toolkit.developeros.in",
            "description": "Test regex patterns in real-time with group capture visualization and syntax explanations.",
        },
        {
            "id": "code-ast-inspector",
            "name": "Python AST Tree Visualizer",
            "category": "code",
            "suite_id": "suite-code-refactor",
            "url": "https://code.toolkit.developeros.in",
            "description": "Inspect and navigate concrete Python Abstract Syntax Trees for metaprogramming and static analysis.",
        },
        {
            "id": "db-sql-formatter",
            "name": "SQL Query Formatter & Minifier",
            "category": "database",
            "suite_id": "suite-db-sql",
            "url": "https://sql.toolkit.developeros.in",
            "description": "Beautify, uppercase keywords, and clean dialect-specific SQL queries (PostgreSQL, MySQL, SQLite).",
        },
        {
            "id": "db-mock-generator",
            "name": "Relational Mock Data Generator",
            "category": "database",
            "suite_id": "suite-db-sql",
            "url": "https://sql.toolkit.developeros.in",
            "description": "Synthesize realistic database rows with foreign keys, emails, dates, and numeric distributions.",
        },
        {
            "id": "media-base64-converter",
            "name": "Base64 Image & Data URI Encoder/Decoder",
            "category": "media",
            "suite_id": "suite-media-assets",
            "url": "https://media.toolkit.developeros.in",
            "description": "Convert images (PNG, JPEG, SVG, WebP) to CSS/HTML data URIs and vice versa.",
        },
        {
            "id": "media-svg-cleaner",
            "name": "SVG Optimizer & Path Cleaner",
            "category": "media",
            "suite_id": "suite-media-assets",
            "url": "https://media.toolkit.developeros.in",
            "description": "Strip redundant XML metadata, optimize path definitions, and reduce SVG file size.",
        },
        {
            "id": "doc-markdown-editor",
            "name": "Markdown Editor & Realtime GitHub Previewer",
            "category": "documentation",
            "suite_id": "suite-doc-specs",
            "url": "https://docs.toolkit.developeros.in",
            "description": "Side-by-side GFM Markdown authoring with syntax highlighting and table generator.",
        },
        {
            "id": "doc-openapi-viewer",
            "name": "OpenAPI / Swagger Spec Validator",
            "category": "documentation",
            "suite_id": "suite-doc-specs",
            "url": "https://docs.toolkit.developeros.in",
            "description": "Interactive documentation viewer and syntax validator for OpenAPI 3.0/3.1 specifications.",
        },
        {
            "id": "perf-payload-estimator",
            "name": "API Payload Size & Compression Estimator",
            "category": "performance",
            "suite_id": "suite-perf-testing",
            "url": "https://perf.toolkit.developeros.in",
            "description": "Simulate Gzip and Brotli compression savings for REST and GraphQL API payloads.",
        },
        {
            "id": "perf-latency-calc",
            "name": "Global Network Latency Calculator",
            "category": "performance",
            "suite_id": "suite-perf-testing",
            "url": "https://perf.toolkit.developeros.in",
            "description": "Model cross-region cloud latency, RTT variations, and CDN cache hit performance.",
        },
    ],
}


def load_tools_catalog() -> Dict[str, Any]:
    """
    Returns the complete DeveloperOS tools catalog.
    Checks for workspace files if available, falling back gracefully to embedded catalog.
    """
    # Look for local workspace registry files
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "infrastructure" / "registry" / "tools_registry.json",
        Path(__file__).resolve().parent.parent.parent / "registry" / "tools_registry.json",
    ]
    for p in candidates:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                suites_map = {s["id"]: s for s in data.get("suites", [])}
                merged_tools = []
                for t in data.get("tools", []):
                    suite = suites_map.get(t.get("suite_id", ""), {})
                    merged_tools.append({
                        "id": t.get("id"),
                        "name": t.get("name"),
                        "category": t.get("category", suite.get("category", "general")),
                        "suite_id": t.get("suite_id"),
                        "url": suite.get("deployment_url", "https://toolkit.developeros.in"),
                        "description": t.get("description", ""),
                    })
                return {
                    "ecosystem": EMBEDDED_CATALOG["ecosystem"],
                    "suites": data.get("suites", EMBEDDED_CATALOG["suites"]),
                    "flagship": EMBEDDED_CATALOG["flagship"],
                    "tools": merged_tools or EMBEDDED_CATALOG["tools"],
                }
            except Exception:
                pass

    return EMBEDDED_CATALOG


def get_all_tools() -> List[Dict[str, Any]]:
    """Retrieves all tools including flagship apps."""
    catalog = load_tools_catalog()
    tools = list(catalog.get("tools", []))
    for app in catalog.get("flagship", []):
        tools.append({
            "id": app["id"],
            "name": app["name"],
            "category": "flagship",
            "suite_id": "flagship",
            "url": app["url"],
            "description": app["description"],
        })
    return tools


def filter_tools(
    tools: List[Dict[str, Any]],
    category: Optional[str] = None,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filters tools by category and text search query."""
    res = tools
    if category:
        cat_lower = category.lower().strip()
        res = [t for t in res if t.get("category", "").lower() == cat_lower]

    if query:
        q = query.lower().strip()
        res = [
            t for t in res
            if q in t.get("id", "").lower()
            or q in t.get("name", "").lower()
            or q in t.get("description", "").lower()
            or q in t.get("category", "").lower()
        ]

    return res


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'list' subcommand parser."""
    parser = subparsers.add_parser(
        "list",
        help="List all DeveloperOS tools with categories and live links",
        description="Browse the complete catalog of DeveloperOS tools, suites, and flagship applications.",
    )
    parser.add_argument(
        "-c", "--category",
        default=None,
        help="Filter tools by category (web, api, security, data, devops, code, database, media, documentation, performance, flagship)",
    )
    parser.add_argument(
        "-s", "--search",
        default=None,
        help="Filter tools by search query across name, id, and description",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display extended descriptions and suite details",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output tools catalog as structured JSON",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the list subcommand."""
    catalog = load_tools_catalog()
    all_tools = get_all_tools()
    filtered = filter_tools(all_tools, category=args.category, query=args.search)

    if args.json:
        payload = {
            "ecosystem": catalog["ecosystem"],
            "total_tools": len(filtered),
            "tools": filtered,
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0

    sys.stdout.write("================================================================================\n")
    sys.stdout.write("  DeveloperOS Tools Ecosystem Directory (https://developeros.in)\n")
    sys.stdout.write(f"  Showing {len(filtered)} tool(s)")
    if args.category:
        sys.stdout.write(f" [Category: {args.category}]")
    if args.search:
        sys.stdout.write(f" [Search: '{args.search}']")
    sys.stdout.write("\n================================================================================\n\n")

    # Group by category
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for t in filtered:
        cat = t.get("category", "other").upper()
        by_category.setdefault(cat, []).append(t)

    for cat_name, cat_tools in sorted(by_category.items()):
        sys.stdout.write(f"[{cat_name}]\n")
        for tool in sorted(cat_tools, key=lambda x: x["name"]):
            name = tool["name"]
            tool_id = tool["id"]
            url = tool.get("url", "https://developeros.in")
            desc = tool.get("description", "")
            sys.stdout.write(f"  * {name} ({tool_id})\n")
            sys.stdout.write(f"    Live Link: {url}\n")
            if args.verbose and desc:
                sys.stdout.write(f"    About:     {desc}\n")
        sys.stdout.write("\n")

    return 0
