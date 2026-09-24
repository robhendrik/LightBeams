"""Figure 5 — Orbital angular momentum in a vortex beam.

Schematic cross sections of an LG-like beam. The intensity is computed
from |(x + i*y) exp(-r**2/w**2)|**2. Arrows illustrate the direction
of the local momentum and the resulting orbital motion of a particle;
they are not a force calculation or a depiction of spin polarization.

Run from any directory with: python scripts/post1_figure5.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np


OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "figure_5_OAM.png"
DPI = 250
CMAP = "inferno"
CYAN = "#6de1ef"
WHITE = "#f5f5f5"
GOLD = "#fff1b0"


def intensity_image(size=600):
    """Return a peak-normalized first-order vortex intensity image."""
    q = np.linspace(-1.15, 1.15, size)
    x, y = np.meshgrid(q, q)
    r2 = x * x + y * y
    intensity = r2 * np.exp(-2 * r2 / 0.46**2)
    return intensity / intensity.max()


INTENSITY = intensity_image()


def beam_panel(ax):
    ax.imshow(INTENSITY, origin="lower", extent=(-1, 1, -1, 1), cmap=CMAP,
              vmin=0, vmax=1, interpolation="bilinear")
    ax.set_xlim(-0.83, 0.83)
    ax.set_ylim(-0.83, 0.83)
    ax.set_aspect("equal")
    ax.set_facecolor("black")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def curved_arrow(ax, radius, start_deg, end_deg, color=CYAN, lw=2.8):
    """Draw an azimuthal arrow, with sign controlled by angle order."""
    angles = np.deg2rad(np.linspace(start_deg, end_deg, 90))
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    ax.plot(x, y, color=color, lw=lw, solid_capstyle="round", zorder=5)
    ax.add_patch(FancyArrowPatch(
        (x[-8], y[-8]), (x[-1], y[-1]), arrowstyle="-|>",
        mutation_scale=19, lw=lw, color=color, zorder=6,
    ))


def add_particle(ax, angle_deg=32, radius=0.39):
    angle = np.deg2rad(angle_deg)
    x, y = radius * np.cos(angle), radius * np.sin(angle)
    ax.add_patch(Circle((x, y), 0.065, facecolor=WHITE,
                        edgecolor="#bababa", lw=1.2, zorder=8))


def main():
    fig = plt.figure(figsize=(13.2, 5.6), facecolor="white")
    grid = fig.add_gridspec(1, 2, width_ratios=(1, 1.72),
                           left=0.025, right=0.985, bottom=0.10,
                           top=0.83, wspace=0.055)

    left = fig.add_subplot(grid[0, 0])
    beam_panel(left)
    left.set_title("Momentum has two directions", fontsize=17, pad=15)

    # The page is a transverse cross section. A dotted circle denotes
    # the longitudinal component, pointing toward the viewer (+z).
    point_angle = np.deg2rad(34)
    point = np.array([0.41 * np.cos(point_angle),
                      0.41 * np.sin(point_angle)])
    tangent = np.array([-np.sin(point_angle), np.cos(point_angle)])
    left.add_patch(FancyArrowPatch(
        point, point + 0.39 * tangent, arrowstyle="-|>",
        mutation_scale=21, lw=3.3, color=CYAN, zorder=8,
    ))
    left.add_patch(Circle(point, 0.043, facecolor="none",
                          edgecolor=WHITE, lw=1.8, zorder=9))
    left.plot(*point, marker="o", ms=3.4, color=WHITE, zorder=10)
    left.text(-0.71, 0.65, r"$p_z$: forward, out of page  $\odot$",
              color=WHITE, fontsize=12, va="center")
    left.text(-0.71, -0.67, r"$p_\phi$: around the axis",
              color=CYAN, fontsize=13, va="center")
    left.annotate("dark axis", xy=(0, 0), xytext=(-0.72, -0.27),
                  color=WHITE, fontsize=10,
                  arrowprops={"arrowstyle": "->", "color": WHITE,
                              "lw": 1.1})

    right_grid = grid[0, 1].subgridspec(1, 2, wspace=0.025)
    plus = fig.add_subplot(right_grid[0, 0])
    minus = fig.add_subplot(right_grid[0, 1])
    for ax in (plus, minus):
        beam_panel(ax)
        add_particle(ax)
    plus.set_title(r"$\ell=+1$", fontsize=17, pad=15)
    minus.set_title(r"$\ell=-1$", fontsize=17, pad=15)
    curved_arrow(plus, 0.48, 45, 245)
    curved_arrow(minus, 0.48, 20, -180)
    for ax in (plus, minus):
        ax.text(0, -0.72, "particle motion", ha="center", va="center",
                color=WHITE, fontsize=11)

    fig.text(0.685, 0.91, "Reverse the winding, reverse the torque",
             ha="center", fontsize=17, color="black")
    fig.text(0.5, 0.025,
             "Transverse view along the beam; the bright ring is the same for both vortex signs.",
             ha="center", fontsize=10.5, color="#555555")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
