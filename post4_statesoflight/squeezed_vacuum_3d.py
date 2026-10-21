"""
Squeezed vacuum as a 3D surface (Wigner function) for the feature image.

Run:   python squeezed_vacuum_3d.py
       (headless server: xvfb-run -a python squeezed_vacuum_3d.py)
Needs: pip install pyvista numpy

The soft shadow is computed by ray-marching the height field towards an area
light and baked into the floor colours. This avoids the blocky shadow maps
that VTK's real-time shadow pass gives on a large floor.
"""
import numpy as np
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap

# ----------------------------------------------------------------- parameters
R_SQUEEZE = 0.8          # squeezing parameter r (noise reduced by e^{-2r})
TILT_DEG = 35.0          # orientation of the narrow axis in the X-P plane
L = 3.2                  # half-width of the phase-space patch
N = 700                  # surface resolution
HEIGHT = 1.0             # visual height of the Wigner peak
OUT = "./LightBeams/post4_statesoflight/feature_squeezed_vacuum.png"
SIZE = (2400, 1350)      # 16:9 feature image

LIGHT_POS = np.array([-4.0, 3.0, 4.2])     # key light (casts the shadow)
LIGHT_SOFTNESS = 0.16                       # penumbra size (radians)
SHADOW_STRENGTH = 0.85

# ------------------------------------------------ Wigner function, pure state
# Convention: vacuum has Delta X = Delta P = 1/2; the peak height is the same
# for vacuum and squeezed vacuum because both are pure states.
sx = 0.5 * np.exp(-R_SQUEEZE)            # narrow axis
sp = 0.5 * np.exp(+R_SQUEEZE)            # wide axis
th = np.deg2rad(TILT_DEG)
c_t, s_t = np.cos(th), np.sin(th)


def wigner(x, y):
    u = x * c_t + y * s_t
    v = -x * s_t + y * c_t
    return np.exp(-u**2 / (2 * sx**2) - v**2 / (2 * sp**2))


xs = np.linspace(-L, L, N)
X, Y = np.meshgrid(xs, xs)
Z = HEIGHT * wigner(X, Y)

surf = pv.StructuredGrid(X, Y, Z)
surf["height"] = Z.ravel(order="F")
surf = surf.extract_surface(algorithm="dataset_surface")
surf_full = surf
surf = surf.clip_scalar(scalars="height", value=0.10, invert=False)   # trim flat skirt so the floor shows

cmap = LinearSegmentedColormap.from_list(
    "qvac", ["#0a1f3d", "#123f7a", "#1f6fb5", "#3aa0d8", "#8fd3f2", "#f4fbff"])

# -------------------------------------------------- baked soft shadow on floor
floor_z = -0.02
R_FLOOR = 3.0
disc = pv.Disc(center=(0, 0, floor_z), inner=0.0, outer=R_FLOOR,
               normal=(0, 0, 1), r_res=140, c_res=220)
FX, FY = disc.points[:, 0], disc.points[:, 1]

rng = np.random.default_rng(3)
base = LIGHT_POS - np.array([0, 0, 0.3])
base = base / np.linalg.norm(base)
n_samples, n_steps = 24, 40
shadow = np.zeros_like(FX)
for _ in range(n_samples):
    d = base + rng.normal(scale=LIGHT_SOFTNESS, size=3)
    d /= np.linalg.norm(d)
    occluded = np.zeros_like(FX, dtype=bool)
    for s_ in np.linspace(0.04, 5.0, n_steps):
        qx, qy, qz = FX + s_ * d[0], FY + s_ * d[1], floor_z + s_ * d[2]
        occluded |= (HEIGHT * wigner(qx, qy)) > qz
    shadow += occluded
shadow /= n_samples                         # 0 = lit, 1 = fully shadowed

rad = np.sqrt(FX**2 + FY**2) / R_FLOOR
fade = np.clip(1.0 - rad**2, 0, 1) ** 1.2   # floor fades into the background
glow = np.exp(-((FX * c_t + FY * s_t) ** 2 / (2 * (1.8 * sx) ** 2)
                + (-FX * s_t + FY * c_t) ** 2 / (2 * (1.5 * sp) ** 2)))

BG_TONE = 0.10   # floor edge tone, matches the background gradient
disc["tone"] = (BG_TONE
                + fade * (0.50 * (1 - shadow) + 0.30 * glow * (1 - 0.6 * shadow))
                - SHADOW_STRENGTH * 0.2 * fade * shadow)
disc["fade"] = fade
floor_cmap = LinearSegmentedColormap.from_list(
    "floor", [(0.0, "#050b16"), (0.11, "#0f1b33"), (0.45, "#24467a"), (1.0, "#4a86c4")])

# ------------------------------------------------------------------- scene
pl = pv.Plotter(off_screen=True, window_size=SIZE, lighting="none")
pl.set_background("#050b16", top="#17294a")

pl.add_mesh(disc, scalars="tone", cmap=floor_cmap, clim=(0, 0.9),
            smooth_shading=False, ambient=1.0,
            diffuse=0.0, specular=0.0, show_scalar_bar=False)

pl.add_mesh(surf, scalars="height", cmap=cmap, clim=(0, HEIGHT),
            smooth_shading=True, specular=0.55, specular_power=35,
            ambient=0.18, diffuse=0.85, show_scalar_bar=False)

# contour lines of constant probability on the surface
for level, op in zip([0.12, 0.30, 0.55, 0.80], [0.22, 0.28, 0.34, 0.40]):
    c = surf_full.contour(isosurfaces=[level * HEIGHT], scalars="height")
    if c.n_points:
        pl.add_mesh(c.tube(radius=0.007, n_sides=16), color="#d9f1ff", opacity=op,
                    smooth_shading=True, ambient=0.7)

SHOW_FLOOR_REFERENCE = False   # gold vacuum circle, white ellipse, axes (hidden under the peak)
if SHOW_FLOOR_REFERENCE:
    # floor reference: ordinary vacuum (gold circle) and the squeezed ellipse (white)
    t = np.linspace(0, 2 * np.pi, 400)
    zf = floor_z + 0.008
    circle = np.column_stack([0.5 * np.cos(t), 0.5 * np.sin(t), np.full_like(t, zf)])
    ex, ey = sx * np.cos(t), sp * np.sin(t)
    ellipse = np.column_stack([ex * c_t - ey * s_t, ex * s_t + ey * c_t, np.full_like(t, zf)])
    pl.add_mesh(pv.Spline(circle, 400).tube(radius=0.012, n_sides=24), color="#f2c14e",
                ambient=0.9, opacity=0.95)
    pl.add_mesh(pv.Spline(ellipse, 400).tube(radius=0.014, n_sides=24), color="#ffffff",
                ambient=0.9, opacity=0.98)

    # phase-space axes on the floor
    for p0, p1 in [((-2.2, 0, zf), (2.2, 0, zf)), ((0, -2.2, zf), (0, 2.2, zf))]:
        pl.add_mesh(pv.Line(p0, p1).tube(radius=0.004), color="#5f84b8",
                    opacity=0.55, ambient=0.9)


# --------------------------------------------------------------- lighting
for pos, col, inten in [(tuple(LIGHT_POS), "#fff1dc", 1.0),     # key
                        ((5.0, 2.5, 2.5), "#8fb8ff", 0.35),     # cool fill
                        ((1.0, 5.0, 2.2), "#9fe0ff", 0.45)]:    # rim
    pl.add_light(pv.Light(position=pos, focal_point=(0, 0, 0.3), color=col,
                          intensity=inten, light_type="scene light"))

pl.enable_depth_peeling(number_of_peels=6)
pl.enable_anti_aliasing("ssaa")

# ----------------------------------------------------------------- camera
az = np.deg2rad(TILT_DEG - 22)
pl.camera_position = [(7.0*np.cos(az), 7.0*np.sin(az), 4.0), (0.0, 0.0, 0.25), (0, 0, 1)]
pl.camera.zoom(1.0)

pl.screenshot(OUT)
print("saved", OUT)
