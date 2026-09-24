"""
Figure 4 — A cylindrical-lens mode converter

Educational PyVista rendering of a pi/2 astigmatic mode converter.

Concept shown:

    rotated HG10
         |
         v
    cylindrical lens
         |
    astigmatic / elliptical waist
         |
    cylindrical lens
         |
         v
        LG01

The HG10 input is oriented at 45 degrees relative to the cylindrical
lens axis. The two cylindrical lenses introduce different Gouy-phase
evolution along the two transverse directions, producing the relative
pi/2 phase required for an LG vortex.

This is an educational illustration, not a numerical propagation
simulation. Beam dimensions and lens curvature are intentionally
exaggerated for clarity.

Requires:
    pip install pyvista vtk numpy matplotlib
"""

from pathlib import Path

import numpy as np
import pyvista as pv
from matplotlib import colormaps


# =====================================================================
# USER SETTINGS
# =====================================================================

# ---------------------------------------------------------------------
# Longitudinal positions
# ---------------------------------------------------------------------

X_INPUT = -6.0

X_SCREEN_IN = -4.6

X_LENS_1 = -1.6
X_LENS_2 = +1.6

X_SCREEN_OUT = +4.6

X_OUTPUT = +6.0

# Beam begins slightly in front of the input source plane and ends
# slightly before the output mode snapshot.
X_BEAM_START = X_SCREEN_IN + 1.38
X_BEAM_END = X_SCREEN_OUT - 1.03


# ---------------------------------------------------------------------
# Beam envelope
# ---------------------------------------------------------------------

# Beam size well outside converter
BEAM_RADIUS_Y_OUTER = 0.62
BEAM_RADIUS_Z_OUTER = 0.62

# Strongly astigmatic waist between lenses.
#
# Deliberately exaggerated so that the astigmatic focus is immediately
# visible in the educational rendering.
BEAM_RADIUS_Y_WAIST = 0.07
BEAM_RADIUS_Z_WAIST = 0.42

# Position of illustrative waist
X_WAIST = 0.0

# Number of longitudinal/radial samples
BEAM_NX = 240
BEAM_NTHETA = 100

# Beam envelope appearance
BEAM_COLOR = "#ff7058"
BEAM_OPACITY = 0.22

BEAM_AMBIENT = 0.32
BEAM_DIFFUSE = 0.65
BEAM_SPECULAR = 0.45
BEAM_SPECULAR_POWER = 25


# ---------------------------------------------------------------------
# Central propagation axis
# ---------------------------------------------------------------------

SHOW_AXIS = False

AXIS_COLOR = "#ff7058"
AXIS_RADIUS = 0.025
AXIS_OPACITY = 0.85


# ---------------------------------------------------------------------
# Mode snapshots
# ---------------------------------------------------------------------

SCREEN_SIZE = 2.45

# Maximum opacity of bright parts of transparent mode snapshots.
SCREEN_OPACITY = 0.9

# Intensity below this threshold becomes completely transparent
# for floating mode snapshots.
MODE_ALPHA_CUTOFF = 0.010

# Controls transparency of faint optical tails.
MODE_ALPHA_GAMMA = 0.55

MODE_RESOLUTION = 400

# Same intensity-display gamma as Figures 2 and 3.
MODE_GAMMA = 1.2

# HG input orientation relative to cylindrical-lens axis.
INPUT_ROTATION_DEG = 45.0

# Matplotlib colormap
MODE_CMAP = "inferno"


# ---------------------------------------------------------------------
# Cylindrical lenses
# ---------------------------------------------------------------------

# Deliberately oversized for educational clarity.

LENS_HEIGHT = 3.4          # z direction
LENS_WIDTH = 2.55          # y direction

LENS_EDGE_THICKNESS = 0.0
LENS_SAG = 0.55

LENS_NY = 120
LENS_NZ = 100


# ---------------------------------------------------------------------
# Glass appearance
# ---------------------------------------------------------------------

GLASS_COLOR = "#b9dce8"
EDGE_COLOR = "#a9bac2"

GLASS_OPACITY = 0.22

BACKGROUND = "black"


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------

WINDOW_SIZE = (1600, 900)

OUT_PNG = Path(
    "./outputs/figure_4_cylindrical_mode_converter.png"
)


# ---------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------

CAMERA_POSITION = (
    10.0,
    -12.5,
    7.0,
)

CAMERA_FOCAL_POINT = (
    0.0,
    0.0,
    0.0,
)

CAMERA_UP = (
    0.0,
    0.0,
    1.0,
)

CAMERA_VIEW_ANGLE = 30.0

CAMERA_CLIPPING_RANGE = (
    0.1,
    60.0,
)


# ---------------------------------------------------------------------
# Lighting
# ---------------------------------------------------------------------

KEY_LIGHT_POSITION = (
    3.0,
    -6.0,
    8.0,
)

KEY_LIGHT_INTENSITY = 1.20


FILL_LIGHT_POSITION = (
    -5.0,
    -3.0,
    3.0,
)

FILL_LIGHT_COLOR = "#b9e8ff"

FILL_LIGHT_INTENSITY = 0.55


RIM_LIGHT_POSITION = (
    1.0,
    6.0,
    5.0,
)

RIM_LIGHT_INTENSITY = 0.80


# =====================================================================
# BASIC GEOMETRY HELPERS
# =====================================================================

def add_cylinder_between(
    plotter,
    p0,
    p1,
    radius,
    color,
    opacity=1.0,
):
    """Add a cylinder between two arbitrary 3D points."""

    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)

    vector = p1 - p0
    length = np.linalg.norm(vector)

    cylinder = pv.Cylinder(
        center=0.5 * (p0 + p1),
        direction=vector,
        radius=radius,
        height=length,
        resolution=60,
    )

    plotter.add_mesh(
        cylinder,
        color=color,
        opacity=opacity,
        smooth_shading=True,
        ambient=0.35,
        diffuse=0.75,
        specular=0.70,
        specular_power=30,
    )


# =====================================================================
# ASTIGMATIC BEAM ENVELOPE
# =====================================================================

def smoothstep(t):
    """Smooth interpolation from 0 to 1."""

    t = np.clip(
        t,
        0.0,
        1.0,
    )

    return t * t * (3.0 - 2.0 * t)


def beam_radius_y(x):
    """
    Illustrative beam radius in the strongly focused Y direction.

    The beam contracts strongly towards the centre of the converter,
    producing an exaggerated narrow waist for educational clarity.
    """

    x = np.asarray(x)

    distance = np.abs(
        x - X_WAIST
    )

    max_distance = max(
        abs(X_INPUT - X_WAIST),
        abs(X_OUTPUT - X_WAIST),
    )

    t = smoothstep(
        distance / max_distance
    )

    return (
        BEAM_RADIUS_Y_WAIST
        +
        (
            BEAM_RADIUS_Y_OUTER
            - BEAM_RADIUS_Y_WAIST
        )
        * t
    )


def beam_radius_z(x):
    """
    Illustrative beam radius in the weakly focused Z direction.

    The beam changes only modestly in this direction, making the
    central waist strongly elliptical.
    """

    x = np.asarray(x)

    distance = np.abs(
        x - X_WAIST
    )

    max_distance = max(
        abs(X_INPUT - X_WAIST),
        abs(X_OUTPUT - X_WAIST),
    )

    t = smoothstep(
        distance / max_distance
    )

    return (
        BEAM_RADIUS_Z_WAIST
        +
        (
            BEAM_RADIUS_Z_OUTER
            - BEAM_RADIUS_Z_WAIST
        )
        * t
    )


def create_beam_envelope():
    """
    Create an elliptical translucent beam envelope.

    The beam starts just in front of the opaque input source plane
    and terminates just before the floating output mode snapshot.
    """

    x = np.linspace(
        X_BEAM_START,
        X_BEAM_END,
        BEAM_NX,
    )

    theta = np.linspace(
        0.0,
        2.0 * np.pi,
        BEAM_NTHETA,
    )

    X, THETA = np.meshgrid(
        x,
        theta,
        indexing="ij",
    )

    ry = beam_radius_y(X)
    rz = beam_radius_z(X)

    Y = ry * np.cos(THETA)
    Z = rz * np.sin(THETA)

    return pv.StructuredGrid(
        X,
        Y,
        Z,
    )


def add_beam_envelope(plotter):
    """Add translucent astigmatic beam envelope."""

    envelope = create_beam_envelope()

    plotter.add_mesh(
        envelope,
        color=BEAM_COLOR,
        opacity=BEAM_OPACITY,
        show_edges=False,
        smooth_shading=True,
        ambient=BEAM_AMBIENT,
        diffuse=BEAM_DIFFUSE,
        specular=BEAM_SPECULAR,
        specular_power=BEAM_SPECULAR_POWER,
    )


# =====================================================================
# CYLINDRICAL LENS GEOMETRY
# =====================================================================

def cylindrical_lens_surfaces(
    x_center,
    curved_direction,
):
    """
    Create front and back surfaces of a plano-convex cylindrical lens.

    Curvature exists only along Y.

    curved_direction:
        -1 : curved surface faces toward -X
        +1 : curved surface faces toward +X

    The two lenses face away from the central waist:
    curved surfaces toward the approximately collimated beams and
    plane surfaces toward the focus.
    """

    y = np.linspace(
        -LENS_WIDTH / 2,
        +LENS_WIDTH / 2,
        LENS_NY,
    )

    z = np.linspace(
        -LENS_HEIGHT / 2,
        +LENS_HEIGHT / 2,
        LENS_NZ,
    )

    Y, Z = np.meshgrid(
        y,
        z,
    )

    u = (
        2.0
        * Y
        / LENS_WIDTH
    )

    sag = (
        LENS_SAG
        * np.sqrt(
            np.clip(
                1.0 - u**2,
                0.0,
                1.0,
            )
        )
    )

    # Flat surface faces the central waist.
    X_flat = np.full_like(
        Y,
        x_center,
    )

    # Curved surface faces away from the central waist.
    X_curved = (
        x_center
        +
        curved_direction
        * (
            LENS_EDGE_THICKNESS
            + sag
        )
    )

    flat = pv.StructuredGrid(
        X_flat,
        Y,
        Z,
    )

    curved = pv.StructuredGrid(
        X_curved,
        Y,
        Z,
    )

    return flat, curved


def add_lens(
    plotter,
    x_center,
    curved_direction,
):
    """Add one transparent cylindrical lens."""

    flat, curved = cylindrical_lens_surfaces(
        x_center,
        curved_direction,
    )

    for surface in (flat, curved):

        plotter.add_mesh(
            surface,
            color=GLASS_COLOR,
            opacity=GLASS_OPACITY,
            show_edges=False,
            smooth_shading=True,
            ambient=0.18,
            diffuse=0.45,
            specular=0.95,
            specular_power=60,
        )

    for surface in (flat, curved):

        edges = surface.extract_feature_edges(
            boundary_edges=True,
            feature_edges=False,
            manifold_edges=False,
        )

        plotter.add_mesh(
            edges,
            color=EDGE_COLOR,
            line_width=1.3,
            opacity=0.78,
        )


# =====================================================================
# TRANSVERSE MODE CALCULATIONS
# =====================================================================

def mode_coordinates():
    """Return normalized transverse coordinates."""

    q = np.linspace(
        -1.0,
        +1.0,
        MODE_RESOLUTION,
    )

    return np.meshgrid(
        q,
        q,
    )


def rotated_hg10_intensity(angle_deg=45.0):
    """
    First-order HG mode rotated in the transverse plane.

    The HG axes lie at 45 degrees to the cylindrical-lens axis in
    the pi/2 mode converter.
    """

    Y, Z = mode_coordinates()

    angle = np.deg2rad(
        angle_deg
    )

    U = (
        Y * np.cos(angle)
        +
        Z * np.sin(angle)
    )

    V = (
        -Y * np.sin(angle)
        +
        Z * np.cos(angle)
    )

    r2 = U**2 + V**2

    field = (
        2.8
        * U
        * np.exp(
            -2.7 * r2
        )
    )

    intensity = np.abs(field)**2

    return (
        intensity
        / intensity.max()
    )


def lg01_intensity():
    """
    First-order Laguerre-Gaussian-like doughnut intensity.

    Only the transverse intensity is shown; the helical phase is
    intentionally not encoded in this figure.
    """

    Y, Z = mode_coordinates()

    r2 = Y**2 + Z**2

    amplitude = (
        np.sqrt(r2)
        * np.exp(
            -2.7 * r2
        )
    )

    intensity = amplitude**2

    return (
        intensity
        / intensity.max()
    )


# =====================================================================
# MODE COLOURING
# =====================================================================

def intensity_to_rgb(intensity):
    """
    Convert normalized intensity to RGB using Matplotlib's inferno map.

    Gamma matches the visual treatment used in Figures 2 and 3.
    """

    display_intensity = (
        intensity**MODE_GAMMA
    )

    cmap = colormaps[
        MODE_CMAP
    ]

    rgba = cmap(
        display_intensity
    )

    rgb = (
        255
        * rgba[..., :3]
    ).astype(np.uint8)

    return rgb


# =====================================================================
# MODE SNAPSHOTS
# =====================================================================

def add_mode_card(
    plotter,
    x,
    intensity,
    transparent_background=True,
):
    """
    Add a transverse mode snapshot.

    transparent_background=False:
        Draw a normal opaque rectangular intensity plane.
        Used for the input/source plane.

    transparent_background=True:
        Suppress the dark background and display the optical mode
        as a floating RGBA image.
        Used for the output LG mode.
    """

    n = intensity.shape[0]

    y = np.linspace(
        -SCREEN_SIZE / 2,
        +SCREEN_SIZE / 2,
        n,
    )

    z = np.linspace(
        -SCREEN_SIZE / 2,
        +SCREEN_SIZE / 2,
        n,
    )

    Y, Z = np.meshgrid(
        y,
        z,
    )

    X = np.full_like(
        Y,
        x,
    )

    grid = pv.StructuredGrid(
        X,
        Y,
        Z,
    )

    rgb = intensity_to_rgb(
        intensity
    )

    # -------------------------------------------------------------
    # Opaque source plane
    # -------------------------------------------------------------

    if not transparent_background:

        colours = rgb.reshape(
            (-1, 3),
            order="F",
        )

        grid["RGB"] = colours

        plotter.add_mesh(
            grid,
            scalars="RGB",
            rgb=True,
            opacity=1.0,
            show_edges=False,
            lighting=False,
        )

        return

    # -------------------------------------------------------------
    # Transparent floating mode
    # -------------------------------------------------------------

    alpha = np.clip(
        intensity**MODE_ALPHA_GAMMA,
        0.0,
        1.0,
    )

    alpha[
        intensity < MODE_ALPHA_CUTOFF
    ] = 0.0

    alpha *= SCREEN_OPACITY

    alpha_uint8 = (
        255.0 * alpha
    ).astype(np.uint8)

    rgba = np.dstack(
        (
            rgb,
            alpha_uint8,
        )
    )

    colours = rgba.reshape(
        (-1, 4),
        order="F",
    )

    grid["RGBA"] = colours

    plotter.add_mesh(
        grid,
        scalars="RGBA",
        rgb=True,
        show_edges=False,
        lighting=False,
    )


# =====================================================================
# SCENE
# =====================================================================

plotter = pv.Plotter(
    off_screen=True,
    window_size=WINDOW_SIZE,
)

plotter.set_background(
    BACKGROUND
)

plotter.enable_anti_aliasing(
    "ssaa"
)


# =====================================================================
# BEAM ENVELOPE
# =====================================================================

add_beam_envelope(
    plotter
)


# =====================================================================
# CENTRAL PROPAGATION AXIS
# =====================================================================

if SHOW_AXIS:

    add_cylinder_between(
        plotter,
        (X_BEAM_START, 0, 0),
        (X_BEAM_END, 0, 0),
        radius=AXIS_RADIUS,
        color=AXIS_COLOR,
        opacity=AXIS_OPACITY,
    )


# =====================================================================
# INPUT / OUTPUT MODES
# =====================================================================

input_mode = rotated_hg10_intensity(
    INPUT_ROTATION_DEG
)

output_mode = lg01_intensity()


# Input:
# Opaque source plane. The beam starts just in front of it.

add_mode_card(
    plotter,
    X_SCREEN_IN,
    input_mode,
    transparent_background=False,
)


# Output:
# Floating LG mode. The beam terminates just before it.

add_mode_card(
    plotter,
    X_SCREEN_OUT,
    output_mode,
    transparent_background=False,
)


# =====================================================================
# CYLINDRICAL LENSES
# =====================================================================

# Lens 1:
# curved surface faces incoming beam;
# plane surface faces central waist.

add_lens(
    plotter,
    X_LENS_1,
    curved_direction=-1,
)


# Lens 2:
# plane surface faces central waist;
# curved surface faces outgoing beam.

add_lens(
    plotter,
    X_LENS_2,
    curved_direction=+1,
)


# =====================================================================
# LIGHTING
# =====================================================================

key_light = pv.Light(
    position=KEY_LIGHT_POSITION,
    focal_point=(
        0.0,
        0.0,
        0.0,
    ),
    color="white",
    intensity=KEY_LIGHT_INTENSITY,
)

plotter.add_light(
    key_light
)


fill_light = pv.Light(
    position=FILL_LIGHT_POSITION,
    focal_point=(
        0.0,
        0.0,
        0.0,
    ),
    color=FILL_LIGHT_COLOR,
    intensity=FILL_LIGHT_INTENSITY,
)

plotter.add_light(
    fill_light
)


rim_light = pv.Light(
    position=RIM_LIGHT_POSITION,
    focal_point=(
        0.0,
        0.0,
        0.0,
    ),
    color="white",
    intensity=RIM_LIGHT_INTENSITY,
)

plotter.add_light(
    rim_light
)


# =====================================================================
# CAMERA
# =====================================================================

plotter.camera.position = (
    CAMERA_POSITION
)

plotter.camera.focal_point = (
    CAMERA_FOCAL_POINT
)

plotter.camera.up = (
    CAMERA_UP
)

plotter.camera.parallel_projection = False

plotter.camera.view_angle = (
    CAMERA_VIEW_ANGLE
)

plotter.camera.clipping_range = (
    CAMERA_CLIPPING_RANGE
)


# =====================================================================
# RENDER
# =====================================================================

OUT_PNG.parent.mkdir(
    parents=True,
    exist_ok=True,
)

plotter.show(
    screenshot=str(
        OUT_PNG
    ),
    auto_close=True,
)


print(
    f"Saved: {OUT_PNG.resolve()}"
)

print(
    "\nReproducible camera settings:"
)

print(
    f"position       = {CAMERA_POSITION}"
)

print(
    f"focal_point    = {CAMERA_FOCAL_POINT}"
)

print(
    f"up             = {CAMERA_UP}"
)

print(
    f"view_angle     = {CAMERA_VIEW_ANGLE}"
)

print(
    f"clipping_range = {CAMERA_CLIPPING_RANGE}"
)