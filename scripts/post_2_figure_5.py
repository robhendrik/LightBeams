"""
post_2_figure_5.py

Figure 5 — What one more photon adds.

A 2x2 real-space intensity comparison using the same Hermite-Gaussian /
Laguerre-Gaussian visual language as Post 1.

Columns:
    HG mode (left)
    LG mode with ell = 2 (right)

Rows:
    n photons
    n + 1 photons

The spatial mode shape is unchanged when one photon is added. The lower row
is only schematically brighter to indicate the additional excitation.

Output:
    outputs/post_2_figure_5.png
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from scipy.special import eval_hermite, eval_genlaguerre


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "post_2_figure_5.png"

# Beam / numerical grid
WAIST = 0.70e-3
WINDOW_SIZE = 3.5e-3
N_GRID = 1000

# Modes
HG_N = 1
HG_M = 0

LG_P = 0
LG_ELL = 2

# The absolute intensity difference is schematic. We deliberately keep it
# modest so the unchanged spatial shape remains the dominant message.
TOP_BRIGHTNESS = 0.72
BOTTOM_BRIGHTNESS = 1.00

# Appearance — deliberately follows Post 1's mode figures.
CMAP = "inferno"
DISPLAY_GAMMA = 1.0

FIGSIZE = (8.2, 8.2)
DPI = 300

TITLE_FONTSIZE = 14
ROW_FONTSIZE = 13
FORMULA_FONTSIZE = 12
ANNOTATION_FONTSIZE = 11

WSPACE = 0.035
HSPACE = 0.035

FORMULA_X = 0.045
FORMULA_Y = 0.95


# ============================================================
# GRID
# ============================================================

x = np.linspace(
    -WINDOW_SIZE / 2,
    WINDOW_SIZE / 2,
    N_GRID,
)

X, Y = np.meshgrid(x, x)
R = np.sqrt(X**2 + Y**2)
PHI = np.arctan2(Y, X)


# ============================================================
# MODE FIELDS
# ============================================================

def hermite_gaussian(n, m, x, y, waist):
    """Hermite-Gaussian field at the beam waist."""
    xi = np.sqrt(2.0) * x / waist
    eta = np.sqrt(2.0) * y / waist

    return (
        eval_hermite(n, xi)
        * eval_hermite(m, eta)
        * np.exp(-(x**2 + y**2) / waist**2)
    )


def laguerre_gaussian(p, ell, r, phi, waist):
    """Laguerre-Gaussian field at the beam waist."""
    abs_ell = abs(ell)
    rho2 = 2.0 * r**2 / waist**2

    radial = (
        (np.sqrt(2.0) * r / waist) ** abs_ell
        * eval_genlaguerre(p, abs_ell, rho2)
        * np.exp(-r**2 / waist**2)
    )

    return radial * np.exp(1j * ell * phi)


def normalized_intensity(field):
    """Return peak-normalized intensity."""
    intensity = np.abs(field) ** 2
    return intensity / intensity.max()


HG = hermite_gaussian(HG_N, HG_M, X, Y, WAIST).astype(complex)
LG = laguerre_gaussian(LG_P, LG_ELL, R, PHI, WAIST)

I_HG = normalized_intensity(HG)
I_LG = normalized_intensity(LG)


# ============================================================
# FOUR PANELS
# ============================================================

intensities = [
    [TOP_BRIGHTNESS * I_HG, TOP_BRIGHTNESS * I_LG],
    [BOTTOM_BRIGHTNESS * I_HG, BOTTOM_BRIGHTNESS * I_LG],
]

panel_labels = [
    [rf"$HG_{{{HG_N}{HG_M}}}$", rf"$LG_{{0}}^{{{LG_ELL}}}$"],
    [rf"$HG_{{{HG_N}{HG_M}}}$", rf"$LG_{{0}}^{{{LG_ELL}}}$"],
]


# ============================================================
# PLOT
# ============================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=FIGSIZE,
)

fig.subplots_adjust(
    left=0.07,
    right=0.99,
    bottom=0.08,
    top=0.89,
    wspace=WSPACE,
    hspace=HSPACE,
)

for row in range(2):
    for col in range(2):
        ax = axes[row, col]

        ax.imshow(
            intensities[row][col],
            origin="lower",
            cmap=CMAP,
            norm=PowerNorm(
                gamma=DISPLAY_GAMMA,
                vmin=0,
                vmax=1,
            ),
            interpolation="bilinear",
        )

        ax.set_xticks([])
        ax.set_yticks([])

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.text(
            FORMULA_X,
            FORMULA_Y,
            panel_labels[row][col],
            transform=ax.transAxes,
            color="white",
            fontsize=FORMULA_FONTSIZE,
            ha="left",
            va="top",
        )


# ============================================================
# HEADERS AND ROW LABELS
# ============================================================

axes[0, 0].set_title(
    "Hermite–Gaussian mode",
    fontsize=TITLE_FONTSIZE,
    pad=9,
)

axes[0, 1].set_title(
    rf"Laguerre–Gaussian mode, $\ell={LG_ELL}$",
    fontsize=TITLE_FONTSIZE,
    pad=9,
)

# Row labels are placed outside the panels so they cannot be confused
# with properties of the transverse mode itself.
fig.text(
    0.025,
    0.685,
    r"$n$ photons",
    rotation=90,
    fontsize=ROW_FONTSIZE,
    ha="center",
    va="center",
)

fig.text(
    0.025,
    0.285,
    r"$n+1$ photons",
    rotation=90,
    fontsize=ROW_FONTSIZE,
    ha="center",
    va="center",
)


# ============================================================
# ONE-PHOTON INCREMENTS
# ============================================================

# Put the physical increment below each column rather than inside the
# intensity images. The spatial profiles themselves remain uncluttered.
fig.text(
    0.29,
    0.025,
    r"$+\hbar\omega,\quad +\hbar k,\quad \Delta L_z=0$",
    fontsize=ANNOTATION_FONTSIZE,
    ha="center",
    va="bottom",
)

fig.text(
    0.76,
    0.025,
    rf"$+\hbar\omega,\quad +\hbar k,\quad +{LG_ELL}\hbar\ \mathrm{{OAM}}$",
    fontsize=ANNOTATION_FONTSIZE,
    ha="center",
    va="bottom",
)


# ============================================================
# SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

plt.savefig(
    OUTPUT,
    dpi=DPI,
    bbox_inches="tight",
    facecolor="white",
)

print(f"Saved: {OUTPUT}")
plt.show()
