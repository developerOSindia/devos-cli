"""
DeveloperOS CLI - UUID Generator Tool
Zero-dependency RFC 4122 compliant UUIDv4 batch generation.
"""

import argparse
import json
import sys
import uuid
from typing import List


def generate_uuids(count: int = 1, upper: bool = False, no_hyphens: bool = False) -> List[str]:
    """Generates a list of random RFC 4122 UUIDv4 identifiers."""
    if count < 1:
        raise ValueError("Count must be at least 1")

    results = []
    for _ in range(count):
        u = uuid.uuid4()
        s = u.hex if no_hyphens else str(u)
        if upper:
            s = s.upper()
        results.append(s)
    return results


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'uuid' subcommand parser."""
    parser = subparsers.add_parser(
        "uuid",
        help="Generate RFC 4122 UUIDv4 identifiers",
        description="Fast, random RFC 4122 UUIDv4 generator supporting bulk counts and formats.",
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="Number of UUIDs to generate (default: 1)",
    )
    parser.add_argument(
        "-u", "--upper",
        action="store_true",
        help="Format UUIDs in uppercase",
    )
    parser.add_argument(
        "--no-hyphens",
        action="store_true",
        help="Omit hyphens (32-character continuous hexadecimal)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output generated UUIDs as a JSON list",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the uuid subcommand."""
    try:
        uuids = generate_uuids(
            count=args.count,
            upper=args.upper,
            no_hyphens=args.no_hyphens,
        )
    except Exception as err:
        sys.stderr.write(f"[ERROR] Failed to generate UUIDs: {err}\n")
        return 1

    if args.json:
        sys.stdout.write(json.dumps(uuids, indent=2) + "\n")
    else:
        for u in uuids:
            sys.stdout.write(u + "\n")

    return 0
