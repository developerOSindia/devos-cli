"""
DeveloperOS CLI - Cryptographic Hash Tool
SHA-256, SHA-512, MD5, and SHA-1 hashing for strings, streams, and files.
"""

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional

SUPPORTED_ALGORITHMS = ["sha256", "sha512", "md5", "sha1"]


def get_hashers(algorithms: List[str]) -> Dict[str, Any]:
    """Instantiates hashlib hashers for the specified algorithm names."""
    hashers = {}
    for alg in algorithms:
        alg_lower = alg.lower()
        if alg_lower == "sha256":
            hashers[alg_lower] = hashlib.sha256()
        elif alg_lower == "sha512":
            hashers[alg_lower] = hashlib.sha512()
        elif alg_lower == "md5":
            hashers[alg_lower] = hashlib.md5()
        elif alg_lower == "sha1":
            hashers[alg_lower] = hashlib.sha1()
        else:
            raise ValueError(f"Unsupported algorithm: {alg}")
    return hashers


def hash_bytes(data: bytes, algorithms: Optional[List[str]] = None) -> Dict[str, str]:
    """Computes cryptographic hashes for a byte buffer."""
    algs = algorithms or ["sha256"]
    hashers = get_hashers(algs)
    for h in hashers.values():
        h.update(data)
    return {alg: h.hexdigest() for alg, h in hashers.items()}


def hash_file(filepath: str, algorithms: Optional[List[str]] = None, chunk_size: int = 65536) -> Dict[str, str]:
    """Computes cryptographic hashes for a file streaming in memory-safe chunks."""
    algs = algorithms or ["sha256"]
    hashers = get_hashers(algs)
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            for h in hashers.values():
                h.update(chunk)
    return {alg: h.hexdigest() for alg, h in hashers.items()}


def hash_stream(stream, algorithms: Optional[List[str]] = None, chunk_size: int = 65536) -> Dict[str, str]:
    """Computes cryptographic hashes from a binary or text stream."""
    algs = algorithms or ["sha256"]
    hashers = get_hashers(algs)
    is_binary = hasattr(stream, "buffer")
    s = stream.buffer if is_binary else stream

    while True:
        chunk = s.read(chunk_size)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        for h in hashers.values():
            h.update(chunk)
    return {alg: h.hexdigest() for alg, h in hashers.items()}


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'hash' subcommand parser."""
    parser = subparsers.add_parser(
        "hash",
        help="Generate SHA-256, SHA-512, MD5, or SHA-1 hashes",
        description="Fast cryptographic hashing for text strings, piped streams, or files.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Input string, file path, or '-' to read from stdin",
    )
    parser.add_argument(
        "-a", "--algorithm",
        default="sha256",
        choices=["sha256", "sha512", "md5", "sha1", "all"],
        help="Hash algorithm to compute (default: sha256, or 'all')",
    )
    parser.add_argument(
        "-f", "--file",
        action="store_true",
        help="Explicitly treat input as a file path",
    )
    parser.add_argument(
        "-t", "--text",
        action="store_true",
        help="Explicitly treat input as literal text",
    )
    parser.add_argument(
        "--upper",
        action="store_true",
        help="Output hex digest in uppercase",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON object",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the hash subcommand."""
    target_algs = SUPPORTED_ALGORITHMS if args.algorithm == "all" else [args.algorithm]

    source_desc = "text"
    try:
        if args.file:
            if not args.input:
                sys.stderr.write("[ERROR] File path required when using --file flag.\n")
                return 1
            if not os.path.isfile(args.input):
                sys.stderr.write(f"[ERROR] File not found: {args.input}\n")
                return 1
            results = hash_file(args.input, target_algs)
            source_desc = f"file:{args.input}"

        elif args.text:
            if args.input is None:
                sys.stderr.write("[ERROR] Text input required when using --text flag.\n")
                return 1
            results = hash_bytes(args.input.encode("utf-8"), target_algs)

        elif not args.input or args.input == "-":
            results = hash_stream(sys.stdin, target_algs)
            source_desc = "stdin"

        elif os.path.isfile(args.input):
            results = hash_file(args.input, target_algs)
            source_desc = f"file:{args.input}"

        else:
            results = hash_bytes(args.input.encode("utf-8"), target_algs)

    except Exception as err:
        sys.stderr.write(f"[ERROR] Hashing failed: {err}\n")
        return 1

    if args.upper:
        results = {k: v.upper() for k, v in results.items()}

    if args.json:
        out_data = {
            "source": source_desc,
            "hashes": results,
        }
        sys.stdout.write(json.dumps(out_data, indent=2) + "\n")
        return 0

    if len(target_algs) == 1:
        # Just print the hash string directly for easy pipe/script use
        sys.stdout.write(list(results.values())[0] + "\n")
    else:
        # Formatted multi-hash listing
        name_map = {
            "sha256": "SHA-256",
            "sha512": "SHA-512",
            "sha1": "SHA-1  ",
            "md5": "MD5    ",
        }
        for alg in target_algs:
            label = name_map.get(alg, alg.upper())
            sys.stdout.write(f"{label}: {results[alg]}\n")

    return 0
