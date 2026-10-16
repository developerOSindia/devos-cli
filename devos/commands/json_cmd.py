"""
DeveloperOS CLI - JSON Tool
Formatting, minification, and RFC 8259 syntax validation.
"""

import argparse
import json
import os
import sys
from typing import Tuple, Optional


def validate_json(text: str) -> Tuple[bool, str, Optional[int], Optional[int]]:
    """
    Validates whether a string is valid JSON according to RFC 8259.
    Returns (is_valid, message, line, column).
    """
    if not text.strip():
        return False, "Empty input is not valid JSON", 1, 1

    try:
        json.loads(text)
        return True, "Valid RFC 8259 JSON", None, None
    except json.JSONDecodeError as err:
        return False, err.msg, err.lineno, err.colno


def format_json(text: str, indent: int = 2, sort_keys: bool = False, minify: bool = False) -> str:
    """
    Formats or minifies a JSON string.
    Raises json.JSONDecodeError if invalid.
    """
    obj = json.loads(text)
    if minify:
        return json.dumps(obj, separators=(",", ":"), sort_keys=sort_keys)
    return json.dumps(obj, indent=indent, sort_keys=sort_keys)


def read_input_payload(source: Optional[str]) -> str:
    """Reads payload from a direct string, file path, or stdin."""
    if not source or source == "-":
        return sys.stdin.read()
    if os.path.isfile(source):
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
    return source


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'json' subcommand parser."""
    parser = subparsers.add_parser(
        "json",
        help="Format, minify, and validate JSON payloads",
        description="Zero-dependency JSON formatter, minifier, and RFC 8259 syntax validator.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="JSON string, file path, or '-' to read from stdin",
    )
    parser.add_argument(
        "-i", "--indent",
        type=int,
        default=2,
        help="Indentation spaces for formatting (default: 2)",
    )
    parser.add_argument(
        "-s", "--sort-keys",
        action="store_true",
        help="Sort dictionary keys alphabetically",
    )
    parser.add_argument(
        "-m", "--minify",
        action="store_true",
        help="Minify JSON output (compact separators, no whitespace)",
    )
    parser.add_argument(
        "-v", "--validate",
        action="store_true",
        help="Validate JSON syntax without outputting formatted payload",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output during validation (exit code only)",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the json subcommand."""
    try:
        content = read_input_payload(args.input)
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to read input: {e}\n")
        return 1

    if not content.strip():
        sys.stderr.write("[ERROR] No JSON input provided.\n")
        return 1

    if args.validate:
        is_valid, msg, line, col = validate_json(content)
        if is_valid:
            if not args.quiet:
                sys.stdout.write(f"[VALID] Valid RFC 8259 JSON payload ({len(content.encode('utf-8'))} bytes).\n")
            return 0
        else:
            if not args.quiet:
                sys.stderr.write(f"[INVALID] Syntax error: {msg} (line {line}, column {col})\n")
            return 1

    try:
        formatted = format_json(
            content,
            indent=args.indent,
            sort_keys=args.sort_keys,
            minify=args.minify,
        )
        sys.stdout.write(formatted + "\n")
        return 0
    except json.JSONDecodeError as err:
        sys.stderr.write(f"[ERROR] Invalid JSON: {err.msg} (line {err.lineno}, column {err.colno})\n")
        return 1
