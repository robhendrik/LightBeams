"""Render LaTeX display equations to transparent PNG assets."""

from __future__ import annotations

import re
from pathlib import Path


BASE_FONT_SIZE = 18
DEFAULT_DPI = 300
MAX_IMAGE_WIDTH_PX = 1800
IMAGE_PADDING_PX = 32


def equation_scale_for_width(measured_width_px: float, max_image_width_px: int = MAX_IMAGE_WIDTH_PX) -> float:
    """Return a no-enlarge scale, shrinking only when the PNG would exceed its width limit."""
    available_width = max(1, max_image_width_px - IMAGE_PADDING_PX)
    return min(1.0, available_width / max(1.0, measured_width_px))


def render_equation(
    latex: str,
    output_path: str | Path,
    dpi: int = DEFAULT_DPI,
    max_width_px: int = MAX_IMAGE_WIDTH_PX,
) -> Path:
    """Render one equation using Matplotlib mathtext without requiring TeX.

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
        scale = equation_scale_for_width(parser.parse(math_source, dpi=dpi, prop=FontProperties(size=BASE_FONT_SIZE)).width, max_width_px)
        fontsize = BASE_FONT_SIZE * scale
        metrics = parser.parse(math_source, dpi=dpi, prop=FontProperties(size=fontsize))
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        width_px = min(max_width_px, metrics.width + IMAGE_PADDING_PX)
        height_px = metrics.height + IMAGE_PADDING_PX
        figure = plt.figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
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
