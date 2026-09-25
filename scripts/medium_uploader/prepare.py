"""Parse validated article Markdown into a Medium-independent model."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import (
    Article,
    DisplayEquation,
    Figure,
    Footnote,
    Link,
    Paragraph,
    PullQuote,
    SectionHeading,
    ValidationResult,
)
from .render_math import render_equation
from .validate import validate_article

_LINK = re.compile(r"(?<!!)\[([^]]+)\]\(([^)]+)\)")
_IMAGE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
_FOOTNOTE_DEF = re.compile(r"^\[\^([\w-]+)\]:\s*(.*)$")
_FOOTNOTE_REF = re.compile(r"\[\^([\w-]+)\]")
_SUPERSCRIPT = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")


class PreparationError(RuntimeError):
    """Raised when an article cannot be safely prepared."""


def _article_id(path: Path) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-").lower() or "article"
    identity = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:10]
    return f"{slug}-{identity}"


def _link_records(text: str) -> list[Link]:
    return [Link(match.group(1), match.group(2)) for match in _LINK.finditer(text)]


def _clean_metadata(value: str) -> str:
    return value.strip()


def prepare_article(article_path: str | Path, validation: ValidationResult | None = None) -> Article:
    """Prepare a validated Markdown article and generated equation assets.

    All source-relative paths are resolved from the supplied Markdown file.
    The source file is only read; generated equation images live in a sibling
    ``.medium_build`` directory.
    """
    source = Path(article_path).expanduser().resolve()
    validation = validation or validate_article(source)
    if validation.has_errors:
        raise PreparationError("Article has validation errors; preparation was stopped.")
    lines = source.read_text(encoding="utf-8").splitlines()
    metadata = dict(validation.metadata)
    feature_image = metadata.get("feature_image")
    resolved_feature_image = (source.parent / str(feature_image)).resolve() if feature_image else None
    build_dir = source.parent / ".medium_build" / _article_id(source)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Read notes first so references can be replaced consistently in prose.
    notes: dict[str, str] = {}
    body_lines: list[tuple[int, str]] = []
    in_metadata = False
    for number, line in enumerate(lines, start=1):
        if line.strip() == "<!-- medium":
            in_metadata = True
            continue
        if in_metadata:
            if line.strip() == "-->":
                in_metadata = False
            continue
        definition = _FOOTNOTE_DEF.match(line)
        if definition:
            identifier, note_text = definition.groups()
            notes[identifier] = note_text
            continue
        body_lines.append((number, line))

    footnotes = [
        Footnote(identifier=identifier, text=text, marker=identifier.translate(_SUPERSCRIPT))
        for identifier, text in notes.items()
    ]
    blocks: list[Paragraph | SectionHeading | Figure | DisplayEquation | PullQuote] = []
    paragraphs: list[str] = []
    equation_index = 0
    pos = 0
    title_index = next((i for i, line in enumerate(lines) if re.match(r"^#\s+", line)), None)
    subtitle_index: int | None = None
    if title_index is not None and validation.subtitle:
        candidate = title_index + 1
        in_comment = False
        in_medium_metadata = False
        while candidate < len(lines):
            current = lines[candidate]
            if current.strip() == "<!-- medium":
                in_medium_metadata = True
                candidate += 1
                continue
            if in_medium_metadata:
                if current.strip() == "-->":
                    in_medium_metadata = False
                candidate += 1
                continue
            if not current.strip():
                candidate += 1
                continue
            if in_comment:
                if "-->" in current:
                    in_comment = False
                candidate += 1
                continue
            if "<!--" in current:
                if "-->" not in current.split("<!--", 1)[1]:
                    in_comment = True
                candidate += 1
                continue
            if re.match(r"^###\s+", current) and current.strip().removeprefix("### ").strip() == validation.subtitle:
                subtitle_index = candidate
            break

    def flush_paragraph() -> None:
        if paragraphs:
            text = "\n".join(paragraphs).strip()
            if text:
                text = _FOOTNOTE_REF.sub(lambda match: match.group(1).translate(_SUPERSCRIPT), text)
                blocks.append(Paragraph(text=text, links=_link_records(text)))
            paragraphs.clear()

    while pos < len(body_lines):
        line_no, line = body_lines[pos]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            pos += 1
            continue
        if stripped.startswith("<!--"):
            flush_paragraph()
            if "-->" not in stripped:
                pos += 1
                while pos < len(body_lines) and "-->" not in body_lines[pos][1]:
                    pos += 1
                pos += 1
            else:
                pos += 1
            continue
        if stripped.startswith("$$"):
            flush_paragraph()
            math_parts = [stripped[2:]]
            closed = "$$" in math_parts[0]
            if closed:
                math_parts[0] = math_parts[0].split("$$", 1)[0]
            pos += 1
            while not closed and pos < len(body_lines):
                math_line = body_lines[pos][1]
                if "$$" in math_line:
                    math_parts.append(math_line.split("$$", 1)[0])
                    closed = True
                    pos += 1
                    break
                math_parts.append(math_line)
                pos += 1
            if not closed:
                raise PreparationError(f"Unterminated display equation beginning on line {line_no}.")
            latex = "\n".join(math_parts).strip()
            equation_index += 1
            output = build_dir / f"equation_{equation_index:03d}.png"
            try:
                render_equation(latex, output)
            except RuntimeError as exc:
                raise PreparationError(f"Equation on line {line_no} could not be rendered: {exc}") from exc
            blocks.append(DisplayEquation(latex=latex, rendered_path=output))
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", stripped)
        if heading:
            flush_paragraph()
            level, text = len(heading.group(1)), heading.group(2)
            # The title/subtitle are article fields, not body blocks.
            if level == 1 or body_lines[pos][0] - 1 == subtitle_index:
                pos += 1
                continue
            if level == 2:
                blocks.append(SectionHeading(text=text))
            else:
                paragraphs.append(stripped)
            pos += 1
            continue
        image = _IMAGE.fullmatch(stripped)
        if image:
            flush_paragraph()
            alt, raw_path = image.groups()
            resolved = (source.parent / raw_path.split()[0]).resolve()
            figure_lines: list[str] = []
            cursor = pos + 1
            while cursor < len(body_lines) and body_lines[cursor][1].lstrip().startswith(">"):
                figure_lines.append(body_lines[cursor][1].lstrip()[1:].strip())
                cursor += 1
            caption = next((value.split(":", 1)[1].strip() for value in figure_lines if value.lower().startswith("caption:")), None)
            alt_text = next((value.split(":", 1)[1].strip() for value in figure_lines if value.startswith("Alt text:")), None)
            attribution = next((value.split(":", 1)[1].strip() for value in figure_lines if value.lower().startswith("source:")), None)
            blocks.append(Figure(alt=alt, source_path=resolved, caption=caption, alt_text=alt_text, source_attribution=attribution))
            pos = cursor
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote_lines: list[str] = []
            while pos < len(body_lines) and body_lines[pos][1].lstrip().startswith(">"):
                quote_lines.append(body_lines[pos][1].lstrip()[1:].strip())
                pos += 1
            if any(re.match(r"(?:Caption|Alt text|Alt-text|Source):", value, re.I) for value in quote_lines):
                # Figure metadata is only an orphan here; never promote it to a quote.
                continue
            quote_text = _FOOTNOTE_REF.sub(lambda match: match.group(1).translate(_SUPERSCRIPT), "\n".join(quote_lines))
            blocks.append(PullQuote(text=quote_text))
            continue
        paragraphs.append(line)
        pos += 1
    flush_paragraph()

    # Validate references against definitions and keep only definitions that are referenced.
    referenced_ids = {
        identifier
        for _, line in body_lines
        for identifier in _FOOTNOTE_REF.findall(line)
    }
    prepared_notes = [note for note in footnotes if note.identifier in referenced_ids]
    return Article(
        source_path=source,
        title=validation.title or "",
        subtitle=validation.subtitle,
        metadata={key: _clean_metadata(value) if isinstance(value, str) else value for key, value in metadata.items()},
        blocks=blocks,
        footnotes=prepared_notes,
        build_dir=build_dir,
        feature_image=resolved_feature_image,
    )
