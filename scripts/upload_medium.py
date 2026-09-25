#!/usr/bin/env python3
"""Command-line entry point for Medium article validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from medium_uploader.validate import format_report, validate_article


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Medium-ready Markdown article.")
    parser.add_argument("article", type=Path, help="Path to the authoritative Markdown article")
    parser.add_argument("--validate-only", action="store_true", help="Validate and report findings without preparing or uploading")
    args = parser.parse_args(argv)
    if not args.validate_only:
        parser.error("Phase 1 supports --validate-only only.")
    result = validate_article(args.article)
    print(format_report(result))
    return 1 if result.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
