"""
Figure 3 — From two lobes to a vortex

Two degenerate first-order Hermite-Gaussian modes are combined
with different relative amplitudes and phases.

Column 1:
    HG10
    HG01

Column 2:
    HG10 + HG01
    HG10 - HG01

Column 3:
    HG10 + i HG01
    HG10 - i HG01

Only intensity is shown. The final two fields therefore look
identical: their difference is hidden in the optical phase.

Visual appearance matches Figures 1 and 2.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from scipy.special import eval_hermite


# ============================================================
# CONFIGURATION
# ============================================================

# ----- Beam -----

WAIST = 0.70e-3              # Gaussian 1/e FIELD radius [m]


# ----- Numerical grid -----

WINDOW_SIZE = 3.5e-3         # full transverse width [m]
N_GRID = 1000


# ----- Appearance -----

CMAP = "inferno"
DISPLAY_GAMMA = 1.0

FIGSIZE = (9, 6)
DPI = 300

TITLE_FONTSIZE = 13
FORMULA_FONTSIZE = 11

WSPACE = 0.025
HSPACE = 0.025

FORMULA_X = 0.045
FORMULA_Y = 0.95


# ----- Output -----

OUTPUT_DIR = Path("./outputs")
OUTPUT_PNG = "figure_3_hg_to_lg.png"
OUTPUT_PDF = "figure_3_hg_to_lg.pdf"


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
# HERMITE-GAUSSIAN FIELD
# ============================================================

def hermite_gaussian(n, m, x, y, waist):
    """
    Hermite-Gaussian field at the beam waist z = 0.

    Overall normalization is omitted because only relative
    amplitudes and phases matter here.
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
# BASIC MODES
# ============================================================

HG10 = hermite_gaussian(
    1, 0, X, Y, WAIST
).astype(complex)

HG01 = hermite_gaussian(
    0, 1, X, Y, WAIST
).astype(complex)


def normalize_power(field):
    """Normalize a complex field to unit discrete power."""

    return field / np.sqrt(
        np.sum(np.abs(field)**2)
    )


HG10 = normalize_power(HG10)
HG01 = normalize_power(HG01)


# ============================================================
# CONSTRUCT THE SIX FIELDS
# ============================================================

sqrt2 = np.sqrt(2.0)


# Column 1 — basis modes

field_00 = HG10
field_10 = HG01


# Column 2 — real superpositions

field_01 = (
    HG10 + HG01
) / sqrt2

field_11 = (
    HG10 - HG01
) / sqrt2


# Column 3 — quadrature superpositions

field_02 = (
    HG10 + 1j * HG01
) / sqrt2

field_12 = (
    HG10 - 1j * HG01
) / sqrt2


fields = [
    [field_00, field_01, field_02],
    [field_10, field_11, field_12],
]


# ============================================================
# PANEL FORMULAS
# ============================================================

formulas = [
    [
        r"$HG_{10}$",
        r"$HG_{10}+HG_{01}$",
        r"$HG_{10}+iHG_{01}$",
    ],
    [
        r"$HG_{01}$",
        r"$HG_{10}-HG_{01}$",
        r"$HG_{10}-iHG_{01}$",
    ],
]


# ============================================================
# INTENSITY
# ============================================================

def normalized_intensity(field):
    """Return peak-normalized intensity."""

    intensity = np.abs(field)**2

    return intensity / intensity.max()


intensities = [
    [
        normalized_intensity(field)
        for field in row
    ]
    for row in fields
]


# ============================================================
# PLOT
# ============================================================

fig, axes = plt.subplots(
    2,
    3,
    figsize=FIGSIZE,
)

fig.subplots_adjust(
    left=0.02,
    right=0.99,
    bottom=0.03,
    top=0.90,
    wspace=WSPACE,
    hspace=HSPACE,
)


for row in range(2):

    for col in range(3):

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

        # -----------------------------------------------
        # Formula in upper-left corner
        # -----------------------------------------------

        ax.text(
            FORMULA_X,
            FORMULA_Y,
            formulas[row][col],
            transform=ax.transAxes,
            color="white",
            fontsize=FORMULA_FONTSIZE,
            horizontalalignment="left",
            verticalalignment="top",
        )


# ============================================================
# COLUMN HEADERS
# ============================================================

axes[0, 0].set_title(
    "Separate",
    fontsize=TITLE_FONTSIZE,
    pad=8,
)

axes[0, 1].set_title(
    "Add / subtract",
    fontsize=TITLE_FONTSIZE,
    pad=8,
)

axes[0, 2].set_title(
    r"Add / subtract with $\pi/2$ phase",
    fontsize=TITLE_FONTSIZE,
    pad=8,
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