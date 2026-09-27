"""Render LaTeX display equations to transparent PNG assets."""

from __future__ import annotations

import re
from pathlib import Path


BASE_FONT_SIZE = 13
DEFAULT_DPI = 300
CANVAS_WIDTH_PX = 1800
HORIZONTAL_MARGIN_PX = 200
VERTICAL_PADDING_PX = 24
USABLE_CANVAS_WIDTH_PX = CANVAS_WIDTH_PX - (2 * HORIZONTAL_MARGIN_PX)


def equation_scale_for_width(measured_width_px: float, usable_width_px: int = USABLE_CANVAS_WIDTH_PX) -> float:
    """Return a no-enlarge scale, shrinking only when the equation exceeds usable canvas width."""
    return min(1.0, usable_width_px / max(1.0, measured_width_px))


def render_equation(
    latex: str,
    output_path: str | Path,
    dpi: int = DEFAULT_DPI,
    canvas_width_px: int = CANVAS_WIDTH_PX,
    horizontal_margin_px: int = HORIZONTAL_MARGIN_PX,
) -> Path:
    """Render one equation centered on a fixed-width transparent canvas.

    Raises:
        RuntimeError: If Matplotlib cannot parse or render the equation.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.font_manager import FontProperties
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
        parser = MathTextParser("agg")
        usable_width_px = canvas_width_px - (2 * horizontal_margin_px)
        if usable_width_px <= 0:
            raise ValueError("horizontal margins must leave a positive usable canvas width")
        baseline_metrics = parser.parse(math_source, dpi=dpi, prop=FontProperties(size=BASE_FONT_SIZE))
        scale = equation_scale_for_width(baseline_metrics.width, usable_width_px)
        fontsize = BASE_FONT_SIZE * scale
        metrics = parser.parse(math_source, dpi=dpi, prop=FontProperties(size=fontsize))
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        height_px = metrics.height + VERTICAL_PADDING_PX
        figure = plt.figure(figsize=(canvas_width_px / dpi, height_px / dpi), dpi=dpi)
        figure.patch.set_alpha(0)
        figure.text(0.5, 0.5, math_source, ha="center", va="center", fontsize=fontsize, parse_math=True)
        figure.savefig(output, dpi=dpi, transparent=True, pad_inches=0)
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
