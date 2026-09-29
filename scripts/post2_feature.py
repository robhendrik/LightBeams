"""
post2_feature.py

Feature image for "What Is a Photon, Really?"

Creates a cinematic PyVista rendering of quantized energy contours:
concentric thin 3D tubes in a single phase-space plane, with

    r_n ∝ sqrt(n + 1/2)

All tubes have the same cross-sectional radius. The geometry is intentionally
abstract: the plane and axes are not rendered.

Requirements:
    pip install pyvista

Run:
    python post2_feature.py

Output:
    post2_feature.png
"""

from pathlib import Path

import numpy as np
import pyvista as pv


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "post2_feature.png"

# Image
WINDOW_SIZE = (1920, 1080)
BACKGROUND = "#07090d"

# Quantized contours
N_RINGS = 14
RADIUS_SCALE = 1.0
TUBE_RADIUS = 0.055
N_POINTS = 720
TUBE_SIDES = 32

# Material
RING_COLOR = "#d9dde2"
METALLIC = 0.75
ROUGHNESS = 0.24

# Camera: low, oblique view of the common phase-space plane
CAMERA_AZIMUTH_DEG = -38.0
CAMERA_ELEVATION_DEG = 27.0
CAMERA_DISTANCE_FACTOR = 2.35
FOCAL_POINT = (0.0, 0.0, 0.0)

# Lighting
KEY_INTENSITY = 1.05
FILL_INTENSITY = 0.28
RIM_INTENSITY = 0.65

CAMERA_POSITION = [(-8.076385749997101, 1.965264128141952, 9.93676270305235),
                (1.1298852763251623, -0.3007494232884832, -2.0670434002465266),
                (-0.4333741997589547, 0.7647869915800942, -0.4767469564592465)]
# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def energy_radius(n: int) -> float:
    """Return radius proportional to sqrt(n + 1/2)."""
    return RADIUS_SCALE * np.sqrt(n + 0.5)


def make_ring(radius: float) -> pv.PolyData:
    """Create one circular contour and turn it into a 3D tube."""
    theta = np.linspace(0.0, 2.0 * np.pi, N_POINTS, endpoint=False)

    points = np.column_stack(
        (
            radius * np.cos(theta),
            radius * np.sin(theta),
            np.zeros_like(theta),
        )
    )

    # Closed polyline: repeat the first point in the connectivity.
    poly = pv.PolyData()
    poly.points = points
    poly.lines = np.concatenate(
        ([N_POINTS + 1], np.arange(N_POINTS), [0])
    )

    return poly.tube(
        radius=TUBE_RADIUS,
        n_sides=TUBE_SIDES,
        capping=True,
    )


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

def configure_lighting(plotter: pv.Plotter, outer_radius: float) -> None:
    """Add restrained cinematic key, fill, and rim lights."""
    plotter.remove_all_lights()

    key = pv.Light(
        position=(-1.1 * outer_radius, -1.5 * outer_radius, 2.5 * outer_radius),
        focal_point=FOCAL_POINT,
        color="#fff4e8",
        intensity=KEY_INTENSITY,
        positional=True,
        cone_angle=70,
        exponent=8,
    )

    fill = pv.Light(
        position=(2.0 * outer_radius, 0.7 * outer_radius, 1.0 * outer_radius),
        focal_point=FOCAL_POINT,
        color="#b9c8dc",
        intensity=FILL_INTENSITY,
        positional=True,
        cone_angle=80,
        exponent=5,
    )

    rim = pv.Light(
        position=(0.2 * outer_radius, 2.0 * outer_radius, 1.8 * outer_radius),
        focal_point=FOCAL_POINT,
        color="#dce8ff",
        intensity=RIM_INTENSITY,
        positional=True,
        cone_angle=75,
        exponent=6,
    )

    plotter.add_light(key)
    plotter.add_light(fill)
    plotter.add_light(rim)


def configure_camera(plotter: pv.Plotter, outer_radius: float) -> None:

    plotter.camera_position = CAMERA_POSITION

    # Slightly wider lens than PyVista's default perspective.
    plotter.camera.view_angle = 34.0


def main() -> None:
    pv.global_theme.allow_empty_mesh = True

    plotter = pv.Plotter(
       window_size=WINDOW_SIZE,
    )
    plotter.set_background(BACKGROUND)

    radii = [energy_radius(n) for n in range(N_RINGS)]
    outer_radius = radii[-1]

    for radius in radii:
        ring = make_ring(radius)
        plotter.add_mesh(
            ring,
            color=RING_COLOR,
            smooth_shading=True,
            metallic=METALLIC,
            roughness=ROUGHNESS,
            specular=0.7,
            specular_power=30,
        )

    configure_lighting(plotter, outer_radius)
    configure_camera(plotter, outer_radius)

    # High-quality anti-aliasing where supported.
    try:
        plotter.enable_anti_aliasing("ssaa")
    except Exception:
        pass

    def save_image():
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        plotter.screenshot(OUTPUT)
        print(f"Saved: {OUTPUT}")


    plotter.add_key_event("s", save_image)

    def print_camera():
        print("\nCamera position:")
        print(plotter.camera_position)


    plotter.add_key_event("c", print_camera)

    plotter.show()

    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
