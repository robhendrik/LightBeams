"""
post_2_figure_2.py

Figure 2 — classical complex amplitude.

A single classical mode is represented by a complex amplitude A. The point
rotates at fixed |A|. The continuous background plane emphasizes that,
classically, A may take any complex value: there are no preferred radii.

Output:
    outputs/post_2_figure_2.gif
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "post_2_figure_2.gif"

AMPLITUDE = 1.65
N_FRAMES = 80
FPS = 20

LIMIT = 2.35
FIGSIZE = (7.2, 7.2)
DPI = 120

# A short fading trail makes the rotation readable without introducing
# additional "allowed" circles.
TRAIL_FRACTION = 0.18
TRAIL_POINTS = 30


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=FIGSIZE)

    ax.set_xlim(-LIMIT, LIMIT)
    ax.set_ylim(-LIMIT, LIMIT)
    ax.set_aspect("equal")
    ax.set_facecolor("0.96")

    # Continuous amplitude plane: a very subtle uniform field, deliberately
    # without rings or a radial gradient.
    ax.axhspan(-LIMIT, LIMIT, color="0.96", zorder=0)

    # Axes through the origin.
    ax.axhline(0, linewidth=1.0, color="0.55", zorder=1)
    ax.axvline(0, linewidth=1.0, color="0.55", zorder=1)

    # Remove the conventional plot frame/ticks: these are coordinates in
    # amplitude space, not a numerical graph the reader needs to measure.
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

    # A faint trace of the particular orbit being followed. This is a
    # trajectory, not a discrete allowed-energy contour.
    theta_orbit = np.linspace(0, 2 * np.pi, 500)
    ax.plot(
        AMPLITUDE * np.cos(-1*theta_orbit),
        AMPLITUDE * np.sin(-1*theta_orbit),
        linewidth=1.0,
        alpha=0.18,
        color="0.25",
        zorder=2,
    )

    # Animated state and trail.
    point, = ax.plot(    [], [],
        marker="o",
        markersize=10,
        linestyle="none",
        color="0.08",
        zorder=5,
    )

    trail, = ax.plot(
        [], [],
        linewidth=2.0,
        color="0.20",
        alpha=0.35,
        solid_capstyle="round",
        zorder=4,
    )

    # Radial line makes |A| explicit without adding another contour.
    radius_line, = ax.plot(
        [], [],
        linewidth=1.3,
        color="0.35",
        alpha=0.55,
        zorder=3,
    )

    amplitude_label = ax.text(
        0, 0, r"$A$",
        fontsize=15,
        ha="left",
        va="bottom",
        zorder=6,
    )

    def update(frame):
        theta = 2 * np.pi * frame / N_FRAMES

        x = AMPLITUDE * np.cos(theta)
        y = AMPLITUDE * np.sin(theta)

        point.set_data([x], [y])
        radius_line.set_data([0, x], [0, y])

        # Short trailing arc behind the point.
        trail_angle = 2 * np.pi * TRAIL_FRACTION
        trail_theta = np.linspace(theta - trail_angle, theta, TRAIL_POINTS)
        trail.set_data(
            AMPLITUDE * np.cos(trail_theta),
            AMPLITUDE * np.sin(trail_theta),
        )

        # Keep the label just outside the moving point.
        offset = 0.11
        amplitude_label.set_position(
            (
                x + offset * np.cos(theta),
                y + offset * np.sin(theta),
            )
        )

        return point, trail, radius_line, amplitude_label

    animation = FuncAnimation(
        fig,
        update,
        frames=N_FRAMES,
        interval=1000 / FPS,
        blit=True,
        repeat=True,
    )

    fig.tight_layout(pad=0.35)

    animation.save(
        OUTPUT,
        writer=PillowWriter(fps=FPS),
        dpi=DPI,
    )

    plt.close(fig)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
