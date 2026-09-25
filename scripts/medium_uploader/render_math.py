"""Render LaTeX display equations to transparent PNG assets."""

from __future__ import annotations

import re
from pathlib import Path


def render_equation(latex: str, output_path: str | Path, dpi: int = 300) -> Path:
    """Render one equation using Matplotlib mathtext without requiring TeX.

    Raises:
        RuntimeError: If Matplotlib cannot parse or render the equation.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.mathtext import MathTextParser

        expression = re.sub(r"\s+", " ", latex).strip()
        if expression.startswith("$") or expression.endswith("$"):
            raise ValueError("equation body must not include outer dollar delimiters")
        # MathText implements the commands in this article except \tfrac and
        # general \text. These equivalent forms keep the expression math,
        # rather than letting Matplotlib fall back to drawing raw source text.
        expression = expression.replace(r"\tfrac", r"\frac")
        expression = re.sub(r"\\text\{([^{}]*)\}", r"\\mathrm{\1}", expression)
        math_source = f"${expression}$"
        # Text artists silently fall back to ordinary text if parsing fails.
        # Parse explicitly first so unsupported syntax is always an error.
        MathTextParser("agg").parse(math_source, dpi=dpi)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        figure = plt.figure(figsize=(8, 1.5), dpi=dpi)
        figure.patch.set_alpha(0)
        figure.text(0.5, 0.5, math_source, ha="center", va="center", fontsize=18, parse_math=True)
        figure.savefig(output, dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0.12)
        plt.close(figure)
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("Matplotlib produced an empty equation image")
        return output
    except Exception as exc:
        try:
            plt.close("all")  # type: ignore[possibly-undefined]
        except Exception:
            pass
        raise RuntimeError(f"Could not render display equation with Matplotlib mathtext: {exc}") from exc
