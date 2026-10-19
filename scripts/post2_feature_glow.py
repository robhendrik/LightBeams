"""
post2_feature_glow.py

Feature image for "What Is a Photon, Really?"

Adds a post-processed bloom/glow, similar in spirit to the Post 1 feature:
1) render the beauty image with PyVista lighting and shading,
2) render a white silhouette mask of the rings,
3) blur and tint the mask with Pillow,
4) screen-blend the glow back over the beauty image.
"""

from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageFilter


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Adjust to your repo layout if needed.
OUTPUT = Path("./LightBeams/outputs/post2_feature.png")

# Image
WINDOW_SIZE = (1920, 1080)
BACKGROUND = "#07090d"
OFF_SCREEN = True

# Quantized contours
N_RINGS = 14
RADIUS_SCALE = 1.0
TUBE_RADIUS = 0.055
N_POINTS = 720
TUBE_SIDES = 32

# Material
RING_COLOR = "#D4AF37"   # metallic gold
METALLIC = 0.75
ROUGHNESS = 0.24
SPECULAR = 0.7
SPECULAR_POWER = 30

# Camera
CAMERA_POSITION = [
    (-8.076385749997101, 1.965264128141952, 9.93676270305235),
    (1.1298852763251623, -0.3007494232884832, -2.0670434002465266),
    (-0.4333741997589547, 0.7647869915800942, -0.4767469564592465),
]
VIEW_ANGLE = 34.0
FOCAL_POINT = (0.0, 0.0, 0.0)

# Lighting
KEY_INTENSITY = 1.05
FILL_INTENSITY = 0.28
RIM_INTENSITY = 0.65

# Glow -- this is what gives the Post 1 style bloom.
ENABLE_GLOW = True
GLOW_STRENGTH = 0.40
GLOW_BLUR_PX = (10, 34)   # inner / outer blur
INNER_GLOW_COLOR = "#ffd86a"
OUTER_GLOW_COLOR = "#8a6a18"

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def energy_radius(n: int) -> float:
    return RADIUS_SCALE * np.sqrt(n + 0.5)


def make_ring(radius: float) -> pv.PolyData:
    theta = np.linspace(0.0, 2.0 * np.pi, N_POINTS, endpoint=False)
    points = np.column_stack(
        (
            radius * np.cos(theta),
            radius * np.sin(theta),
            np.zeros_like(theta),
        )
    )

    poly = pv.PolyData()
    poly.points = points
    poly.lines = np.concatenate(([N_POINTS + 1], np.arange(N_POINTS), [0]))

    tube = poly.tube(radius=TUBE_RADIUS, n_sides=TUBE_SIDES, capping=True)
    return tube.compute_normals(auto_orient_normals=True, split_vertices=False)


# ---------------------------------------------------------------------------
# Scene setup
# ---------------------------------------------------------------------------

def configure_lighting(plotter: pv.Plotter, outer_radius: float) -> None:
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


def configure_camera(plotter: pv.Plotter) -> None:
    plotter.camera_position = CAMERA_POSITION
    plotter.camera.view_angle = VIEW_ANGLE


# ---------------------------------------------------------------------------
# Rendering and glow
# ---------------------------------------------------------------------------

def build_plotter() -> pv.Plotter:
    plotter = pv.Plotter(window_size=WINDOW_SIZE, off_screen=OFF_SCREEN)
    plotter.set_background(BACKGROUND)
    return plotter


def add_scene_meshes(plotter: pv.Plotter, radii: list[float], mask: bool = False) -> None:
    for radius in radii:
        ring = make_ring(radius)
        if mask:
            plotter.add_mesh(ring, color="white", lighting=False, smooth_shading=True)
        else:
            plotter.add_mesh(
                ring,
                color=RING_COLOR,
                smooth_shading=True,
                metallic=METALLIC,
                roughness=ROUGHNESS,
                specular=SPECULAR,
                specular_power=SPECULAR_POWER,
            )


def render_scene(radii: list[float], outer_radius: float, mask: bool = False) -> Image.Image:
    plotter = build_plotter()
    if mask:
        plotter.set_background("black")
    add_scene_meshes(plotter, radii, mask=mask)
    if not mask:
        configure_lighting(plotter, outer_radius)
    else:
        plotter.remove_all_lights()
    configure_camera(plotter)

    try:
        plotter.enable_anti_aliasing("ssaa")
    except Exception:
        pass

    plotter.render()
    pixels = plotter.screenshot(return_img=True)
    plotter.close()
    return Image.fromarray(pixels[:, :, :3]).convert("RGB")


def screen_blend(base: Image.Image, glow: Image.Image, strength: float) -> Image.Image:
    a = np.asarray(base, dtype=np.float32) / 255.0
    b = np.asarray(glow, dtype=np.float32) / 255.0
    result = 1.0 - (1.0 - a) * (1.0 - strength * b)
    return Image.fromarray(np.uint8(np.clip(result * 255, 0, 255)))


def add_glow(beauty: Image.Image, silhouette: Image.Image) -> Image.Image:
    mask = silhouette.convert("L")
    inner = mask.filter(ImageFilter.GaussianBlur(GLOW_BLUR_PX[0]))
    outer = mask.filter(ImageFilter.GaussianBlur(GLOW_BLUR_PX[1]))

    black = Image.new("RGB", beauty.size, "black")
    inner_rgb = Image.new("RGB", beauty.size, INNER_GLOW_COLOR)
    outer_rgb = Image.new("RGB", beauty.size, OUTER_GLOW_COLOR)

    inner_col = Image.composite(inner_rgb, black, inner)
    outer_col = Image.composite(outer_rgb, black, outer)
    glow = screen_blend(outer_col, inner_col, 0.9)
    return screen_blend(beauty, glow, GLOW_STRENGTH)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    pv.global_theme.allow_empty_mesh = True
    pv.global_theme.multi_samples = 8

    radii = [energy_radius(n) for n in range(N_RINGS)]
    outer_radius = radii[-1]

    beauty = render_scene(radii, outer_radius, mask=False)
    if ENABLE_GLOW:
        silhouette = render_scene(radii, outer_radius, mask=True)
        beauty = add_glow(beauty, silhouette)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    beauty.save(OUTPUT)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
