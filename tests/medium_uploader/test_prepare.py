import builtins
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from medium_uploader.models import DisplayEquation, Figure, Paragraph, PullQuote, SectionHeading
from medium_uploader.prepare import prepare_article


def write_article(tmp_path: Path, content: str, *, image_paths: tuple[str, ...] = ()) -> Path:
    article_path = tmp_path / "posts" / "sample" / "article.md"
    article_path.parent.mkdir(parents=True, exist_ok=True)
    for relative in image_paths:
        image = article_path.parent / relative
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"image")
    article_path.write_text(content, encoding="utf-8")
    return article_path


def test_source_markdown_remains_byte_for_byte_unchanged(tmp_path):
    source = "# Title\n\n### Subtitle\n\n$$x^2$$\n"
    path = write_article(tmp_path, source)
    before = path.read_bytes()
    prepare_article(path)
    assert path.read_bytes() == before


def test_image_and_feature_paths_resolve_relative_to_article(tmp_path):
    path = write_article(
        tmp_path,
        "# Title\n\n### Subtitle\n\n<!-- medium\nfeature_image: ../feature.png\n-->\n\n![alt](images/figure.png)\n> Caption: Caption.\n> Alt text: Details.\n",
        image_paths=("../feature.png", "images/figure.png"),
    )
    article = prepare_article(path)
    figure = next(block for block in article.blocks if isinstance(block, Figure))
    assert figure.source_path == (path.parent / "images/figure.png").resolve()
    assert article.feature_image == (path.parent / "../feature.png").resolve()


def test_equations_render_to_ordered_files_and_preserve_latex(tmp_path):
    path = write_article(tmp_path, "# Title\n\n### Subtitle\n\n$$x^2$$\n\n$$y^2$$\n")
    article = prepare_article(path)
    equations = [block for block in article.blocks if isinstance(block, DisplayEquation)]
    assert [equation.latex for equation in equations] == ["x^2", "y^2"]
    assert [equation.rendered_path.name for equation in equations] == ["equation_001.png", "equation_002.png"]
    assert all(equation.rendered_path.is_file() for equation in equations)
    assert all(equation.rendered_path.parent == article.build_dir for equation in equations)


def test_figures_keep_metadata_and_are_not_pull_quotes(tmp_path):
    path = write_article(
        tmp_path,
        "# Title\n\n### Subtitle\n\n![Graph](fig.png)\n> Caption: A caption.\n> Alt text: A graph.\n> Source: Author.\n",
        image_paths=("fig.png",),
    )
    article = prepare_article(path)
    figure = next(block for block in article.blocks if isinstance(block, Figure))
    assert figure.caption == "A caption."
    assert figure.alt_text == "A graph."
    assert figure.source_attribution == "Author."
    assert not any(isinstance(block, PullQuote) for block in article.blocks)


def test_standalone_blockquotes_become_pull_quotes(tmp_path):
    article = prepare_article(write_article(tmp_path, "# Title\n\n### Subtitle\n\n> **A memorable statement.**\n"))
    quote = next(block for block in article.blocks if isinstance(block, PullQuote))
    assert quote.text == "**A memorable statement.**"


def test_links_retain_text_and_target(tmp_path):
    article = prepare_article(write_article(tmp_path, "# Title\n\n### Subtitle\n\nSee [the paper](https://example.test/paper).\n"))
    paragraph = next(block for block in article.blocks if isinstance(block, Paragraph))
    assert paragraph.links[0].text == "the paper"
    assert paragraph.links[0].target == "https://example.test/paper"


def test_footnotes_become_superscript_references_and_end_notes(tmp_path):
    article = prepare_article(write_article(tmp_path, "# Title\n\n### Subtitle\n\nA remark[^1].\n\n[^1]: Extra context.\n"))
    paragraph = next(block for block in article.blocks if isinstance(block, Paragraph))
    assert paragraph.text == "A remark¹."
    assert len(article.footnotes) == 1
    assert (article.footnotes[0].marker, article.footnotes[0].text) == ("¹", "Extra context.")


def test_metadata_is_carried_forward(tmp_path):
    article = prepare_article(write_article(
        tmp_path,
        "# Title\n\n### Subtitle\n\n<!-- medium\ntopics:\n  - Science\nseo_title: Search title\nseo_description: Description\npreview_title: Card title\npreview_subtitle: Card subtitle\nfeature_image: feature.png\n-->\n",
        image_paths=("feature.png",),
    ))
    assert article.metadata == {
        "topics": ["Science"], "seo_title": "Search title", "seo_description": "Description",
        "preview_title": "Card title", "preview_subtitle": "Card subtitle", "feature_image": "feature.png",
    }


def test_headings_and_paragraphs_are_model_blocks(tmp_path):
    article = prepare_article(write_article(tmp_path, "# Title\n\n### Subtitle\n\n## Main Section\n\nProse.\n"))
    assert any(isinstance(block, SectionHeading) and block.text == "Main Section" for block in article.blocks)
    assert any(isinstance(block, Paragraph) and block.text == "Prose." for block in article.blocks)


def test_prepare_only_does_not_import_or_invoke_browser_logic(tmp_path, monkeypatch, capsys):
    path = write_article(tmp_path, "# Title\n\n### Subtitle\n\nA paragraph.\n")
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "upload_medium.py"
    spec = importlib.util.spec_from_file_location("upload_medium_for_test", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if "medium_browser" in name or "playwright" in name:
            raise AssertionError(f"Browser logic must not be imported: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    assert module.main([str(path), "--prepare-only"]) == 0
    assert "Build directory:" in capsys.readouterr().out
