"""Render a shaded, luminous helical tube for LightBeams Post 1.

The tube is genuine 3-D geometry (PyVista/VTK): directional studio lights,
per-pixel smooth normals, and specular reflections create its roundness.
A restrained glow is composited *after* rendering so it does not flatten the
lighting on the tube itself.

Install: pip install numpy pyvista pillow
Run:     python post1_feature_luminous_helix_3d.py
"""

from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageFilter


# Keep this path exactly as requested.
OUTPUT_FILE = Path("./LightBeams/outputs/feature_twisted_light_tube.png")
IMAGE_WIDTH, IMAGE_HEIGHT = 1920, 1080

# Geometry: a helical tube around the x-axis.
N_TURNS = 6.0
N_POINTS = 1800
HELIX_LENGTH = 25.0
HELIX_RADIUS = 2.05
TUBE_RADIUS = 0.28              # Increase for an obviously cylindrical surface
TUBE_SIDES = 64
PHASE_OFFSET = 0.10 * np.pi

BACKGROUND_COLOR = "#000004"    # Black from the HG intensity figure
TUBE_COLOR = "#daf419"          # Orange body; directional highlights become gold

# Camera: oblique angle emphasizing crossing of front and back coils.
CAMERA_POSITION = (16.0, -18.0, 11.0)
CAMERA_FOCAL_POINT = (3.0, 1.5, -1.5)
CAMERA_ZOOM = 1.45
CAMERA_UP = (0.0, 0.0, 1.0)


# Diffuse/specular studio lighting, not an almost-unlit emissive surface.
AMBIENT = 0.17
DIFFUSE = 0.80
SPECULAR = 0.95
SPECULAR_POWER = 75

# Post-process halo in colors of the HG figure. Keep modest for 3-D definition.
ENABLE_GLOW = True
GLOW_STRENGTH = 0.95            # 0 removes glow; ~0.3-0.7 is restrained
GLOW_BLUR_PX = (16, 46)         # inner + outer bloom radii at 1920 x 1080

OFF_SCREEN = True


def create_helix_tube() -> pv.PolyData:
    """Create a smoothly shaded tube around a sampled helical centreline."""
    x = np.linspace(-HELIX_LENGTH / 2, HELIX_LENGTH / 2, N_POINTS)
    theta = (2 * np.pi * N_TURNS * (x + HELIX_LENGTH / 2)
             / HELIX_LENGTH + PHASE_OFFSET)
    points = np.column_stack((x, HELIX_RADIUS * np.cos(theta),
                              HELIX_RADIUS * np.sin(theta)))
    curve = pv.lines_from_points(points, close=False)
    tube = curve.tube(radius=TUBE_RADIUS, n_sides=TUBE_SIDES, capping=True)
    return tube.compute_normals(auto_orient_normals=True, split_vertices=False)


def add_studio_lights(plotter: pv.Plotter) -> None:
    """Light tube from different directions to give it readable highlights."""
    # Three lights at different positions provide bright and dark sides.
    settings = [
        ((-4, -10, 16), "#fff3ad", 1.20),  # warm key (top/front)
        ((6, 8, 3), "#fda34b", 0.66),     # amber fill (back)
        ((-10, 2, -10), "#aa45e2", 0.90), # purple rim (below/back)
    ]
    for position, color, intensity in settings:
        light = pv.Light(
            position=position, focal_point=(0, 0, 0),
            color=color, intensity=intensity, positional=False,
        )
        plotter.add_light(light)


def setup_camera(plotter: pv.Plotter) -> None:
    plotter.camera.position = CAMERA_POSITION
    plotter.camera.focal_point = CAMERA_FOCAL_POINT
    plotter.camera.up = CAMERA_UP
    plotter.camera.zoom(CAMERA_ZOOM)


def render(tube: pv.PolyData, mask: bool = False) -> Image.Image:
    """Render either a 3-D lit tube or a white silhouette for the halo."""
    plotter = pv.Plotter(
        window_size=(IMAGE_WIDTH, IMAGE_HEIGHT),
        off_screen=OFF_SCREEN,
    )
    plotter.set_background("#000000" if mask else BACKGROUND_COLOR)
    plotter.remove_all_lights()

    if mask:
        plotter.add_mesh(tube, color="white", lighting=False,
                         smooth_shading=True)
    else:
        add_studio_lights(plotter)
        plotter.add_mesh(
            tube,
            color=TUBE_COLOR,
            smooth_shading=True,
            lighting=True,
            ambient=AMBIENT,
            diffuse=DIFFUSE,
            specular=SPECULAR,
            specular_power=SPECULAR_POWER,
            show_edges=False,
        )

    setup_camera(plotter)
    plotter.render()
    pixels = plotter.screenshot(return_img=True)
    plotter.close()
    return Image.fromarray(pixels[:, :, :3]).convert("RGB")


def screen_blend(base: Image.Image, glow: Image.Image, strength: float) -> Image.Image:
    """Screen-blend light onto an existing RGB image without hiding shading."""
    a = np.asarray(base, dtype=np.float32) / 255.0
    b = np.asarray(glow, dtype=np.float32) / 255.0
    result = 1.0 - (1.0 - a) * (1.0 - strength * b)
    return Image.fromarray(np.uint8(np.clip(result * 255, 0, 255)))


def add_glow(beauty: Image.Image, silhouette: Image.Image) -> Image.Image:
    """Bloom around the tube using orange near glow and purple distant glow."""
    mask = silhouette.convert("L")
    outer = mask.filter(ImageFilter.GaussianBlur(GLOW_BLUR_PX[1]))
    inner = mask.filter(ImageFilter.GaussianBlur(GLOW_BLUR_PX[0]))

    # Build colored glow on a black canvas, then screen onto the lit image.
    outer_rgb = Image.new("RGB", beauty.size, "#68258e")
    inner_rgb = Image.new("RGB", beauty.size, "#ed5621")
    black = Image.new("RGB", beauty.size, "black")
    purple = Image.composite(outer_rgb, black, outer)
    orange = Image.composite(inner_rgb, black, inner)
    glow = screen_blend(purple, orange, 0.9)
    return screen_blend(beauty, glow, GLOW_STRENGTH)


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pv.global_theme.multi_samples = 8

    tube = create_helix_tube()
    beauty = render(tube)
    if ENABLE_GLOW:
        silhouette = render(tube, mask=True)
        beauty = add_glow(beauty, silhouette)

    beauty.save(OUTPUT_FILE)
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
