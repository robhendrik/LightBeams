#!/usr/bin/env python3
"""Command-line entry point for Medium article validation and preparation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from medium_uploader.models import DisplayEquation, Figure, Paragraph, PullQuote, SectionHeading
from medium_uploader.prepare import PreparationError, prepare_article
from medium_uploader.validate import format_report, validate_article


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate or prepare a Medium-ready Markdown article.")
    parser.add_argument("article", type=Path, help="Path to the authoritative Markdown article")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate-only", action="store_true", help="Validate without preparing or uploading")
    modes.add_argument("--prepare-only", action="store_true", help="Validate and prepare assets without opening a browser")
    args = parser.parse_args(argv)
    result = validate_article(args.article)
    print(format_report(result))
    if result.has_errors:
        return 1
    if args.validate_only:
        return 0
    try:
        article = prepare_article(args.article, result)
    except PreparationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    counts = {
        "paragraphs": sum(isinstance(block, Paragraph) for block in article.blocks),
        "headings": sum(isinstance(block, SectionHeading) for block in article.blocks),
        "figures": sum(isinstance(block, Figure) for block in article.blocks),
        "pull quotes": sum(isinstance(block, PullQuote) for block in article.blocks),
        "equations": sum(isinstance(block, DisplayEquation) for block in article.blocks),
    }
    count_text = ", ".join(f"{count} {name}" for name, count in counts.items())
    print(f"Prepared: {article.title}")
    print(f"Content: {count_text}")
    print(f"Build directory: {article.build_dir}")
    for block in article.blocks:
        if isinstance(block, DisplayEquation):
            print(f"Equation: {block.rendered_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
