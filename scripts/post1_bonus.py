"""
Bonus Figure — Building a higher-order optical vortex

Four degenerate third-order Hermite-Gaussian modes combine with
specific amplitudes and phases to form an LG mode with |ell| = 3.

The figure shows:

    HG30    HG21    HG12    HG03

                  ↓

              LG_0^(+3)

The LG intensity is a doughnut, but its phase winds three complete
times around the dark centre.

Visual appearance matches Figures 2 and 3.
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

WAIST = 0.70e-3


# ----- Numerical grid -----

WINDOW_SIZE = 3.5e-3
N_GRID = 1000


# ----- Appearance -----

CMAP = "inferno"
DISPLAY_GAMMA = 1.0

FIGSIZE = (10, 6)
DPI = 300

TITLE_FONTSIZE = 13
FORMULA_FONTSIZE = 11
ANNOTATION_FONTSIZE = 12

WSPACE = 0.025
HSPACE = 0.08


# ----- Output -----

OUTPUT_DIR = Path("./outputs")

OUTPUT_PNG = "bonus_higher_order_vortex.png"
OUTPUT_PDF = "bonus_higher_order_vortex.pdf"


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

    Overall normalization is omitted here; each HG mode is
    subsequently normalized to unit discrete power.
    """

    xi = np.sqrt(2.0) * x / waist
    eta = np.sqrt(2.0) * y / waist

    Hn = eval_hermite(n, xi)
    Hm = eval_hermite(m, eta)

    gaussian = np.exp(
        -(x**2 + y**2) / waist**2
    )

    return Hn * Hm * gaussian


def normalize_power(field):
    """Normalize complex field to unit discrete power."""

    return field / np.sqrt(
        np.sum(np.abs(field)**2)
    )


# ============================================================
# THIRD-ORDER HG BASIS
# ============================================================

HG30 = normalize_power(
    hermite_gaussian(
        3, 0, X, Y, WAIST
    ).astype(complex)
)

HG21 = normalize_power(
    hermite_gaussian(
        2, 1, X, Y, WAIST
    ).astype(complex)
)

HG12 = normalize_power(
    hermite_gaussian(
        1, 2, X, Y, WAIST
    ).astype(complex)
)

HG03 = normalize_power(
    hermite_gaussian(
        0, 3, X, Y, WAIST
    ).astype(complex)
)


# ============================================================
# BUILD LG_0^(+3)
# ============================================================

#
# In the normalized HG basis:
#
#                  1
# LG_0^(+3) = ----------- [
#                2 sqrt(2)
#
#               HG30
#             + i sqrt(3) HG21
#             -   sqrt(3) HG12
#             - i         HG03
#
#             ]
#
# The opposite winding is obtained by complex conjugation.
#

LG_PLUS_3 = (
    HG30
    + 1j * np.sqrt(3.0) * HG21
    - np.sqrt(3.0) * HG12
    - 1j * HG03
) / (2.0 * np.sqrt(2.0))


LG_MINUS_3 = np.conjugate(
    LG_PLUS_3
)


# ============================================================
# INTENSITY
# ============================================================

def normalized_intensity(field):
    """Return peak-normalized intensity."""

    intensity = np.abs(field)**2

    return intensity / intensity.max()


HG_INTENSITIES = [
    normalized_intensity(HG30),
    normalized_intensity(HG21),
    normalized_intensity(HG12),
    normalized_intensity(HG03),
]

LG_INTENSITY = normalized_intensity(
    LG_PLUS_3
)


# ============================================================
# FIGURE
# ============================================================

fig = plt.figure(
    figsize=FIGSIZE
)

gs = fig.add_gridspec(
    2,
    4,
    height_ratios=[
        1.0,
        1.35,
    ],
    left=0.025,
    right=0.985,
    bottom=0.035,
    top=0.92,
    wspace=WSPACE,
    hspace=HSPACE,
)


# ============================================================
# TOP ROW — FOUR HG COMPONENTS
# ============================================================

labels = [
    r"$HG_{30}$",
    r"$i\sqrt{3}\,HG_{21}$",
    r"$-\sqrt{3}\,HG_{12}$",
    r"$-iHG_{03}$",
]


for col in range(4):

    ax = fig.add_subplot(
        gs[0, col]
    )

    ax.imshow(
        HG_INTENSITIES[col],
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
        0.045,
        0.94,
        labels[col],
        transform=ax.transAxes,
        color="white",
        fontsize=FORMULA_FONTSIZE,
        horizontalalignment="left",
        verticalalignment="top",
    )


# ============================================================
# BOTTOM — RESULTING LG MODE
# ============================================================

# Create a nested grid in the bottom centre.
# The empty first row acts as a vertical spacer.
lg_gs = gs[1, 1:3].subgridspec(
    2,
    1,
    height_ratios=[0.22, 1.0],
    hspace=0.0,
)

ax_lg = fig.add_subplot(
    lg_gs[1, 0]
)


ax_lg.imshow(
    LG_INTENSITY,
    origin="lower",
    cmap=CMAP,
    norm=PowerNorm(
        gamma=DISPLAY_GAMMA,
        vmin=0,
        vmax=1,
    ),
    interpolation="bilinear",
)

ax_lg.set_xticks([])
ax_lg.set_yticks([])

for spine in ax_lg.spines.values():
    spine.set_visible(False)

ax_lg.text(
    0.045,
    0.94,
    r"$LG_{0}^{+3}$",
    transform=ax_lg.transAxes,
    color="white",
    fontsize=FORMULA_FONTSIZE,
    horizontalalignment="left",
    verticalalignment="top",
)


# ============================================================
# HEADERS / EXPLANATION
# ============================================================

fig.text(
    0.5,
    0.965,
    r"Four 3$^\text{rd}$-order Hermite–Gaussian modes combine into a 3$^\text{rd}$-order vortex",
    horizontalalignment="center",
    verticalalignment="top",
    fontsize=TITLE_FONTSIZE,
)

fig.text(
    0.5,
    0.475,
    r"$\downarrow$",
    horizontalalignment="center",
    verticalalignment="center",
    fontsize=ANNOTATION_FONTSIZE,
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

png_path = (
    OUTPUT_DIR
    / OUTPUT_PNG
)

pdf_path = (
    OUTPUT_DIR
    / OUTPUT_PDF
)


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


print(
    f"Saved: {png_path}"
)

print(
    f"Saved: {pdf_path}"
)

plt.show()