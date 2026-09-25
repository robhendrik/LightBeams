#!/usr/bin/env python3
"""Validate, prepare, or create an unpublished Medium story draft."""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from medium_uploader.models import DisplayEquation, Figure, Paragraph, PullQuote, SectionHeading
from medium_uploader.prepare import PreparationError, prepare_article
from medium_uploader.validate import format_report, validate_article
from medium_uploader.clipboard_workflow import (
    build_clipboard_payload,
    copy_upload_assets,
    copy_plain_text_windows,
    copy_windows_clipboard,
    run_asset_assistant,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate, prepare, and copy a Medium-ready article.")
    parser.add_argument("article", type=Path, help="Path to the authoritative Markdown article")
    modes = parser.add_mutually_exclusive_group()
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
    if args.prepare_only:
        return 0

    try:
        upload_assets = copy_upload_assets(article)
    except OSError as exc:
        print(f"ERROR: Could not copy article upload assets: {exc}", file=sys.stderr)
        return 1
    try:
        payload = build_clipboard_payload(article)
        copy_windows_clipboard(payload)
    except (RuntimeError, OSError) as exc:
        print(f"ERROR: Could not prepare the Windows rich clipboard: {exc}", file=sys.stderr)
        return 1

    try:
        opened = webbrowser.open("https://medium.com/new-story")
    except Exception as exc:
        opened = False
        print(f"WARNING: Could not open Medium automatically: {exc}")
    if not opened:
        print("WARNING: Visit https://medium.com/new-story manually.")
    print("Article copied to clipboard.")
    print("In Medium:")
    print("  1. click in the title area")
    print("  2. press Ctrl+V")
    input("Press Enter here after you have pasted the article into Medium: ")
    assets = ([upload_assets.feature_image] if upload_assets.feature_image else []) + upload_assets.article_assets
    print(f"Upload assets folder: {upload_assets.directory}")
    if assets:
        print("After the article is pasted, follow the asset prompts to replace each visible placeholder.")
        try:
            run_asset_assistant(assets, copy_text=copy_plain_text_windows)
        except (RuntimeError, OSError) as exc:
            print(f"ERROR: Clipboard assistant stopped: {exc}", file=sys.stderr)
            return 1
    print("Review the story manually. No publication or submission action was performed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
