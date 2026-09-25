"""Render LaTeX display equations to transparent PNG assets."""

from __future__ import annotations

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

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        figure = plt.figure(figsize=(8, 1.5), dpi=dpi)
        figure.patch.set_alpha(0)
        figure.text(0.5, 0.5, f"${latex.strip()}$", ha="center", va="center", fontsize=18)
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
