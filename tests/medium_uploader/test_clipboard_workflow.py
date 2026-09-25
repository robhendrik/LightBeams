import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from medium_uploader.clipboard_workflow import (
    build_asset_sequence,
    build_clipboard_payload,
    copy_upload_assets,
    run_asset_assistant,
)
from medium_uploader.models import Article, DisplayEquation, Figure, Footnote, Paragraph, PullQuote, SectionHeading
from medium_uploader.render_math import equation_scale_for_width, render_equation


def sample_article(tmp_path):
    source = tmp_path / "authoritative.md"
    source.write_bytes(b"# unchanged\n")
    (tmp_path / "figure.png").write_bytes(b"figure")
    (tmp_path / "equation_001.png").write_bytes(b"equation")
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


def test_upload_assets_are_copied_to_article_sibling_and_feature_is_separate(tmp_path):
    article = sample_article(tmp_path)
    feature = tmp_path / "feature.png"
    figure = tmp_path / "figure.png"
    equation = tmp_path / "equation_001.png"
    feature.write_bytes(b"feature source")
    figure.write_bytes(b"figure source")
    equation.write_bytes(b"equation source")
    article.feature_image = feature
    original_bytes = {path: path.read_bytes() for path in (feature, figure, equation)}

    upload = copy_upload_assets(article)

    assert Path(upload.directory) == article.source_path.parent / "medium_upload_assets"
    assert upload.feature_image is not None
    assert upload.feature_image.kind == "Feature image"
    assert upload.feature_image.label == "Feature image"
    assert upload.feature_image.path == "medium_upload_assets/feature_image.png"
    assert [asset.label for asset in upload.article_assets] == ["[[FIGURE_01]]", "[[EQUATION_01]]"]
    assert [asset.path for asset in upload.article_assets] == [
        "medium_upload_assets/figure_01.png", "medium_upload_assets/equation_01.png",
    ]
    assert [
        (Path(upload.directory) / Path(item.path).name).read_bytes()
        for item in [upload.feature_image, *upload.article_assets]
    ] == [b"feature source", b"figure source", b"equation source"]
    assert {path: path.read_bytes() for path in original_bytes} == original_bytes


def test_figure_one_is_first_body_figure_after_separate_feature_image(tmp_path):
    article = sample_article(tmp_path)
    article.blocks.insert(0, DisplayEquation("x", tmp_path / "before.png"))
    article.blocks.insert(1, Figure("alt", tmp_path / "second-figure.png", "Caption", "Alt"))
    # Figure numbering is independent from feature-image presence and equations.
    assets = build_asset_sequence(article)
    assert [asset.label for asset in assets if asset.kind == "Figure"] == ["[[FIGURE_01]]", "[[FIGURE_02]]"]
    assert [asset.label for asset in assets if asset.kind == "Equation"] == ["[[EQUATION_01]]", "[[EQUATION_02]]"]


def test_interactive_assistant_copies_caption_then_alt_then_advances(tmp_path):
    asset = build_asset_sequence(sample_article(tmp_path))[0]
    inputs = iter(["", ""])
    events = []
    from io import StringIO

    output = StringIO()
    def get_input(prompt):
        events.append(("input", prompt))
        return next(inputs)

    run_asset_assistant([asset], copy_text=lambda text: events.append(("copy", text)), input_fn=get_input, output=output)
    assert events == [
        ("copy", "Figure caption Source: Author"),
        ("input", "Press Enter after pasting the caption: "),
        ("copy", "Figure alt"),
        ("input", "Press Enter after pasting the alt text: "),
    ]
    report = output.getvalue()
    assert asset.label in report
    assert asset.path in report
    assert "Source: Author" in report
    assert "Placeholder: [[FIGURE_01]]" in report
    assert "Caption for Figure 1 copied to clipboard." in report
    assert "Alt text for Figure 1 copied to clipboard." in report
    assert "continue" not in report.casefold()


def test_caption_markdown_is_stripped_from_clipboard_text(tmp_path):
    article = sample_article(tmp_path)
    article.blocks[1].caption = "**Figure 1.** *Gaussian beams* `stay` [focused](https://example.com)."
    article.blocks[1].source_attribution = "**Image by author.**"
    asset = copy_upload_assets(article).article_assets[0]
    assert asset.caption == "Figure 1. Gaussian beams stay focused."
    assert asset.source == "Image by author."


def test_equations_and_feature_image_do_not_get_unnecessary_clipboard_steps(tmp_path):
    article = sample_article(tmp_path)
    asset = build_asset_sequence(article)[1]
    inputs = []
    from io import StringIO

    output = StringIO()
    run_asset_assistant([asset], copy_text=lambda value: pytest.fail("equation has no caption/alt action"),
                        input_fn=lambda prompt: inputs.append(prompt), output=output)
    assert inputs == []
    assert "[[EQUATION_01]]" in output.getvalue()
    assert "equation_001.png" in output.getvalue()


def test_feature_image_has_its_own_manual_step_and_no_figure_number(tmp_path):
    article = sample_article(tmp_path)
    feature_path = tmp_path / "feature.png"
    feature_path.write_bytes(b"feature")
    article.feature_image = feature_path
    feature = copy_upload_assets(article).feature_image
    assert feature is not None
    prompts = []
    from io import StringIO

    output = StringIO()
    run_asset_assistant([feature], copy_text=lambda _value: None, input_fn=prompts.append, output=output)
    text = output.getvalue()
    assert "Feature image" in text
    assert "File: medium_upload_assets/feature_image.png" in text
    assert "Figure 1" not in text
    assert len(prompts) == 1


def test_feature_image_caption_and_alt_use_the_same_copy_steps(tmp_path):
    article = sample_article(tmp_path)
    feature_path = tmp_path / "feature.png"
    feature_path.write_bytes(b"feature")
    article.feature_image = feature_path
    article.metadata.update({
        "feature_image_caption": "**Feature caption**",
        "feature_image_alt_text": "*Feature description*",
    })
    feature = copy_upload_assets(article).feature_image
    copied = []
    prompts = []
    from io import StringIO

    run_asset_assistant([feature], copy_text=copied.append, input_fn=prompts.append, output=StringIO())
    assert copied == ["Feature caption", "Feature description"]
    assert len(prompts) == 2


def test_equation_scale_never_enlarges_short_expressions_and_reduces_long_ones():
    assert equation_scale_for_width(100) == 1.0
    assert equation_scale_for_width(2_000) < 1.0
    assert equation_scale_for_width(2_000) == equation_scale_for_width(2_000)


def test_short_equations_keep_the_same_baseline_font_scale(tmp_path):
    from PIL import Image

    left = render_equation("x^2", tmp_path / "x.png")
    right = render_equation("y^2", tmp_path / "y.png")
    with Image.open(left) as left_png, Image.open(right) as right_png:
        assert left_png.getchannel("A").getbbox()[2] - left_png.getchannel("A").getbbox()[0] == (
            right_png.getchannel("A").getbbox()[2] - right_png.getchannel("A").getbbox()[0]
        )


def test_equation_render_scale_keeps_short_equations_at_baseline_and_caps_long_width(tmp_path):
    short = render_equation("x^2", tmp_path / "short.png", max_width_px=500)
    long_latex = "+".join(["x"] * 35)
    long = render_equation(long_latex, tmp_path / "long.png", max_width_px=500)
    from PIL import Image

    with Image.open(short) as short_png, Image.open(long) as long_png:
        assert short_png.width < 500
        assert long_png.width <= 500
        # Baseline font height remains stable for short expressions; only an
        # over-width equation is proportionally reduced.
        assert long_png.height < short_png.height


def test_clipboard_rendering_does_not_modify_source(tmp_path):
    article = sample_article(tmp_path)
    before = article.source_path.read_bytes()
    build_clipboard_payload(article)
    assert article.source_path.read_bytes() == before
