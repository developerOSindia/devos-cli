"""
DeveloperOS CLI - JWT Tool
Zero-dependency JWT claims inspection, header parsing, and expiration validation.
"""

import argparse
import base64
import datetime
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple


def b64url_decode(segment: str) -> bytes:
    """Decodes a base64url string with missing padding restoration."""
    segment = segment.strip().replace("-", "+").replace("_", "/")
    rem = len(segment) % 4
    if rem > 0:
        segment += "=" * (4 - rem)
    return base64.b64decode(segment)


def format_timestamp(ts: Any) -> Tuple[Optional[str], Optional[datetime.datetime]]:
    """Converts a Unix timestamp into a readable UTC date string."""
    try:
        ts_val = float(ts)
        dt = datetime.datetime.fromtimestamp(ts_val, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC"), dt
    except (ValueError, TypeError, OverflowError):
        return None, None


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Parses and decodes a JWT token without external cryptography dependencies.
    Returns a dictionary containing header, payload, signature, and metadata.
    """
    token = token.strip()
    parts = token.split(".")
    if len(parts) not in (2, 3):
        raise ValueError(f"Invalid JWT format: expected 3 dot-separated segments, got {len(parts)}")

    header_raw = parts[0]
    payload_raw = parts[1]
    signature_raw = parts[2] if len(parts) == 3 else ""

    try:
        header_bytes = b64url_decode(header_raw)
        header = json.loads(header_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to decode JWT header: {e}")

    try:
        payload_bytes = b64url_decode(payload_raw)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to decode JWT payload: {e}")

    # Inspect timestamps
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_ts = now_utc.timestamp()

    exp_readable, exp_dt = format_timestamp(payload.get("exp"))
    iat_readable, _ = format_timestamp(payload.get("iat"))
    nbf_readable, nbf_dt = format_timestamp(payload.get("nbf"))

    is_expired = False
    expiry_message = "No expiration specified (infinite lifetime)"
    if exp_dt is not None:
        delta = exp_dt.timestamp() - now_ts
        if delta < 0:
            is_expired = True
            secs_ago = int(abs(delta))
            expiry_message = f"EXPIRED {secs_ago}s ago ({exp_readable})"
        else:
            is_expired = False
            secs_left = int(delta)
            expiry_message = f"ACTIVE (expires in {secs_left}s at {exp_readable})"

    not_yet_valid = False
    if nbf_dt is not None:
        if now_ts < nbf_dt.timestamp():
            not_yet_valid = True

    return {
        "header": header,
        "payload": payload,
        "signature": signature_raw,
        "timestamps": {
            "exp_readable": exp_readable,
            "iat_readable": iat_readable,
            "nbf_readable": nbf_readable,
        },
        "is_expired": is_expired,
        "not_yet_valid": not_yet_valid,
        "expiry_message": expiry_message,
    }


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'jwt' subcommand parser."""
    parser = subparsers.add_parser(
        "jwt",
        help="Inspect and decode JWT tokens, claims, and headers",
        description="Zero-dependency JWT claims inspector, header parser, and expiration validator.",
    )
    parser.add_argument(
        "token",
        nargs="?",
        default=None,
        help="JWT string or file path containing the token (or stdin)",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="Print only the decoded header JSON",
    )
    parser.add_argument(
        "-c", "--claims", "--payload",
        dest="claims",
        action="store_true",
        help="Print only the decoded payload claims JSON",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output complete inspection result as structured JSON",
    )
    parser.add_argument(
        "--verify-exp",
        action="store_true",
        help="Verify expiration claim and return non-zero exit code if expired",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the jwt subcommand."""
    raw_token = args.token
    if not raw_token or raw_token == "-":
        raw_token = sys.stdin.read()
    elif os.path.isfile(raw_token):
        with open(raw_token, "r", encoding="utf-8") as f:
            raw_token = f.read()

    raw_token = raw_token.strip()
    if not raw_token:
        sys.stderr.write("[ERROR] No JWT token provided.\n")
        return 1

    try:
        data = decode_jwt(raw_token)
    except Exception as err:
        sys.stderr.write(f"[ERROR] {err}\n")
        return 1

    if args.verify_exp:
        if data["is_expired"]:
            sys.stderr.write(f"[EXPIRED] Token has expired: {data['expiry_message']}\n")
            return 1
        sys.stdout.write(f"[VALID] Token is active: {data['expiry_message']}\n")
        return 0

    if args.header:
        sys.stdout.write(json.dumps(data["header"], indent=2) + "\n")
        return 0

    if args.claims:
        sys.stdout.write(json.dumps(data["payload"], indent=2) + "\n")
        return 0

    if args.json:
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return 0

    # Default human-readable output
    alg = data["header"].get("alg", "UNKNOWN")
    typ = data["header"].get("typ", "JWT")
    out = [
        "============================================================",
        f" DeveloperOS JWT Inspector [Algorithm: {alg} | Type: {typ}]",
        "============================================================",
        "\n--- Header ---",
        json.dumps(data["header"], indent=2),
        "\n--- Payload (Claims) ---",
        json.dumps(data["payload"], indent=2),
        "\n--- Lifecycle & Timestamps ---",
        f"Status:             {'EXPIRED' if data['is_expired'] else ('NOT YET VALID' if data['not_yet_valid'] else 'ACTIVE')}",
        f"Expiration (exp):   {data['timestamps']['exp_readable'] or 'None'} -> {data['expiry_message']}",
        f"Issued At (iat):    {data['timestamps']['iat_readable'] or 'None'}",
        f"Not Before (nbf):   {data['timestamps']['nbf_readable'] or 'None'}",
        "\n--- Signature ---",
        f"{data['signature'][:32]}... ({len(data['signature'])} chars)" if len(data["signature"]) > 32 else (data["signature"] or "[None]"),
    ]
    sys.stdout.write("\n".join(out) + "\n")
    return 0
