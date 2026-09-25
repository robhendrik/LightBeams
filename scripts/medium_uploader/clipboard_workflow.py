"""Rich clipboard rendering and the manual asset insertion assistant."""

from __future__ import annotations

import ctypes
import html
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable, TextIO

import mistune

from .models import Article, DisplayEquation, Figure, Paragraph, PullQuote, SectionHeading


@dataclass(frozen=True)
class ClipboardPayload:
    html: str
    plain_text: str
    cf_html: bytes


@dataclass(frozen=True)
class ClipboardAsset:
    label: str
    kind: str
    path: str
    caption: str | None = None
    alt_text: str | None = None
    source: str | None = None


class _PlainText(HTMLParser):
    """Extract readable clipboard fallback text and retain link destinations."""

    _BLOCKS = {"p", "h1", "h2", "h3", "h4", "blockquote", "li", "div"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[tuple[int, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._BLOCKS and self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append((len(self.parts), href))

    def handle_endtag(self, tag):
        if tag == "a" and self.links:
            index, href = self.links.pop()
            text = "".join(self.parts[index:]).strip()
            if text and text != href:
                self.parts.append(f" ({href})")
        if tag in self._BLOCKS and self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def _plain_text(fragment: str) -> str:
    parser = _PlainText()
    parser.feed(fragment)
    return re.sub(r"\n{3,}", "\n\n", "".join(parser.parts)).strip()


def _inline_markdown(markdown_renderer, text: str) -> str:
    rendered = markdown_renderer(text).strip()
    if rendered.startswith("<p>") and rendered.endswith("</p>"):
        return rendered[3:-4]
    return rendered


def build_asset_sequence(article: Article) -> list[ClipboardAsset]:
    """Build the manual insertion queue in body document order."""
    assets: list[ClipboardAsset] = []
    figure_index = 0
    equation_index = 0
    for block in article.blocks:
        if isinstance(block, Figure):
            figure_index += 1
            assets.append(ClipboardAsset(
                label=f"[[FIGURE_{figure_index:02d}]]",
                kind="Figure",
                path=str(block.source_path),
                caption=block.caption,
                alt_text=block.alt_text,
                source=block.source_attribution,
            ))
        elif isinstance(block, DisplayEquation):
            equation_index += 1
            assets.append(ClipboardAsset(
                label=f"[[EQUATION_{equation_index:02d}]]",
                kind="Equation",
                path=str(block.rendered_path),
                alt_text=f"Display equation {equation_index}",
            ))
    return assets


def _cf_html(document: str) -> bytes:
    start_marker = "<!--StartFragment-->"
    end_marker = "<!--EndFragment-->"
    fragment = document
    html_document = f"<html><body>{start_marker}{fragment}{end_marker}</body></html>"
    template = (
        "Version:0.9\r\n"
        "StartHTML:{start_html:010d}\r\n"
        "EndHTML:{end_html:010d}\r\n"
        "StartFragment:{start_fragment:010d}\r\n"
        "EndFragment:{end_fragment:010d}\r\n"
    )
    empty_header = template.format(start_html=0, end_html=0, start_fragment=0, end_fragment=0).encode("ascii")
    html_bytes = html_document.encode("utf-8")
    fragment_start_in_html = html_bytes.index(start_marker.encode("ascii")) + len(start_marker)
    fragment_end_in_html = html_bytes.index(end_marker.encode("ascii"))
    header_size = len(empty_header)
    return template.format(
        start_html=header_size,
        end_html=header_size + len(html_bytes),
        start_fragment=header_size + fragment_start_in_html,
        end_fragment=header_size + fragment_end_in_html,
    ).encode("ascii") + html_bytes


def build_clipboard_payload(article: Article) -> ClipboardPayload:
    """Render prepared typed blocks as Medium-friendly rich HTML and plain text."""
    markdown = mistune.create_markdown(plugins=["table", "strikethrough"])
    assets = build_asset_sequence(article)
    asset_iter = iter(assets)
    html_blocks: list[str] = []
    if article.title:
        html_blocks.append(f"<h1>{_inline_markdown(markdown, article.title)}</h1>")
    if article.subtitle:
        html_blocks.append(f"<h3>{_inline_markdown(markdown, article.subtitle)}</h3>")

    for block in article.blocks:
        if isinstance(block, Paragraph):
            html_blocks.append(markdown(block.text).strip())
        elif isinstance(block, SectionHeading):
            html_blocks.append(f"<h2>{_inline_markdown(markdown, block.text)}</h2>")
        elif isinstance(block, PullQuote):
            rendered = markdown(block.text).strip()
            html_blocks.append(f"<blockquote>{rendered}</blockquote>")
        elif isinstance(block, (Figure, DisplayEquation)):
            asset = next(asset_iter)
            html_blocks.append(f"<p>{html.escape(asset.label)}</p>")
    if article.footnotes:
        html_blocks.append("<h2>Notes</h2>")
        html_blocks.extend(f"<p>{html.escape(note.marker)} {_inline_markdown(markdown, note.text)}</p>" for note in article.footnotes)

    content = "\n".join(html_blocks)
    document = f'<meta charset="utf-8"><div>{content}</div>'
    plain = _plain_text(content)
    return ClipboardPayload(html=document, plain_text=plain, cf_html=_cf_html(document))


def copy_windows_clipboard(payload: ClipboardPayload) -> None:
    """Set Windows CF_HTML and CF_UNICODETEXT clipboard formats via Win32."""
    if sys.platform != "win32":
        raise RuntimeError("Rich clipboard copying is supported on Windows for this workflow.")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    cf_unicode_text = 13
    _configure_win32_clipboard_apis(user32, kernel32)
    cf_html = user32.RegisterClipboardFormatW("HTML Format")
    if not cf_html:
        raise OSError("Could not register the Windows HTML clipboard format.")
    if not user32.OpenClipboard(None):
        raise OSError("Could not open the Windows clipboard.")
    allocated: list[int] = []
    try:
        user32.EmptyClipboard()
        for format_id, data in (
            (cf_html, payload.cf_html + b"\x00"),
            (cf_unicode_text, (payload.plain_text + "\x00").encode("utf-16-le")),
        ):
            handle = kernel32.GlobalAlloc(0x0002, len(data))  # GMEM_MOVEABLE
            if not handle:
                raise OSError("Could not allocate Windows clipboard memory.")
            allocated.append(handle)
            pointer = kernel32.GlobalLock(handle)
            if not pointer:
                raise OSError("Could not lock Windows clipboard memory.")
            try:
                ctypes.memmove(pointer, data, len(data))
            finally:
                kernel32.GlobalUnlock(handle)
            if not user32.SetClipboardData(format_id, handle):
                raise OSError("Could not set a Windows clipboard format.")
            allocated.remove(handle)  # Windows owns it after SetClipboardData.
    finally:
        user32.CloseClipboard()
        for handle in allocated:
            kernel32.GlobalFree(handle)


def run_asset_assistant(
    assets: list[ClipboardAsset],
    *,
    copy_text: Callable[[str], None],
    input_fn: Callable[[str], str] = input,
    output: TextIO = sys.stdout,
) -> None:
    """Guide manual image insertion and copy caption/alt values on Enter."""
    for asset in assets:
        print(f"\n{asset.label} ({asset.kind})", file=output)
        print(f"Image file: {asset.path}", file=output)
        print(f"Caption: {asset.caption or '(none; press Enter at the caption step to copy blank text)'}", file=output)
        print(f"Alt text: {asset.alt_text or '(none; press Enter at the alt-text step to copy blank text)'}", file=output)
        if asset.source:
            print(f"Source: {asset.source}", file=output)
        print("In Medium: find the placeholder, insert this image, then paste its caption. Open image settings and paste its alt text.", file=output)
        input_fn("Press Enter when ready to copy the caption: ")
        copy_text(asset.caption or "")
        print("Caption copied. Paste it in Medium, then press Enter to copy alt text.", file=output)
        input_fn("Press Enter when ready to copy alt text: ")
        copy_text(asset.alt_text or "")
        print("Alt text copied. Paste it in Medium image settings, then press Enter for the next asset.", file=output)
        input_fn("Press Enter to continue: ")


def copy_plain_text_windows(text: str) -> None:
    """Copy plain text only, used for the assistant's caption and alt steps."""
    if sys.platform != "win32":
        raise RuntimeError("Clipboard copying is supported on Windows for this workflow.")
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _configure_win32_clipboard_apis(user32, kernel32)
    if not user32.OpenClipboard(None):
        raise OSError("Could not open the Windows clipboard.")
    handle = None
    try:
        user32.EmptyClipboard()
        data = (text + "\x00").encode("utf-16-le")
        handle = kernel32.GlobalAlloc(0x0002, len(data))
        if not handle:
            raise OSError("Could not allocate Windows clipboard memory.")
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            raise OSError("Could not lock Windows clipboard memory.")
        try:
            ctypes.memmove(pointer, data, len(data))
        finally:
            kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(13, handle):
            raise OSError("Could not set Windows plain text clipboard data.")
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def _configure_win32_clipboard_apis(user32, kernel32) -> None:
    """Declare pointer-sized Win32 signatures so handles remain safe on 64-bit Windows."""
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_int
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = ctypes.c_int
    user32.RegisterClipboardFormatW.argtypes = [ctypes.c_wchar_p]
    user32.RegisterClipboardFormatW.restype = ctypes.c_uint
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = ctypes.c_int
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_int
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.restype = ctypes.c_void_p
