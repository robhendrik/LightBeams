#!/usr/bin/env python3
"""Experiment: upload one PNG to an unpublished Medium story draft."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


NEW_STORY_URL = "https://medium.com/new-story"
PROFILE_DIR = Path(__file__).resolve().parents[1] / ".medium_feature_upload_profile"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("png", type=Path, help="PNG file to upload into a new Medium story")
    args = parser.parse_args()
    image_path = args.png.expanduser().resolve()
    if not image_path.is_file() or image_path.suffix.lower() != ".png":
        parser.error(f"expected an existing PNG file, got: {image_path}")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(NEW_STORY_URL, wait_until="domcontentloaded")
        input(
            "Log in manually if needed, then wait until the new story editor is ready. "
            "Press Enter here to insert the PNG: "
        )

        editor = page.locator('[contenteditable="true"][role="textbox"]').first
        editor.wait_for(state="visible", timeout=30_000)
        editor.click()

        add_image = page.get_by_role("button", name="Add an image", exact=True)
        image_button = page.get_by_role("button", name="Image", exact=True)
        image_menu_item = page.get_by_role("menuitem", name="Image", exact=True)
        with page.expect_file_chooser(timeout=8_000) as chooser_info:
            if add_image.count() and add_image.first.is_visible():
                add_image.first.click()
            elif image_button.count() and image_button.first.is_visible():
                image_button.first.click()
            elif image_menu_item.count() and image_menu_item.first.is_visible():
                image_menu_item.first.click()
            else:
                add_block = page.get_by_role("button", name="Add a block", exact=True)
                if not add_block.count() or not add_block.first.is_visible():
                    raise RuntimeError("Could not find Medium's accessible image insertion control.")
                add_block.first.click()
                page.get_by_role("menuitem", name="Image", exact=True).click()
        chooser_info.value.set_files(str(image_path))
        page.get_by_test_id("editorImageParagraph").last.wait_for(state="visible", timeout=30_000)
        print(f"Uploaded {image_path} into the story editor. The browser will stay open for inspection.")
        print("This script does not click Publish, Submit, or any publication control.")
        page.wait_for_event("close", timeout=0)
        context.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
