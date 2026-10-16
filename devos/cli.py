"""
DeveloperOS Unified CLI (devos)
Command-line entrypoint using standard library argparse.
Zero external dependencies, ultra-fast, 100% offline.
https://developeros.in
"""

import argparse
import sys
from typing import List, Optional

from devos import __version__
from devos.commands import (
    b64_cmd,
    cron_cmd,
    hash_cmd,
    json_cmd,
    jwt_cmd,
    list_cmd,
    uuid_cmd,
)

ASCII_BANNER = r"""
  ____                 _                         ___  ____  
 |  _ \  _____   _____| | ___  _ __   ___ _ __  / _ \/ ___| 
 | | | |/ _ \ \ / / _ \ |/ _ \| '_ \ / _ \ '__|| | | \___ \ 
 | |_| |  __/\ V /  __/ | (_) | |_) |  __/ |   | |_| |___) |
 |____/ \___| \_/ \___|_|\___/| .__/ \___|_|    \___/|____/ 
                              |_|                           
 DeveloperOS Unified Developer CLI v{version} • Zero Dependencies • Offline-First
 https://developeros.in
""".format(version=__version__)


def build_parser() -> argparse.ArgumentParser:
    """Builds the primary argparse argument parser."""
    parser = argparse.ArgumentParser(
        prog="devos",
        description=f"{ASCII_BANNER}\nUltra-fast developer utilities for the DeveloperOS ecosystem.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"devos {__version__}",
        help="Show program's version number and exit",
    )

    subparsers = parser.add_subparsers(
        title="Subcommands",
        dest="subcommand",
        metavar="<command>",
    )

    # Register all subcommands
    json_cmd.register_subparser(subparsers)
    jwt_cmd.register_subparser(subparsers)
    hash_cmd.register_subparser(subparsers)
    b64_cmd.register_subparser(subparsers)
    uuid_cmd.register_subparser(subparsers)
    cron_cmd.register_subparser(subparsers)
    list_cmd.register_subparser(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI execution routine."""
    parser = build_parser()

    # If no arguments provided, print banner and help
    args_to_parse = argv if argv is not None else sys.argv[1:]
    if not args_to_parse:
        sys.stdout.write(ASCII_BANNER + "\n")
        parser.print_help()
        return 0

    args = parser.parse_args(args_to_parse)

    subcommand_handlers = {
        "json": json_cmd.execute,
        "jwt": jwt_cmd.execute,
        "hash": hash_cmd.execute,
        "b64": b64_cmd.execute,
        "uuid": uuid_cmd.execute,
        "cron": cron_cmd.execute,
        "list": list_cmd.execute,
    }

    handler = subcommand_handlers.get(args.subcommand)
    if not handler:
        parser.print_help()
        return 1

    try:
        return handler(args)
    except KeyboardInterrupt:
        sys.stderr.write("\nOperation canceled by user.\n")
        return 130
    except BrokenPipeError:
        # Standard unix practice when output piped to head/grep terminates early
        return 0
    except Exception as exc:
        sys.stderr.write(f"[FATAL] Unexpected error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
