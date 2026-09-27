#!/usr/bin/env python3
"""Paste one PNG from the Windows clipboard into a Medium story draft."""

from __future__ import annotations

import argparse
import ctypes
import os
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


NEW_STORY_URL = "https://medium.com/new-story"
PROFILE_DIR = Path(__file__).resolve().parents[1] / ".medium_feature_upload_profile"


def copy_png_to_windows_clipboard(image_path: Path) -> None:
    """Place PNG pixels on the Windows clipboard as a CF_DIB bitmap."""
    if os.name != "nt":
        raise RuntimeError("The image clipboard step requires Windows Python.")

    from io import BytesIO

    with Image.open(image_path) as image:
        bmp = BytesIO()
        image.convert("RGB").save(bmp, format="BMP")
    dib = bmp.getvalue()[14:]  # CF_DIB omits the BMP file header.

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GlobalAlloc.argtypes = (ctypes.c_uint, ctypes.c_size_t)
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = (ctypes.c_void_p,)
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = (ctypes.c_void_p,)
    kernel32.GlobalFree.argtypes = (ctypes.c_void_p,)
    user32.OpenClipboard.argtypes = (ctypes.c_void_p,)
    user32.OpenClipboard.restype = ctypes.c_bool
    user32.EmptyClipboard.restype = ctypes.c_bool
    user32.SetClipboardData.argtypes = (ctypes.c_uint, ctypes.c_void_p)
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.restype = ctypes.c_bool

    memory = kernel32.GlobalAlloc(0x0002, len(dib))  # GMEM_MOVEABLE
    if not memory:
        raise ctypes.WinError()
    pointer = kernel32.GlobalLock(memory)
    if not pointer:
        kernel32.GlobalFree(memory)
        raise ctypes.WinError()
    ctypes.memmove(pointer, dib, len(dib))
    kernel32.GlobalUnlock(memory)

    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(memory)
        raise ctypes.WinError()
    try:
        if not user32.EmptyClipboard():
            kernel32.GlobalFree(memory)
            raise ctypes.WinError()
        if not user32.SetClipboardData(8, memory):  # CF_DIB
            kernel32.GlobalFree(memory)
            raise ctypes.WinError()
        # Windows owns the memory after SetClipboardData succeeds.
    finally:
        user32.CloseClipboard()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("png", type=Path, help="PNG file to paste into a Medium story")
    args = parser.parse_args()
    image_path = args.png.expanduser().resolve()
    if not image_path.is_file() or image_path.suffix.lower() != ".png":
        parser.error(f"expected an existing PNG file, got: {image_path}")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="msedge",
            headless=False,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(NEW_STORY_URL, wait_until="domcontentloaded")
        input("Log in to Medium if needed. When the story editor is ready, press Enter: ")
        copy_png_to_windows_clipboard(image_path)
        input("Put the cursor at the desired insertion point in the editor, then press Enter: ")
        page.keyboard.press("Control+V")
        print("Ctrl+V sent. The browser will remain open; close its window when finished inspecting.")
        page.wait_for_event("close", timeout=0)
        context.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
