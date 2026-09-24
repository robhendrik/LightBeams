"""
Figure 1 — Why laser beams keep their shape

The same propagation calculation is applied to two initial fields:

    1. A hard-edged circular beam
    2. A Gaussian beam

Both propagate the same physical distance using the angular-spectrum
method. The calculation is performed on a larger domain than the
displayed region to suppress FFT wrap-around artifacts.

The point of the figure:
    A hard edge develops diffraction structure.
    A Gaussian broadens while retaining its Gaussian shape.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm


# ============================================================
# CONFIGURATION
# ============================================================

# ----- Physics -----

WAVELENGTH = 633e-9          # wavelength [m]
Z = 5.0                      # propagation distance [m]

APERTURE_RADIUS = 0.65e-3    # hard circular beam radius [m]
GAUSSIAN_WAIST = 0.70e-3     # Gaussian 1/e FIELD radius [m]


# ----- Numerical grid -----
#
# Calculation window is deliberately much larger than the
# region shown in the final figure. This prevents diffracted
# light from wrapping around the FFT boundaries.
#

CALC_WINDOW = 40e-3          # full calculation width [m]
N = 2048                     # samples per dimension

DISPLAY_WINDOW = 10e-3        # full displayed width [m]


# ----- Display -----

CMAP = "inferno"

# gamma < 1 reveals weak diffraction rings.
# Set to 1.0 for strictly linear intensity display.
DISPLAY_GAMMA = 0.45

FIGSIZE = (8, 8)
DPI = 300

SHOW_COLUMN_LABELS = True
SHOW_ROW_LABELS = True


# ----- Output -----

OUTPUT_DIR = Path("./outputs")
OUTPUT_PNG = "figure_1_diffraction_vs_gaussian.png"
OUTPUT_PDF = "figure_1_diffraction_vs_gaussian.pdf"


# ============================================================
# ANGULAR-SPECTRUM PROPAGATION
# ============================================================

def angular_spectrum(U0, z, wavelength, dx):
    """
    Propagate a scalar complex field by distance z.

    Uses the exact angular-spectrum transfer function:

        H(kx, ky) = exp(i kz z)

    with

        kz = sqrt(k^2 - kx^2 - ky^2)

    Propagating spatial-frequency components are retained.
    """

    ny, nx = U0.shape

    fx = np.fft.fftfreq(nx, d=dx)
    fy = np.fft.fftfreq(ny, d=dx)

    FX, FY = np.meshgrid(fx, fy)

    k = 2.0 * np.pi / wavelength

    kx = 2.0 * np.pi * FX
    ky = 2.0 * np.pi * FY

    kz_squared = k**2 - kx**2 - ky**2

    # Our paraxial beams contain no relevant evanescent
    # components, but treating kz as complex makes the
    # propagator mathematically complete.
    kz = np.sqrt(kz_squared.astype(complex))

    H = np.exp(1j * kz * z)

    spectrum = np.fft.fft2(U0)

    Uz = np.fft.ifft2(
        spectrum * H
    )

    return Uz


# ============================================================
# GRID
# ============================================================

dx = CALC_WINDOW / N

x = (
    np.arange(N) - N / 2
) * dx

X, Y = np.meshgrid(x, x)

R = np.sqrt(
    X**2 + Y**2
)

print()
print("Numerical grid")
print("--------------")
print(f"N                 : {N}")
print(f"Calculation window: {CALC_WINDOW * 1e3:.1f} mm")
print(f"Pixel size        : {dx * 1e6:.2f} µm")
print(f"Display window    : {DISPLAY_WINDOW * 1e3:.1f} mm")


# ============================================================
# INITIAL FIELDS
# ============================================================

# Hard-edged circular field.
#
# Uniform amplitude and phase inside the circle.

U_circle_0 = (
    R <= APERTURE_RADIUS
).astype(float)


# Fundamental Gaussian field.
#
# GAUSSIAN_WAIST is the 1/e FIELD radius:
#
#     E(r) = exp(-r² / w0²)
#
# Therefore:
#
#     I(r) = exp(-2r² / w0²)

U_gauss_0 = np.exp(
    -(R / GAUSSIAN_WAIST)**2
)


# ============================================================
# PROPAGATE BOTH FIELDS
# ============================================================

print()
print(f"Propagating both fields over {Z:.2f} m ...")


U_circle_z = angular_spectrum(
    U_circle_0,
    Z,
    WAVELENGTH,
    dx,
)

U_gauss_z = angular_spectrum(
    U_gauss_0,
    Z,
    WAVELENGTH,
    dx,
)


# ============================================================
# INTENSITIES
# ============================================================

I_circle_0 = np.abs(U_circle_0)**2
I_circle_z = np.abs(U_circle_z)**2

I_gauss_0 = np.abs(U_gauss_0)**2
I_gauss_z = np.abs(U_gauss_z)**2


# ============================================================
# PHYSICAL DIAGNOSTICS
# ============================================================

D = 2.0 * APERTURE_RADIUS

z_rayleigh = (
    np.pi
    * GAUSSIAN_WAIST**2
    / WAVELENGTH
)

gaussian_w_z = (
    GAUSSIAN_WAIST
    * np.sqrt(
        1.0 + (Z / z_rayleigh)**2
    )
)

# Far-field Airy first-zero estimate.
# Included only as a useful scale check.

airy_first_zero = (
    1.22
    * WAVELENGTH
    * Z
    / D
)

print()
print("Physical scales")
print("---------------")
print(f"Wavelength        : {WAVELENGTH * 1e9:.0f} nm")
print(f"Propagation       : {Z:.2f} m")
print(f"Aperture diameter : {D * 1e3:.2f} mm")
print(f"Gaussian waist    : {GAUSSIAN_WAIST * 1e3:.2f} mm")
print(f"Rayleigh range    : {z_rayleigh:.2f} m")
print(f"Gaussian w(z)     : {gaussian_w_z * 1e3:.2f} mm")
print(f"Airy zero estimate: {airy_first_zero * 1e3:.2f} mm")


# ============================================================
# CROP DISPLAY REGION
# ============================================================

half_display = DISPLAY_WINDOW / 2

display_mask = (
    (x >= -half_display)
    & (x <= half_display)
)

indices = np.where(display_mask)[0]

i0 = indices[0]
i1 = indices[-1] + 1


def crop(image):
    """Crop an image to the central displayed region."""

    return image[
        i0:i1,
        i0:i1,
    ]


I_circle_0_crop = crop(I_circle_0)
I_circle_z_crop = crop(I_circle_z)

I_gauss_0_crop = crop(I_gauss_0)
I_gauss_z_crop = crop(I_gauss_z)


# ============================================================
# NORMALIZATION
# ============================================================
#
# Normalize each image by its own peak.
#
# For this conceptual figure this makes the transverse
# structures easy to compare. We are comparing SHAPE,
# not absolute irradiance.
#

I_circle_0_crop /= I_circle_0_crop.max()
I_circle_z_crop /= I_circle_z_crop.max()

I_gauss_0_crop /= I_gauss_0_crop.max()
I_gauss_z_crop /= I_gauss_z_crop.max()


# ============================================================
# PLOT
# ============================================================

extent_mm = [
    -half_display * 1e3,
     half_display * 1e3,
    -half_display * 1e3,
     half_display * 1e3,
]

fig, axes = plt.subplots(
    2,
    2,
    figsize=FIGSIZE,
    constrained_layout=True,
)

images = [
    I_circle_0_crop,
    I_circle_z_crop,
    I_gauss_0_crop,
    I_gauss_z_crop,
]


for ax, image in zip(axes.flat, images):

    ax.imshow(
        image,
        extent=extent_mm,
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


# ============================================================
# MINIMAL LABELS
# ============================================================

if SHOW_COLUMN_LABELS:

    axes[0, 0].set_title(
        "Before propagation",
        fontsize=13,
    )

    axes[0, 1].set_title(
        f"After {Z:g} m",
        fontsize=13,
    )


if SHOW_ROW_LABELS:

    axes[0, 0].set_ylabel(
        "Hard edge",
        fontsize=12,
        labelpad=12,
    )

    axes[1, 0].set_ylabel(
        "Gaussian",
        fontsize=12,
        labelpad=12,
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
)

plt.savefig(
    pdf_path,
    bbox_inches="tight",
)

print()
print(f"Saved: {png_path}")
print(f"Saved: {pdf_path}")

plt.show()