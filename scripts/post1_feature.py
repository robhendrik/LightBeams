"""
Feature image — helical wavefront / twisted light

A deliberately minimal PyVista rendering:
- monochrome helical surface
- shape revealed primarily by studio-style lighting
- dark background
- no axes, labels, or scientific annotations

Install:
    pip install pyvista

Run:
    python generate_feature_image.py
"""

from pathlib import Path

import numpy as np
import pyvista as pv


# ============================================================
# CONFIGURATION
# ============================================================

# ----- Output -----
OUTPUT_FILE = Path("./outputs/feature_twisted_light.png")
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# ----- Helical wavefront geometry -----
N_TURNS = 4.0               # number of full turns
N_THETA = 500               # resolution along propagation
N_RADIUS = 100              # resolution across sheet

HELIX_LENGTH = 20.0          # total length along propagation axis
INNER_RADIUS = 0.25          # small hole around propagation axis
OUTER_RADIUS = 2.25          # outer radius of wavefront

# Controls how tightly the sheet twists.
# 1.0 = N_TURNS exactly over HELIX_LENGTH
TWIST_FACTOR = 1.0

# Slight radial curvature makes the sheet less "computer flat".
# Set to 0 for a mathematically flat radial sheet.
RADIAL_CURVATURE = 0.08

# ----- Material -----
# Keep material nearly neutral: lighting should provide the 3-D effect.
SURFACE_COLOR = "#d8d5ce"    # warm light grey / ivory

AMBIENT = 0.5
DIFFUSE = 0.88
SPECULAR = 0.22
SPECULAR_POWER = 85

# ----- Background -----
BACKGROUND_COLOR = "#17191c"

# ----- Optional propagation axis -----
SHOW_AXIS = True
AXIS_RADIUS = 0.018
AXIS_COLOR = "#777777"
AXIS_OPACITY = 0.55

# ----- Camera -----
#
# Geometry propagates along +x.
#
CAMERA_POSITION = (10.0, -10.5, 6.0)
CAMERA_FOCAL_POINT = (1.0, 1.0, -0.5)
CAMERA_UP = (0.0, 0.0, 1.0)

CAMERA_ZOOM = 1.05

# ----- Lighting -----
#
# Colors are intentionally almost neutral.
# Geometry should get its appearance from light intensity and direction.
#
KEY_LIGHT_POSITION = (2.0, -7.0, 10.0)
KEY_LIGHT_INTENSITY = 1.0
KEY_LIGHT_COLOR = "#fffaf2"

FILL_LIGHT_POSITION = (-3.0, 7.0, 3.0)
FILL_LIGHT_INTENSITY = 0.28
FILL_LIGHT_COLOR = "#e8edf2"

RIM_LIGHT_POSITION = (-5.0, 1.0, -6.0)
RIM_LIGHT_INTENSITY = 0.38
RIM_LIGHT_COLOR = "#ffffff"

# ----- Rendering -----
MULTISAMPLES = 8
ENABLE_SHADOWS = True

# While developing / adjusting camera
OFF_SCREEN = False

# When producing the final PNG
OFF_SCREEN = True


# ============================================================
# GEOMETRY
# ============================================================

def create_helical_wavefront():
    """
    Create a continuous helical sheet around the x-axis.

    Coordinates:
        x     = propagation direction
        r     = radial coordinate
        phi   = helical phase angle

    For each x, the sheet extends radially from INNER_RADIUS
    to OUTER_RADIUS. As x increases, that radial sheet rotates.
    """

    x = np.linspace(
        -HELIX_LENGTH / 2,
        HELIX_LENGTH / 2,
        N_THETA,
    )

    r = np.linspace(
        INNER_RADIUS,
        OUTER_RADIUS,
        N_RADIUS,
    )

    X, R = np.meshgrid(x, r, indexing="ij")

    phase = (
        2.0
        * np.pi
        * N_TURNS
        * TWIST_FACTOR
        * (X + HELIX_LENGTH / 2)
        / HELIX_LENGTH
    )

    # Give the sheet a very slight curvature across its radius.
    # This helps grazing light reveal the surface without making
    # the geometry obviously warped.
    radial_phase = RADIAL_CURVATURE * (R / OUTER_RADIUS) ** 2

    phi = phase + radial_phase

    Y = R * np.cos(phi)
    Z = R * np.sin(phi)

    grid = pv.StructuredGrid(X, Y, Z)

    return grid.extract_surface()


# ============================================================
# LIGHTING
# ============================================================

def add_light(
    plotter,
    position,
    focal_point,
    intensity,
    color,
):
    """Add a positional studio light."""

    light = pv.Light(
        position=position,
        focal_point=focal_point,
        color=color,
        intensity=intensity,
        positional=True,
    )

    light.cone_angle = 70
    plotter.add_light(light)


# ============================================================
# MAIN
# ============================================================

def main():

    pv.global_theme.multi_samples = MULTISAMPLES

    plotter = pv.Plotter(
        window_size=(IMAGE_WIDTH, IMAGE_HEIGHT),
        off_screen=OFF_SCREEN,
    )

    plotter.set_background(BACKGROUND_COLOR)

    # --------------------------------------------------------
    # Helical wavefront
    # --------------------------------------------------------

    surface = create_helical_wavefront()

    plotter.add_mesh(
        surface,
        color=SURFACE_COLOR,
        smooth_shading=True,
        ambient=AMBIENT,
        diffuse=DIFFUSE,
        specular=SPECULAR,
        specular_power=SPECULAR_POWER,
        show_edges=False,
    )

    # --------------------------------------------------------
    # Propagation axis
    # --------------------------------------------------------

    if SHOW_AXIS:

        axis = pv.Cylinder(
            center=(0.0, 0.0, 0.0),
            direction=(1.0, 0.0, 0.0),
            radius=AXIS_RADIUS,
            height=HELIX_LENGTH * 1.15,
            resolution=64,
        )

        plotter.add_mesh(
            axis,
            color=AXIS_COLOR,
            opacity=AXIS_OPACITY,
            smooth_shading=True,
            ambient=0.15,
            diffuse=0.7,
            specular=0.2,
        )

    # --------------------------------------------------------
    # Lighting
    # --------------------------------------------------------

    plotter.remove_all_lights()

    add_light(
        plotter,
        KEY_LIGHT_POSITION,
        CAMERA_FOCAL_POINT,
        KEY_LIGHT_INTENSITY,
        KEY_LIGHT_COLOR,
    )

    add_light(
        plotter,
        FILL_LIGHT_POSITION,
        CAMERA_FOCAL_POINT,
        FILL_LIGHT_INTENSITY,
        FILL_LIGHT_COLOR,
    )

    add_light(
        plotter,
        RIM_LIGHT_POSITION,
        CAMERA_FOCAL_POINT,
        RIM_LIGHT_INTENSITY,
        RIM_LIGHT_COLOR,
    )

    if ENABLE_SHADOWS:
        plotter.enable_shadows()

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    plotter.camera.position = CAMERA_POSITION
    plotter.camera.focal_point = CAMERA_FOCAL_POINT
    plotter.camera.up = CAMERA_UP

    plotter.camera.zoom(CAMERA_ZOOM)

    # --------------------------------------------------------
    # Render / save
    # --------------------------------------------------------

    plotter.show(
        screenshot=str(OUTPUT_FILE),
        auto_close=True,
    )
    print("Camera:")
    print(plotter.camera_position)
    print(f"Saved: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()