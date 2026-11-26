#!/usr/bin/env python3
"""Search documentation pages bundled with this skill.

Usage: python scripts/search_docs.py "search terms" [--limit 5]

Prints the best-matching pages (path, title) and the lines that matched, so an agent can
open the right page instead of reading every page. Standard library only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from search_engine import search
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from devkit.search_engine import search

REFERENCES = Path(__file__).resolve().parent.parent / "references"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", nargs="+", help="search terms")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    results = search(REFERENCES, " ".join(args.query), args.limit)
    if not results:
        print("No matching pages. Try other terms, or browse the index in SKILL.md.")
        return 1
    for result in results:
        print(f"references/{result.path}  ({result.title})")
        for number, line in result.lines:
            print(f"    {number}: {line[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
