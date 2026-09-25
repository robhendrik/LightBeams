"""Data structures shared by the Medium article validator."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    """Severity of a validation finding."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


@dataclass(frozen=True)
class Finding:
    """A single validation result attached to a source line."""

    severity: Severity
    message: str
    line: int


@dataclass
class ValidationResult:
    """Findings and parsed values produced while validating an article."""

    source: Path
    findings: list[Finding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    title: str | None = None
    subtitle: str | None = None

    @property
    def has_errors(self) -> bool:
        """Whether any finding should block normal execution."""
        return any(f.severity in (Severity.ERROR, Severity.FATAL) for f in self.findings)

    @property
    def has_fatal(self) -> bool:
        """Whether the article cannot be interpreted safely."""
        return any(f.severity is Severity.FATAL for f in self.findings)


@dataclass(frozen=True)
class Link:
    """A Markdown hyperlink retained as display text and destination."""

    text: str
    target: str


@dataclass
class Paragraph:
    """A prose block with links retained separately from its Markdown text."""

    text: str
    links: list[Link] = field(default_factory=list)


@dataclass
class SectionHeading:
    """An authored level-two section heading."""

    text: str


@dataclass
class Figure:
    """An article image and its associated figure metadata."""

    alt: str
    source_path: Path
    caption: str | None = None
    alt_text: str | None = None
    source_attribution: str | None = None


@dataclass
class DisplayEquation:
    """A LaTeX display equation and its generated raster asset."""

    latex: str
    rendered_path: Path


@dataclass
class PullQuote:
    """A standalone authored blockquote."""

    text: str


@dataclass
class Footnote:
    """A footnote prepared for an end-of-article notes section."""

    identifier: str
    text: str
    marker: str


@dataclass
class Article:
    """Medium-independent prepared article and generated build assets."""

    source_path: Path
    title: str
    subtitle: str | None
    metadata: dict[str, Any]
    blocks: list[Paragraph | SectionHeading | Figure | DisplayEquation | PullQuote]
    footnotes: list[Footnote]
    build_dir: Path
    feature_image: Path | None = None
