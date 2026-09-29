"""
post_2_figures_3_4.py

Generate Figures 3 and 4 for "What Is a Photon, Really?"

Figure 3:
    Quantization replaces the classical amplitude picture with discrete
    energy contours, E_n = (n + 1/2) ħω.

Figure 4:
    The same contours with creation/annihilation operations shown as
    transitions between neighboring energy levels.

The styling intentionally matches post_2_figure_2.py.

Outputs:
    outputs/post_2_figure_3.png
    outputs/post_2_figure_4.png
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUTPUT_3 = OUTPUT_DIR / "post_2_figure_3.png"
OUTPUT_4 = OUTPUT_DIR / "post_2_figure_4.png"

FIGSIZE = (7.2, 7.2)
DPI = 180
LIMIT = 2.35

# Quantized energy contours: r_n ∝ sqrt(n + 1/2)
N_LEVELS = 7
RADIUS_SCALE = 0.72

PLANE_COLOR = "0.96"
AXIS_COLOR = "0.55"
RING_COLOR = "0.18"

# Figure 4: choose one neighboring pair to explain the ladder operation.
TRANSITION_N = 2


# ---------------------------------------------------------------------------
# Shared drawing
# ---------------------------------------------------------------------------

def radius(n):
    """Phase-space radius corresponding to E_n ∝ n + 1/2."""
    return RADIUS_SCALE * np.sqrt(n + 0.5)


def setup_axes():
    """Create the common complex-amplitude plane used in Figures 2–4."""
    fig, ax = plt.subplots(figsize=FIGSIZE)

    ax.set_xlim(-LIMIT, LIMIT)
    ax.set_ylim(-LIMIT, LIMIT)
    ax.set_aspect("equal")
    ax.set_facecolor(PLANE_COLOR)

    ax.axhline(0, linewidth=1.0, color=AXIS_COLOR, zorder=1)
    ax.axvline(0, linewidth=1.0, color=AXIS_COLOR, zorder=1)

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.text(
        LIMIT * 0.96, -0.10,
        r"$\mathrm{Re}(A)$",
        ha="right", va="top",
        fontsize=15,
    )
    ax.text(
        0.10, LIMIT * 0.96,
        r"$\mathrm{Im}(A)$",
        ha="left", va="top",
        fontsize=15,
    )

    return fig, ax


def draw_energy_rings(ax):
    """Draw the discrete quantized energy contours."""
    theta = np.linspace(0, 2 * np.pi, 800)

    for n in range(N_LEVELS):
        r = radius(n)
        ax.plot(
            r * np.cos(theta),
            r * np.sin(theta),
            color=RING_COLOR,
            linewidth=1.8,
            zorder=3,
        )


def save(fig, output):
    """Save and close a figure."""
    fig.tight_layout(pad=0.35)
    fig.savefig(output, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output}")


# ---------------------------------------------------------------------------
# Figure 3
# ---------------------------------------------------------------------------

def make_figure_3():
    """Discrete energy contours after quantization."""
    fig, ax = setup_axes()
    draw_energy_rings(ax)

    # A compact equation is enough; avoid labeling every ring.
    ax.text(
        0.04, 0.96,
        r"$E_n=(n+\frac{1}{2})\hbar\omega$",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=16,
    )

    save(fig, OUTPUT_3)


# ---------------------------------------------------------------------------
# Figure 4
# ---------------------------------------------------------------------------

def radial_arrow(ax, r_start, r_end, angle, label, label_offset=0.0):
    """Draw a radial transition arrow between two neighboring contours."""
    direction = np.array([np.cos(angle), np.sin(angle)])

    p0 = r_start * direction
    p1 = r_end * direction

    arrow = FancyArrowPatch(
        p0,
        p1,
        arrowstyle="-|>",
        mutation_scale=17,
        linewidth=2.0,
        color="0.08",
        shrinkA=3,
        shrinkB=3,
        zorder=6,
    )
    ax.add_patch(arrow)

    mid = 0.5 * (p0 + p1)
    tangent = np.array([-np.sin(angle), np.cos(angle)])

    ax.text(
        *(mid + label_offset * tangent),
        label,
        fontsize=17,
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.16",
            facecolor=PLANE_COLOR,
            edgecolor="none",
            alpha=0.92,
        ),
        zorder=7,
    )


def make_figure_4():
    """Creation and annihilation as neighboring energy transitions."""
    fig, ax = setup_axes()
    draw_energy_rings(ax)

    n = TRANSITION_N
    r_inner = radius(n)
    r_outer = radius(n + 1)

    # Put the two arrows in different angular positions so their meanings
    # remain visually distinct while both connect the same neighboring levels.
    radial_arrow(
        ax,
        r_inner,
        r_outer,
        angle=np.deg2rad(32),
        label=r"$\hat{a}^{\dagger}$",
        label_offset=0.18,
    )

    radial_arrow(
        ax,
        r_outer,
        r_inner,
        angle=np.deg2rad(-32),
        label=r"$\hat{a}$",
        label_offset=-0.18,
    )

    ax.text(
        0.04, 0.96,
        r"$\Delta E=\hbar\omega$",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=16,
    )

    save(fig, OUTPUT_4)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    make_figure_3()
    make_figure_4()


if __name__ == "__main__":
    main()
