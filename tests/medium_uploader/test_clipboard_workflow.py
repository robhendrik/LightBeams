import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from medium_uploader.clipboard_workflow import (
    build_asset_sequence,
    build_clipboard_payload,
    run_asset_assistant,
)
from medium_uploader.models import Article, DisplayEquation, Figure, Footnote, Paragraph, PullQuote, SectionHeading


def sample_article(tmp_path):
    source = tmp_path / "authoritative.md"
    source.write_bytes(b"# unchanged\n")
    return Article(
        source_path=source,
        title="A **Rich** Title",
        subtitle="A *subtitle*",
        metadata={},
        blocks=[
            Paragraph('A [linked phrase](https://example.com) with **bold** and *italic*.'),
            Figure("desc", tmp_path / "figure.png", "Figure caption", "Figure alt", "Author"),
            PullQuote("A **quoted** phrase."),
            DisplayEquation("x^2", tmp_path / "equation_001.png"),
            SectionHeading("A Section"),
        ],
        footnotes=[Footnote("1", "Note text", "¹")],
        build_dir=tmp_path / ".medium_build" / "article",
    )


def test_placeholders_appear_in_html_and_plain_text(tmp_path):
    payload = build_clipboard_payload(sample_article(tmp_path))
    assert "[[FIGURE_01]]" in payload.html
    assert "[[EQUATION_01]]" in payload.html
    assert "[[FIGURE_01]]" in payload.plain_text
    assert "[[EQUATION_01]]" in payload.plain_text


def test_html_preserves_headings_emphasis_quotes_and_links(tmp_path):
    payload = build_clipboard_payload(sample_article(tmp_path))
    assert "<h1>A <strong>Rich</strong> Title</h1>" in payload.html
    assert "<h3>A <em>subtitle</em></h3>" in payload.html
    assert '<a href="https://example.com">linked phrase</a>' in payload.html
    assert "<strong>bold</strong>" in payload.html
    assert "<em>italic</em>" in payload.html
    assert "<blockquote>" in payload.html and "<strong>quoted</strong>" in payload.html
    assert "<h2>A Section</h2>" in payload.html
    assert "https://example.com" in payload.plain_text
    assert "Note text" in payload.html
    assert payload.html.index("[[FIGURE_01]]") < payload.html.index("quoted") < payload.html.index("[[EQUATION_01]]")


def test_clipboard_payload_contains_cf_html_byte_offsets(tmp_path):
    payload = build_clipboard_payload(sample_article(tmp_path))
    header = payload.cf_html.split(b"<html>", 1)[0].decode("ascii")
    values = {
        key: int(line.split(":", 1)[1])
        for line in header.splitlines()
        if ":" in line
        for key in (line.split(":", 1)[0],)
        if key in {"StartHTML", "EndHTML", "StartFragment", "EndFragment"}
    }
    assert payload.cf_html[values["StartHTML"]:values["EndHTML"]].startswith(b"<html>")
    fragment = payload.cf_html[values["StartFragment"]:values["EndFragment"]].decode("utf-8")
    assert "[[FIGURE_01]]" in fragment


def test_assets_follow_document_order_and_retain_metadata(tmp_path):
    assets = build_asset_sequence(sample_article(tmp_path))
    assert [asset.label for asset in assets] == ["[[FIGURE_01]]", "[[EQUATION_01]]"]
    assert assets[0].path == str(tmp_path / "figure.png")
    assert assets[0].caption == "Figure caption"
    assert assets[0].alt_text == "Figure alt"
    assert assets[0].source == "Author"
    assert assets[1].path == str(tmp_path / "equation_001.png")


def test_interactive_assistant_copies_caption_then_alt_then_advances(tmp_path):
    asset = build_asset_sequence(sample_article(tmp_path))[0]
    inputs = iter(["", "", ""])
    copied = []
    from io import StringIO

    output = StringIO()
    run_asset_assistant([asset], copy_text=copied.append, input_fn=lambda _prompt: next(inputs), output=output)
    assert copied == ["Figure caption", "Figure alt"]
    report = output.getvalue()
    assert asset.label in report
    assert asset.path in report
    assert "Source: Author" in report
    assert "insert this image" in report


def test_clipboard_rendering_does_not_modify_source(tmp_path):
    article = sample_article(tmp_path)
    before = article.source_path.read_bytes()
    build_clipboard_payload(article)
    assert article.source_path.read_bytes() == before
