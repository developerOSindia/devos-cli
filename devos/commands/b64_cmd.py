"""
DeveloperOS CLI - Base64 Encoding / Decoding Tool
Zero-dependency RFC 4648 standard and URL-safe Base64 encoder/decoder.
"""

import argparse
import base64
import os
import sys
from typing import Optional


def encode_b64(data: bytes, url_safe: bool = False) -> str:
    """Encodes bytes into standard or URL-safe Base64 ASCII string."""
    if url_safe:
        return base64.urlsafe_b64encode(data).decode("ascii")
    return base64.b64encode(data).decode("ascii")


def decode_b64(text: str, url_safe: bool = False) -> bytes:
    """Decodes standard or URL-safe Base64 string with automatic padding recovery."""
    s = text.strip()
    if url_safe:
        s = s.replace("-", "+").replace("_", "/")
    rem = len(s) % 4
    if rem > 0:
        s += "=" * (4 - rem)
    return base64.b64decode(s.encode("ascii"))


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'b64' subcommand parser."""
    parser = subparsers.add_parser(
        "b64",
        help="Encode or decode Base64 data (standard or URL-safe)",
        description="Zero-dependency Base64 encoder and decoder supporting RFC 4648 standard and URL-safe variants.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Text to encode/decode, file path, or '-' to read from stdin",
    )
    parser.add_argument(
        "-d", "--decode",
        action="store_true",
        help="Decode Base64 payload back to plain text or binary",
    )
    parser.add_argument(
        "-u", "--url",
        action="store_true",
        help="Use URL-safe Base64 (- and _ instead of + and /)",
    )
    parser.add_argument(
        "-f", "--file",
        action="store_true",
        help="Explicitly treat input as a file path to encode/decode",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="File path to write decoded binary or encoded text output",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the b64 subcommand."""
    try:
        if args.file:
            if not args.input:
                sys.stderr.write("[ERROR] File path required when using --file flag.\n")
                return 1
            if not os.path.isfile(args.input):
                sys.stderr.write(f"[ERROR] File not found: {args.input}\n")
                return 1
            with open(args.input, "rb") as f:
                raw_bytes = f.read()
        elif not args.input or args.input == "-":
            raw_bytes = sys.stdin.buffer.read()
        elif os.path.isfile(args.input):
            with open(args.input, "rb") as f:
                raw_bytes = f.read()
        else:
            raw_bytes = args.input.encode("utf-8")

        if not raw_bytes:
            sys.stderr.write("[ERROR] No input provided to Base64 tool.\n")
            return 1

        if args.decode:
            # Decode base64 to bytes
            decoded = decode_b64(raw_bytes.decode("ascii", errors="replace"), url_safe=args.url)
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(decoded)
            else:
                try:
                    sys.stdout.write(decoded.decode("utf-8"))
                except UnicodeDecodeError:
                    # Binary output to stdout buffer
                    sys.stdout.buffer.write(decoded)
                if not decoded.endswith(b"\n"):
                    sys.stdout.write("\n")
            return 0

        else:
            # Encode bytes to base64
            encoded = encode_b64(raw_bytes, url_safe=args.url)
            if args.output:
                with open(args.output, "w", encoding="ascii") as f:
                    f.write(encoded + "\n")
            else:
                sys.stdout.write(encoded + "\n")
            return 0

    except Exception as err:
        sys.stderr.write(f"[ERROR] Base64 operation failed: {err}\n")
        return 1
