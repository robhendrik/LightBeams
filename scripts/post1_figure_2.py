"""
Figure 2 — A family of laser modes

Intensity profiles of the first 16 Hermite-Gaussian modes:

    HG_nm,  n,m = 0,1,2,3

The modes are evaluated at the beam waist z = 0.

The visual appearance is deliberately matched to Figure 1:
black background, inferno colormap, no axes or colorbars.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import eval_hermite
from matplotlib.colors import PowerNorm

# ============================================================
# CONFIGURATION
# ============================================================

# ----- Modes -----

N_MAX = 3
M_MAX = 3

# Gaussian 1/e FIELD radius
WAIST = 0.70e-3              # [m]


# ----- Numerical grid -----

WINDOW_SIZE = 3.5e-3         # full transverse width [m]
N_GRID = 1200                 # samples per dimension


# ----- Appearance -----

CMAP = "inferno"
DISPLAY_GAMMA = 0.75
FIGSIZE = (8, 8)
DPI = 300

LABEL_FONTSIZE = 13

# Space between panels
WSPACE = 0.035
HSPACE = 0.035


# ----- Output -----

OUTPUT_DIR = Path("./outputs")
OUTPUT_PNG = "figure_2_hermite_gaussian_modes.png"
OUTPUT_PDF = "figure_2_hermite_gaussian_modes.pdf"


# ============================================================
# GRID
# ============================================================

x = np.linspace(
    -WINDOW_SIZE / 2,
    WINDOW_SIZE / 2,
    N_GRID,
)

X, Y = np.meshgrid(x, x)


# ============================================================
# HERMITE-GAUSSIAN MODE
# ============================================================

def hermite_gaussian(n, m, x, y, waist):
    """
    Hermite-Gaussian field at the beam waist z = 0.

    Overall normalization constants are omitted because each
    mode is normalized to its own peak intensity for display.

    Convention:

        HG_nm(x,y) ∝
            H_n(sqrt(2)x/w)
            H_m(sqrt(2)y/w)
            exp[-(x²+y²)/w²]

    where w is the Gaussian 1/e field radius.
    """

    xi = np.sqrt(2.0) * x / waist
    eta = np.sqrt(2.0) * y / waist

    Hn = eval_hermite(n, xi)
    Hm = eval_hermite(m, eta)

    gaussian = np.exp(
        -(x**2 + y**2) / waist**2
    )

    return Hn * Hm * gaussian


# ============================================================
# CALCULATE MODES
# ============================================================

modes = {}

for m in range(M_MAX + 1):

    for n in range(N_MAX + 1):

        field = hermite_gaussian(
            n,
            m,
            X,
            Y,
            WAIST,
        )

        intensity = np.abs(field)**2

        # Normalize each mode independently.
        intensity /= intensity.max()

        modes[(n, m)] = intensity


# ============================================================
# PLOT
# ============================================================

n_rows = M_MAX + 1
n_cols = N_MAX + 1

fig, axes = plt.subplots(
    n_rows,
    n_cols,
    figsize=FIGSIZE,
)

fig.subplots_adjust(
    left=0.08,
    right=0.99,
    bottom=0.02,
    top=0.93,
    wspace=WSPACE,
    hspace=HSPACE,
)


for m in range(n_rows):

    for n in range(n_cols):

        ax = axes[m, n]

        ax.imshow(
            modes[(n, m)],
            origin="lower",
            cmap=CMAP,
            norm=PowerNorm(
                gamma=DISPLAY_GAMMA,
                vmin=0,
                vmax=1,
            ),
        )


        ax.set_xticks([])
        ax.set_yticks([])

        for spine in ax.spines.values():
            spine.set_visible(False)


# ============================================================
# MINIMAL MODE LABELS
# ============================================================

# Column labels: n

for n in range(n_cols):

    axes[0, n].set_title(
        f"n = {n}",
        fontsize=LABEL_FONTSIZE,
        pad=8,
    )


# Row labels: m

for m in range(n_rows):

    axes[m, 0].set_ylabel(
        f"m = {m}",
        fontsize=LABEL_FONTSIZE,
        rotation=90,
        labelpad=10,
    )


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

png_path = OUTPUT_DIR / OUTPUT_PNG
pdf_path = OUTPUT_DIR / OUTPUT_PDF

plt.savefig(
    png_path,
    dpi=DPI,
    bbox_inches="tight",
    facecolor="white",
)

plt.savefig(
    pdf_path,
    bbox_inches="tight",
    facecolor="white",
)

print(f"Saved: {png_path}")
print(f"Saved: {pdf_path}")

plt.show()