from pathlib import Path

import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from medium_uploader.models import Severity
from medium_uploader.validate import validate_article


def metadata_block(**overrides):
    values = {
        "date": "2026-09-27", "revision": 1,
        "medium": {
            "topics": ["Physics", "Optics"],
            "seo_title": "Why Lasers Keep Their Shape",
            "seo_description": "A" * 145,
            "preview_title": "Why Lasers Keep Their Shape",
            "preview_subtitle": "How laser beams resist diffraction",
            "publication": "",
            "canonical_url": "",
        },
    }
    values.update(overrides)
    import yaml
    return "<!--\nMETADATA\n" + yaml.safe_dump(values, sort_keys=False) + "-->\n"


def article(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "nested" / "article.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def severities(result):
    return [finding.severity for finding in result.findings]


def test_valid_article_and_allowed_display_math(tmp_path):
    path = article(tmp_path, "# Clear Title\n\n### A Subtitle\n\n## Good Section\n\n$$ x $$\n\n$$\nx^2\n$$\n")
    result = validate_article(path)
    assert not result.has_errors
    assert result.title == "Clear Title"
    assert result.subtitle == "A Subtitle"


def test_missing_title_is_fatal(tmp_path):
    result = validate_article(article(tmp_path, "Just prose.\n"))
    assert Severity.FATAL in severities(result)


def test_non_title_case_section_is_warning(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n## the science of beams\n"))
    assert any(f.severity is Severity.WARNING and "Title Case" in f.message for f in result.findings)
    assert not result.has_errors


def test_inline_math_is_error_but_display_math_is_allowed(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\nInline $x+y$.\n\n$$ x+y $$\n\n$$\nz^2\n$$\n"))
    assert sum(f.severity is Severity.ERROR and "Inline LaTeX" in f.message for f in result.findings) == 1


def test_validator_accepts_both_standalone_display_math_forms(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n$$ a+b $$\n\n$$\nc+d\n$$\n"))
    assert not any(f.severity in (Severity.ERROR, Severity.FATAL) for f in result.findings)


def test_figure_contract_and_relative_image_resolution(tmp_path):
    path = article(tmp_path, "# Title\n\n![A figure](art.png)\n> Caption: Figure one.\n> Alt text: A figure.\n")
    result = validate_article(path)
    assert any(f.severity is Severity.ERROR and "does not exist" in f.message for f in result.findings)
    assert any(f.severity is Severity.WARNING and "Source:" in f.message for f in result.findings)
    (path.parent / "art.png").write_bytes(b"test")
    result = validate_article(path)
    assert not any("does not exist" in f.message for f in result.findings)


def test_figure_missing_caption_and_alt_and_wrong_alt_spelling(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n![x](missing.png)\n> Alt-text: x\n"))
    messages = [f.message for f in result.findings]
    assert any("Caption" in m for m in messages)
    assert any("exact spelling" in m for m in messages)


def test_figure_missing_alt_text_entirely(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n![x](missing.png)\n> Caption: A caption.\n"))
    assert any(f.severity is Severity.ERROR and "missing an Alt text" in f.message for f in result.findings)


def test_unterminated_display_math_is_error(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n$$\nx^2\n"))
    assert any(f.severity is Severity.ERROR and "Unterminated display-math" in f.message and f.line == 3 for f in result.findings)


def test_multiline_comment_between_title_and_subtitle_is_skipped(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n<!-- A comment\nthat spans multiple lines\nand ends here -->\n\n### Subtitle\n"))
    assert result.subtitle == "Subtitle"
    assert not any("Expected a level-3 subtitle" in f.message for f in result.findings)


def test_too_many_topics_finding_points_to_topics_key(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n<!-- medium\ntopics:\n  - A\n  - B\n  - C\n  - D\n  - E\n  - F\nseo_title: Later\n-->\n"))
    finding = next(f for f in result.findings if "at most five topics" in f.message)
    assert finding.line == 4


def test_missing_subtitle_is_warning(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n## Section\n"))
    assert any(f.severity is Severity.WARNING and "Expected a level-3 subtitle" in f.message for f in result.findings)


def test_footnote_validation(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\nA[^missing] B[^dup].\n\n[^dup]: First\n[^dup]: Second\n[^unused]: Extra\n"))
    messages = [f.message for f in result.findings]
    assert any("Unresolved footnote" in m for m in messages)
    assert any("Duplicate footnote" in m for m in messages)
    assert any("Unused footnote" in m for m in messages)


def test_metadata_parsing_and_unknown_key_warning(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n<!-- medium\n\ntopics:\n  - Science\nseo_title: Example\nnew_key: ignored\n-->\n"))
    assert result.metadata["topics"] == ["Science"]
    assert result.metadata["seo_title"] == "Example"
    assert any(f.severity is Severity.WARNING and "Unknown metadata" in f.message for f in result.findings)


def test_metadata_yaml_block_parses_bookkeeping_and_all_medium_fields(tmp_path):
    block = metadata_block()
    result = validate_article(article(tmp_path, "# Title\n\n### Subtitle\n\n" + block))
    assert result.metadata["date"] == "2026-09-27"
    assert result.metadata["revision"] == 1
    assert result.metadata["medium"] == {
        "topics": ["Physics", "Optics"],
        "seo_title": "Why Lasers Keep Their Shape",
        "seo_description": "A" * 145,
        "preview_title": "Why Lasers Keep Their Shape",
        "preview_subtitle": "How laser beams resist diffraction",
        "publication": "",
        "canonical_url": "",
    }
    assert not result.has_errors


@pytest.mark.parametrize("topics", [["One"], ["One", "Two", "Three", "Four", "Five"]])
def test_metadata_accepts_one_to_five_topics(tmp_path, topics):
    result = validate_article(article(tmp_path, "# Title\n\n" + metadata_block(medium={**metadata_block_dict(), "topics": topics})))
    assert not any("topics" in finding.message for finding in result.findings if finding.severity is Severity.ERROR)


def metadata_block_dict():
    return {
        "seo_title": "A title", "seo_description": "A" * 145,
        "preview_title": "Preview", "preview_subtitle": "Subtitle",
        "publication": "", "canonical_url": "",
    }


def test_metadata_rejects_more_than_five_topics_and_missing_required_field(tmp_path):
    too_many = validate_article(article(tmp_path, "# Title\n\n" + metadata_block(medium={**metadata_block_dict(), "topics": ["A", "B", "C", "D", "E", "F"]})))
    assert any(f.severity is Severity.ERROR and "1-5" in f.message for f in too_many.findings)
    missing = validate_article(article(tmp_path, "# Title\n\n" + metadata_block(medium={"topics": ["Physics"]})))
    assert any(f.severity is Severity.ERROR and "seo_title" in f.message for f in missing.findings)


@pytest.mark.parametrize("field,value", [("date", "27-09-2026"), ("date", "2026-02-30"), ("revision", 0), ("revision", -1), ("revision", "one")])
def test_metadata_rejects_invalid_date_and_revision(tmp_path, field, value):
    values = {"date": "2026-09-27", "revision": 1, "medium": metadata_block_dict() | {"topics": ["Physics"]}}
    values[field] = value
    result = validate_article(article(tmp_path, "# Title\n\n" + metadata_block(**values)))
    expected = "date" if field == "date" else "revision"
    assert any(f.severity is Severity.ERROR and expected in f.message for f in result.findings)


def test_metadata_empty_optional_fields_are_valid(tmp_path):
    result = validate_article(article(tmp_path, "# Title\n\n" + metadata_block()))
    assert not result.has_errors
    assert result.metadata["medium"]["publication"] == ""
    assert result.metadata["medium"]["canonical_url"] == ""


def test_metadata_length_recommendations_warn_without_failing(tmp_path):
    medium = metadata_block_dict() | {
        "topics": ["Physics"], "seo_title": "T" * 61, "seo_description": "Short",
    }
    result = validate_article(article(tmp_path, "# Title\n\n" + metadata_block(medium=medium)))
    messages = [f.message for f in result.findings if f.severity is Severity.WARNING]
    assert any("seo_title" in message for message in messages)
    assert any("seo_description" in message for message in messages)
    assert not result.has_errors


def test_duplicate_title_and_heading_line_numbers(tmp_path):
    result = validate_article(article(tmp_path, "# First\n\n# Second\n\n## poor heading\n"))
    assert any(f.severity is Severity.ERROR and f.line == 3 for f in result.findings)
    assert any(f.severity is Severity.WARNING and f.line == 5 for f in result.findings)
