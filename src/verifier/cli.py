"""Command-line surface for Verifier.

This is a thin adapter over the (not-yet-built) surface-agnostic core. It exists now to
pin the *shape* of the interface — the ergonomic goal is that the obvious command is the
right one:

    verifier verify --claim "Tesla committed to net zero by 2035" \\
                    --url   https://example.com/tesla-report \\
                    [--quote "net zero by 2050"]

The verification engine arrives with the vertical slice (step C). Until then this
prints a clear not-implemented notice rather than pretending to verify.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verifier",
        description="Independently fact-check the citations an AI agent produces.",
    )
    sub = parser.add_subparsers(dest="command")

    verify = sub.add_parser("verify", help="verify a claim against its cited source URL")
    verify.add_argument("--claim", required=True, help="the claim to check")
    verify.add_argument("--url", required=True, help="the source URL the claim cites")
    verify.add_argument("--quote", default=None, help="optional quoted passage to locate")

    args = parser.parse_args(argv)

    if args.command != "verify":
        parser.print_help()
        return 1

    print(
        "verifier: the verification engine is not implemented yet (step C).\n"
        f"  claim: {args.claim}\n"
        f"  url:   {args.url}\n"
        f"  quote: {args.quote!r}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
