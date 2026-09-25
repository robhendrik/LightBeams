"""Rich clipboard rendering and the manual asset insertion assistant."""

from __future__ import annotations

import ctypes
import html
import re
import shutil
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


@dataclass(frozen=True)
class UploadAssets:
    directory: str
    feature_image: ClipboardAsset | None
    article_assets: list[ClipboardAsset]


class _PlainText(HTMLParser):
    """Extract readable clipboard fallback text and retain link destinations."""

    _BLOCKS = {"p", "h1", "h2", "h3", "h4", "blockquote", "li", "div"}

    def __init__(self, *, include_link_targets: bool = True):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[tuple[int, str]] = []
        self.include_link_targets = include_link_targets

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
            if self.include_link_targets and text and text != href:
                self.parts.append(f" ({href})")
        if tag in self._BLOCKS and self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def _plain_text(fragment: str) -> str:
    parser = _PlainText()
    parser.feed(fragment)
    return re.sub(r"\n{3,}", "\n\n", "".join(parser.parts)).strip()


def strip_markdown(text: str | None) -> str | None:
    """Return visible Markdown wording without emphasis, code, or link syntax."""
    if text is None:
        return None
    renderer = mistune.create_markdown(plugins=["table", "strikethrough"])
    parser = _PlainText(include_link_targets=False)
    parser.feed(renderer(text))
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()


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
            ))
    return assets


def copy_upload_assets(article: Article) -> UploadAssets:
    """Copy every upload image beside the source article under portable names."""
    directory = article.source_path.parent / "medium_upload_assets"
    directory.mkdir(parents=True, exist_ok=True)

    feature_asset = None
    if article.feature_image is not None:
        feature_path = directory / "feature_image.png"
        _copy_asset(article.feature_image, feature_path)
        metadata_text = lambda key: strip_markdown(article.metadata.get(key)) if isinstance(article.metadata.get(key), str) else None
        feature_asset = ClipboardAsset(
            label="Feature image",
            kind="Feature image",
            path="medium_upload_assets/feature_image.png",
            caption=metadata_text("feature_image_caption"),
            alt_text=metadata_text("feature_image_alt_text"),
            source=metadata_text("feature_image_source"),
        )

    copied_assets: list[ClipboardAsset] = []
    figure_index = 0
    equation_index = 0
    for block in article.blocks:
        if isinstance(block, Figure):
            figure_index += 1
            filename = f"figure_{figure_index:02d}.png"
            _copy_asset(block.source_path, directory / filename)
            copied_assets.append(ClipboardAsset(
                label=f"[[FIGURE_{figure_index:02d}]]",
                kind="Figure",
                path=f"medium_upload_assets/{filename}",
                caption=strip_markdown(block.caption),
                alt_text=strip_markdown(block.alt_text),
                source=strip_markdown(block.source_attribution),
            ))
        elif isinstance(block, DisplayEquation):
            equation_index += 1
            filename = f"equation_{equation_index:02d}.png"
            _copy_asset(block.rendered_path, directory / filename)
            copied_assets.append(ClipboardAsset(
                label=f"[[EQUATION_{equation_index:02d}]]",
                kind="Equation",
                path=f"medium_upload_assets/{filename}",
            ))
    return UploadAssets(
        directory=str(directory),
        feature_image=feature_asset,
        article_assets=copied_assets,
    )


def _copy_asset(source, destination) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Upload image does not exist: {source}")
    shutil.copy2(source, destination)


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
    """Guide one-Enter transitions, copying figure caption then alt text."""
    for asset in assets:
        figure_number = int(asset.label.removeprefix("[[FIGURE_").removesuffix("]]")) if asset.kind == "Figure" else None
        title = f"Figure {figure_number}" if figure_number is not None else asset.kind
        print(f"\n{title}", file=output)
        if asset.label.startswith("[["):
            print(f"Placeholder: {asset.label}", file=output)
        print(f"File: {asset.path}", file=output)
        if asset.source:
            print(f"Source: {asset.source}", file=output)
        if asset.kind == "Feature image":
            print("In Medium, set this image as the feature image.", file=output)
            if asset.caption or asset.alt_text:
                if asset.caption:
                    copy_text(asset.caption)
                    print("Feature image caption copied to clipboard. Paste it into Medium, then press Enter here.", file=output)
                    input_fn("Press Enter after pasting the caption: ")
                if asset.alt_text:
                    copy_text(asset.alt_text)
                    print("Feature image alt text copied to clipboard. Paste it into Medium, then press Enter here.", file=output)
                    input_fn("Press Enter after pasting the alt text: ")
            else:
                input_fn("Press Enter after setting the feature image to continue: ")
            continue
        if asset.kind == "Equation":
            print("Find this placeholder in Medium and insert the equation image. No caption or alt-text clipboard step is needed.", file=output)
            continue

        if asset.caption:
            caption = asset.caption
            if asset.source:
                caption = f"{caption} Source: {asset.source}"
            copy_text(caption)
            print(f"Caption for Figure {figure_number} copied to clipboard.", file=output)
            print("Paste it into Medium, then press Enter here.", file=output)
            input_fn("Press Enter after pasting the caption: ")
        if asset.alt_text:
            copy_text(asset.alt_text)
            print(f"Alt text for Figure {figure_number} copied to clipboard.", file=output)
            print("Paste it into Medium image settings, then press Enter here.", file=output)
            input_fn("Press Enter after pasting the alt text: ")


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
