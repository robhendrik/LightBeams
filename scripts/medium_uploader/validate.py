"""Validation of authoritative Medium-ready Markdown articles."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import yaml

from .models import Finding, Severity, ValidationResult

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_IMAGE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
_FOOTNOTE_REF = re.compile(r"\[\^([\w-]+)\]")
_FOOTNOTE_DEF = re.compile(r"^\s*\[\^([\w-]+)\]:")
_SINGLE_LINE_DISPLAY = re.compile(r"^\s*\$\$(.*?)\$\$\s*$")
_KNOWN_METADATA = {
    "topics", "seo_title", "seo_description", "preview_title",
    "preview_subtitle", "feature_image",
}

# Keep Medium's current recommendations together for straightforward updates.
SEO_TITLE_MAX_LENGTH = 60
SEO_DESCRIPTION_MIN_LENGTH = 140
SEO_DESCRIPTION_MAX_LENGTH = 156
MAX_MEDIUM_TOPICS = 5
_REQUIRED_BOOKKEEPING_FIELDS = ("date", "revision")
_REQUIRED_MEDIUM_FIELDS = (
    "topics", "seo_title", "seo_description", "preview_title", "preview_subtitle",
)
_OPTIONAL_MEDIUM_FIELDS = ("publication", "canonical_url")


def _finding(result: ValidationResult, severity: Severity, message: str, line: int) -> None:
    result.findings.append(Finding(severity, message, line))


def _metadata(lines: list[str], result: ValidationResult) -> tuple[set[int], set[int]]:
    """Parse the METADATA YAML comment and the legacy Medium metadata comment."""
    covered: set[int] = set()
    topic_lines: set[int] = set()
    metadata_starts = [i for i, line in enumerate(lines) if line.strip() == "METADATA" and i > 0 and lines[i - 1].strip() == "<!--"]
    if len(metadata_starts) > 1:
        _finding(result, Severity.FATAL, "Only one METADATA block is allowed.", metadata_starts[1] + 1)
    if metadata_starts:
        marker = metadata_starts[0]
        start = marker - 1
        end = next((i for i in range(marker + 1, len(lines)) if lines[i].strip() == "-->"), None)
        if end is None:
            _finding(result, Severity.FATAL, "Unterminated METADATA block.", start + 1)
            covered.update(range(start, len(lines)))
        else:
            covered.update(range(start, end + 1))
            try:
                parsed = yaml.safe_load("\n".join(lines[marker + 1:end]))
            except yaml.YAMLError as exc:
                parsed = None
                _finding(result, Severity.ERROR, f"Malformed METADATA YAML: {exc}", marker + 1)
            if not isinstance(parsed, dict):
                _finding(result, Severity.ERROR, "METADATA content must be a YAML mapping.", marker + 1)
                parsed = {}
            result.metadata.update(parsed)
            medium = parsed.get("medium")
            if not isinstance(medium, dict):
                _finding(result, Severity.ERROR, "Required metadata field 'medium' must be a mapping.", marker + 1)
                medium = {}
                result.metadata["medium"] = medium
            date_value = parsed.get("date")
            if isinstance(date_value, date):
                result.metadata["date"] = date_value.isoformat()
                date_value = date_value.isoformat()
            if not isinstance(date_value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value):
                _finding(result, Severity.ERROR, "Metadata 'date' must use ISO YYYY-MM-DD format.", marker + 1)
            else:
                try:
                    date.fromisoformat(date_value)
                except ValueError:
                    _finding(result, Severity.ERROR, "Metadata 'date' must be a valid ISO calendar date.", marker + 1)
            revision = parsed.get("revision")
            if isinstance(revision, bool) or not isinstance(revision, int) or revision <= 0:
                _finding(result, Severity.ERROR, "Metadata 'revision' must be a positive integer.", marker + 1)
            for key in _REQUIRED_BOOKKEEPING_FIELDS:
                if key not in parsed:
                    _finding(result, Severity.ERROR, f"Missing required metadata field '{key}'.", marker + 1)
            for key in _REQUIRED_MEDIUM_FIELDS:
                if key not in medium:
                    _finding(result, Severity.ERROR, f"Missing required Medium metadata field '{key}'.", marker + 1)
            for key in _OPTIONAL_MEDIUM_FIELDS:
                if key not in medium:
                    medium[key] = ""
                elif not isinstance(medium[key], str):
                    _finding(result, Severity.ERROR, f"Medium '{key}' must be a string (or empty).", marker + 1)
            topics = medium.get("topics")
            if not isinstance(topics, list) or not 1 <= len(topics) <= MAX_MEDIUM_TOPICS:
                _finding(result, Severity.ERROR, "Medium 'topics' must contain 1-5 non-empty strings.", marker + 1)
            elif any(not isinstance(topic, str) or not topic.strip() for topic in topics):
                _finding(result, Severity.ERROR, "Medium 'topics' must contain only non-empty strings.", marker + 1)
            else:
                topic_lines.update(range(marker + 1, end))
            for key in ("seo_title", "seo_description", "preview_title", "preview_subtitle"):
                value = medium.get(key)
                if not isinstance(value, str) or not value.strip():
                    _finding(result, Severity.ERROR, f"Medium '{key}' must be a non-empty string.", marker + 1)
            seo_title = medium.get("seo_title")
            if isinstance(seo_title, str) and len(seo_title) > SEO_TITLE_MAX_LENGTH:
                _finding(result, Severity.WARNING, f"Medium seo_title is over {SEO_TITLE_MAX_LENGTH} characters.", marker + 1)
            description = medium.get("seo_description")
            if isinstance(description, str) and not SEO_DESCRIPTION_MIN_LENGTH <= len(description) <= SEO_DESCRIPTION_MAX_LENGTH:
                _finding(result, Severity.WARNING, f"Medium seo_description should be {SEO_DESCRIPTION_MIN_LENGTH}-{SEO_DESCRIPTION_MAX_LENGTH} characters.", marker + 1)

    starts = [i for i, line in enumerate(lines) if line.strip() == "<!-- medium"]
    if not starts:
        return covered, topic_lines
    if len(starts) > 1:
        _finding(result, Severity.FATAL, "Only one Medium metadata block is allowed.", starts[1] + 1)
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "-->"), None)
    if end is None:
        _finding(result, Severity.FATAL, "Unterminated Medium metadata block.", start + 1)
        return set(range(start, len(lines))), set()
    covered.update(range(start, end + 1))
    topic_lines: set[int] = set()
    topics_line: int | None = None
    key_line: int | None = None
    current_key: str | None = None
    seen: set[str] = set()
    malformed = False
    for i in range(start + 1, end):
        raw = lines[i]
        if not raw.strip():
            continue
        if raw.startswith("  - "):
            if current_key != "topics":
                malformed = True
                _finding(result, Severity.ERROR, "List item is not attached to the topics key.", i + 1)
                continue
            result.metadata.setdefault("topics", []).append(raw[4:].strip().strip("\"'"))
            topic_lines.add(i)
            continue
        match = re.fullmatch(r"([A-Za-z_][\w-]*):(?:\s*(.*))?", raw)
        if not match:
            malformed = True
            _finding(result, Severity.ERROR, "Malformed metadata entry.", i + 1)
            continue
        key, value = match.group(1), (match.group(2) or "").strip()
        current_key, key_line = key, i + 1
        if key in seen:
            malformed = True
            _finding(result, Severity.ERROR, f"Duplicate metadata key '{key}'.", i + 1)
            continue
        seen.add(key)
        if key not in _KNOWN_METADATA:
            _finding(result, Severity.WARNING, f"Unknown metadata key '{key}' will be ignored.", i + 1)
        if key == "topics":
            topics_line = i + 1
            result.metadata["topics"] = []
            if value:
                malformed = True
                _finding(result, Severity.ERROR, "The topics value must be a YAML-style list.", i + 1)
        elif value:
            result.metadata[key] = value.strip("\"'")
        else:
            malformed = True
            _finding(result, Severity.ERROR, f"Metadata key '{key}' requires a value.", i + 1)
    if malformed and not any(f.severity is Severity.ERROR and start < f.line - 1 < end for f in result.findings):
        _finding(result, Severity.ERROR, "Malformed metadata block.", start + 1)
    topics = result.metadata.get("topics", [])
    if len(topics) > 5:
        _finding(result, Severity.ERROR, "Medium supports at most five topics; choose which to remove.", topics_line or start + 1)
    return covered, topic_lines


def _likely_title_case_violation(text: str) -> bool:
    words = re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", text)
    if len(words) < 2:
        return False
    small = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "vs", "via"}
    return any(word.islower() and word.lower() not in small for word in words)


def validate_article(article_path: str | Path) -> ValidationResult:
    """Validate an article, resolving every referenced asset from its own directory."""
    source = Path(article_path).expanduser().resolve()
    result = ValidationResult(source=source)
    try:
        content = source.read_text(encoding="utf-8")
    except OSError as exc:
        _finding(result, Severity.FATAL, f"Cannot read article: {exc}", 1)
        return result
    lines = content.splitlines()
    metadata_lines, _ = _metadata(lines, result)
    feature_image = result.metadata.get("feature_image")
    if feature_image:
        feature_path = (source.parent / str(feature_image)).resolve()
        if not feature_path.is_file():
            line = next((i + 1 for i, value in enumerate(lines) if re.match(r"^feature_image:\s*", value)), 1)
            _finding(result, Severity.ERROR, f"Feature image does not exist: {feature_image}.", line)
    title_lines: list[tuple[int, str]] = []
    headings: list[tuple[int, int, str]] = []
    in_display_math = False
    display_math_start: int | None = None
    definition_ids: dict[str, list[int]] = {}
    references: list[tuple[str, int]] = []

    in_html_comment = False
    for idx, line in enumerate(lines):
        line_no = idx + 1
        if idx in metadata_lines:
            continue
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
            continue
        if "<!--" in line:
            if "-->" not in line.split("<!--", 1)[1]:
                in_html_comment = True
            continue
        single_line_display = _SINGLE_LINE_DISPLAY.fullmatch(line)
        if in_display_math:
            if line.strip() == "$$":
                in_display_math = False
                display_math_start = None
            elif "$$" in line:
                _finding(result, Severity.ERROR, "A multiline display equation must close on its own '$$' line.", line_no)
                in_display_math = False
                display_math_start = None
        elif single_line_display:
            if not single_line_display.group(1).strip():
                _finding(result, Severity.ERROR, "A single-line display equation cannot be empty.", line_no)
        elif line.strip() == "$$":
            in_display_math = True
            display_math_start = line_no
        elif "$$" in line:
            _finding(result, Severity.ERROR, "Display math must use a standalone '$$ ... $$' line or a multiline block.", line_no)
        if not in_display_math and not single_line_display:
            check = line
            check = re.sub(r"`[^`]*`", "", check)
            if re.search(r"(?<!\$)\$(?!\$)[^\n$]+(?<!\$)\$(?!\$)", check):
                _finding(result, Severity.ERROR, "Inline LaTeX math ($...$) is not supported.", line_no)
        heading = _HEADING.match(line)
        if heading:
            level, text = len(heading.group(1)), heading.group(2)
            headings.append((idx, level, text))
            if level == 1:
                title_lines.append((idx, text))
            elif level == 2 and _likely_title_case_violation(text):
                _finding(result, Severity.WARNING, f"Section heading may not be Title Case: '{text}'.", line_no)
        definition = _FOOTNOTE_DEF.match(line)
        if definition:
            definition_ids.setdefault(definition.group(1), []).append(line_no)
            continue
        references.extend((m.group(1), line_no) for m in _FOOTNOTE_REF.finditer(line))
        for image in _IMAGE.finditer(line):
            alt, raw_path = image.groups()
            image_path = (source.parent / raw_path.split()[0]).resolve()
            if not image_path.is_file():
                _finding(result, Severity.ERROR, f"Referenced image does not exist: {raw_path}.", line_no)
            blocks: list[tuple[str, int]] = []
            j = idx + 1
            while j < len(lines) and lines[j].lstrip().startswith(">"):
                blocks.append((lines[j].lstrip()[1:].strip(), j + 1))
                j += 1
            if not any(re.match(r"Caption:\s*\S", text, re.I) for text, _ in blocks):
                _finding(result, Severity.ERROR, "Figure is missing a Caption: field.", line_no)
            wrong = next(((text, n) for text, n in blocks if re.match(r"Alt-text:", text, re.I)), None)
            if wrong:
                _finding(result, Severity.ERROR, "Use the exact spelling 'Alt text:' (not 'Alt-text:').", wrong[1])
            if not any(re.match(r"Alt text:\s*\S", text) for text, _ in blocks):
                if not wrong:
                    _finding(result, Severity.ERROR, "Figure is missing an Alt text: field.", line_no)
            if not any(re.match(r"Source:\s*\S", text, re.I) for text, _ in blocks):
                _finding(result, Severity.WARNING, "Figure is missing a Source: field.", line_no)
    if in_display_math:
        _finding(result, Severity.ERROR, "Unterminated display-math block opened with '$$'.", display_math_start or len(lines))
    if len(title_lines) == 0:
        _finding(result, Severity.FATAL, "Article must contain exactly one level-1 title; none found.", 1)
    elif len(title_lines) > 1:
        _finding(result, Severity.ERROR, "Article must contain exactly one level-1 title.", title_lines[1][0] + 1)
        result.title = title_lines[0][1]
    else:
        result.title = title_lines[0][1]
        pos = title_lines[0][0] + 1
        while pos < len(lines):
            if pos in metadata_lines or not lines[pos].strip():
                pos += 1
                continue
            remainder = lines[pos]
            while "<!--" in remainder:
                before, comment_tail = remainder.split("<!--", 1)
                if "-->" in comment_tail:
                    _, remainder = comment_tail.split("-->", 1)
                    remainder = before + remainder
                else:
                    pos += 1
                    while pos < len(lines) and "-->" not in lines[pos]:
                        pos += 1
                    if pos >= len(lines):
                        remainder = ""
                        break
                    _, remainder = lines[pos].split("-->", 1)
                    remainder = before + remainder
            if not remainder.strip():
                pos += 1
                continue
            candidate = _HEADING.match(remainder.strip())
            if candidate and len(candidate.group(1)) == 3:
                result.subtitle = candidate.group(2)
            break
        if result.subtitle is None:
            _finding(result, Severity.WARNING, "Expected a level-3 subtitle immediately after the title, but none was found.", title_lines[0][0] + 1)
    for footnote_id, ref_line in references:
        if footnote_id not in definition_ids:
            _finding(result, Severity.ERROR, f"Unresolved footnote reference '[^{footnote_id}]'.", ref_line)
    for identifier, def_lines in definition_ids.items():
        if len(def_lines) > 1:
            _finding(result, Severity.ERROR, f"Duplicate footnote definition '[^{identifier}]'.", def_lines[1])
        elif not any(ref == identifier for ref, _ in references):
            _finding(result, Severity.WARNING, f"Unused footnote definition '[^{identifier}]'.", def_lines[0])
    return result


def format_report(result: ValidationResult) -> str:
    """Return a concise, readable line-numbered validation report."""
    lines = [f"Validation: {result.source}"]
    if result.findings:
        lines.extend(f"{finding.severity.value} line {finding.line}: {finding.message}" for finding in result.findings)
    else:
        lines.append("INFO: No validation issues found.")
    return "\n".join(lines)
