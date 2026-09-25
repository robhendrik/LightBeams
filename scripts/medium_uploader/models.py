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
