"""
post_2_figure_1.py

Figure 1 — A localized classical wave packet.

A Gaussian wave packet travels from left to right. Nothing in this
localization is quantum: it is simply a superposition of classical waves.

The packet starts fully outside the frame, crosses it, disappears fully
beyond the right edge, and only then loops.

Output:
    outputs/post_2_figure_1.gif
"""

from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "post_2_figure_1.gif"

FIGSIZE = (12, 6.5)
DPI = 110
FPS = 24

BG = "#090b10"
FG = "#eef2f7"
MUTED = "#8e9aaa"
BLUE = "#57a6ff"

X_MIN = -10.0
X_MAX = 10.0
N_X = 1600

WAVE_SPEED = 1.0
K0 = 6.5
SIGMA = 1.65

# Same apparent speed as the earlier dispersion animation.
TIME_UNITS_PER_VIDEO_SECOND = 2.5


# ============================================================
# STYLE
# ============================================================

def configure_style():
    """Apply the visual language used in the earlier wave-packet figure."""
    mpl.rcParams.update(
        {
            "figure.figsize": FIGSIZE,
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "text.color": FG,
            "axes.labelcolor": FG,
            "axes.edgecolor": MUTED,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.size": 15,
            "axes.labelsize": 15,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "animation.embed_limit": 100,
        }
    )


def style_axes(ax):
    """Keep the plot explanatory and visually quiet."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)


# ============================================================
# ANIMATION
# ============================================================

def main():
    configure_style()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    x = np.linspace(X_MIN, X_MAX, N_X)

    # Start/end far enough away that the Gaussian is effectively invisible
    # before the animation loops.
    x_start = X_MIN - 4.5 * SIGMA
    x_end = X_MAX + 4.5 * SIGMA

    duration = (x_end - x_start) / WAVE_SPEED
    video_seconds = duration / TIME_UNITS_PER_VIDEO_SECOND
    n_frames = int(np.ceil(video_seconds * FPS))
    times = np.linspace(0.0, duration, n_frames, endpoint=False)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    style_axes(ax)

    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(-1.2, 1.2)

    ax.set_xlabel("position")
    ax.set_ylabel("field amplitude")
    ax.set_yticks([-1, 0, 1])

    # No title and no envelope curves: the visual point is simply that a
    # classical wave can form a localized travelling packet.
    ax.axhline(
        0.0,
        color=MUTED,
        alpha=0.35,
        linewidth=1.0,
    )

    wave, = ax.plot(
        [],
        [],
        color=BLUE,
        linewidth=2.7,
    )

    def field(t):
        """Classical Gaussian wave packet moving rigidly to the right."""
        xc = x_start + WAVE_SPEED * t
        envelope = np.exp(
            -0.5 * ((x - xc) / SIGMA) ** 2
        )

        return envelope * np.cos(
            K0 * (x - xc)
        )

    def update(i):
        y = field(times[i])
        wave.set_data(x, y)
        return (wave,)

    fig.tight_layout()

    animation = FuncAnimation(
        fig,
        update,
        frames=len(times),
        interval=1000 / FPS,
        blit=True,
        repeat=True,
    )

    animation.save(
        OUTPUT,
        writer=PillowWriter(fps=FPS),
        dpi=DPI,
    )

    plt.close(fig)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
