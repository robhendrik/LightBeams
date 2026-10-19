"""Figure 4 prototype: two indistinguishable alternatives for one photon from each of two
independent sources.

Sources a, b (angular separation theta), detectors 1, 2 (baseline d).
  direct alternative:    a -> 1 and b -> 2
  exchanged alternative: a -> 2 and b -> 1
For bosons the two probability amplitudes add. With equal magnitudes the relative phase is
  dphi = k d theta = 2 pi d      (d in units of lambda/theta, as in Figure 3)
and the coincidence probability for this a-b pair, relative to independent (distinguishable)
photons, is
  |A1 + A2|^2 / (|A1|^2 + |A2|^2) = 1 + cos(dphi) = 2 cos^2(dphi / 2).
Only the a-b pair contribution is shown. Same-source pairs, which add the flat background
that keeps the full thermal-light g2 of Figure 3 at 1 (not 0) at the null, are not drawn.
"""
import io
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Arc
from matplotlib.lines import Line2D
from PIL import Image
import os

os.chdir("LightBeams")
os.chdir("post3b_stellar_interferometry")
cwd = os.getcwd()
print(cwd)
# ---------- output location (change these)
OUT_DIR = Path(".")
GIF_NAME = "fig4_two_alternatives.gif"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- animation parameters: one full period, d in units of lambda/theta
n_frames = 81
d_vals = np.linspace(0.0, 1.0, n_frames)       # index 20 -> d=0.25, index 40 -> d=0.5


def ratio(d):
    return 1.0 + np.cos(2.0 * np.pi * d)


# ---------- style (dark, as Figures 1 and 3)
BG = "#0e1621"
FG = "#d7e0ea"
MUTED = "#8fa3b8"
BLUE = "#7cc4f2"
YEL = "#fbbf24"
PANEL = "#2d3b52"
LIGHT = "#c9d6e2"
GREEN = "#6ee7a8"
DASH = (0, (4, 3))
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG,
    "axes.edgecolor": "#5b7088", "font.size": 10,
})


def arrow(ax, x0, y0, x1, y1, color, ls="-", lw=2.6):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=3)
    v = np.array([x1 - x0, y1 - y0])
    length = np.hypot(*v)
    if length > 0.12:
        u = v / length
        ax.annotate("", xy=(x1, y1), xytext=(x1 - 0.14 * u[0], y1 - 0.14 * u[1]),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0,
                                    mutation_scale=16, shrinkA=0, shrinkB=0), zorder=4)


frames = []
for fi, d in enumerate(d_vals):
    phi = 2.0 * np.pi * d

    fig = plt.figure(figsize=(11.3, 5.9), dpi=100)
    gs = GridSpec(1, 3, figure=fig, width_ratios=[0.9, 1.1, 1.1], left=0.04, right=0.97,
                  top=0.82, bottom=0.14, wspace=0.28)
    fig.suptitle("One photon from each source: two indistinguishable ways to be detected",
                 fontsize=14, y=0.95)

    # ---------------- geometry
    axg = fig.add_subplot(gs[0])
    axg.set_xlim(0, 11.4); axg.set_ylim(-6.9, 5.2)
    axg.set_aspect("equal", adjustable="box"); axg.axis("off")
    axg.set_title("The two alternatives (schematic)", fontsize=10)
    ya, yb = 0.45, -0.45
    axg.add_patch(Circle((1.0, ya), 0.22, color=YEL))
    axg.add_patch(Circle((1.0, yb), 0.22, color=BLUE))
    axg.text(0.5, ya, "a", ha="right", va="center", color=YEL)
    axg.text(0.5, yb, "b", ha="right", va="center", color=BLUE)
    y1 = -4.0
    y2 = -4.0 + 8.0 * d
    axg.plot([9, 9], [-4.4, 4.4], color=PANEL, lw=3, alpha=0.6, zorder=0)
    # direct (solid): a->1, b->2 ; exchanged (dashed): a->2, b->1
    for sy, c, yd, ls in ((ya, YEL, y1, "-"), (yb, BLUE, y2, "-"),
                          (ya, YEL, y2, DASH), (yb, BLUE, y1, DASH)):
        axg.plot([1.25, 9], [sy, yd], color=c, lw=1.5, alpha=0.9, ls=ls, zorder=2)
    for yd, lab, dy in ((y1, "1", -0.85), (y2, "2", 0.85)):
        axg.add_patch(Circle((9, yd), 0.3, facecolor=BG, edgecolor=LIGHT, lw=1.8, zorder=3))
        axg.text(9, yd + dy, lab, va="center", ha="center", color=LIGHT)
    axg.annotate("", xy=(10.3, y2), xytext=(10.3, y1),
                 arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
    if d > 0.04:
        axg.text(10.7, (y1 + y2) / 2, "d", ha="left", va="center", color=MUTED, style="italic")
    # legend
    axg.plot([0.4, 1.9], [-5.5, -5.5], color=LIGHT, lw=1.6)
    axg.text(2.2, -5.5, "a→1 and b→2", va="center", ha="left", color=FG, fontsize=8.5)
    axg.plot([0.4, 1.9], [-6.3, -6.3], color=LIGHT, lw=1.6, ls=DASH)
    axg.text(2.2, -6.3, "a→2 and b→1", va="center", ha="left", color=FG, fontsize=8.5)

    # ---------------- phasors
    axp = fig.add_subplot(gs[1])
    axp.set_xlim(-0.6, 2.6); axp.set_ylim(-1.5, 1.5)
    axp.set_aspect("equal", adjustable="box"); axp.axis("off")
    axp.set_title("Adding the two amplitudes", fontsize=10)
    axp.add_patch(Circle((1, 0), 1, fill=False, ec="#3a4a60", ls=":", lw=1))
    axp.plot(0, 0, "o", color=MUTED, ms=3, zorder=5)
    tipx, tipy = 1 + np.cos(phi), np.sin(phi)
    arrow(axp, 0, 0, 1, 0, LIGHT)
    arrow(axp, 1, 0, tipx, tipy, LIGHT, ls=(0, (3, 2)))
    arrow(axp, 0, 0, tipx, tipy, GREEN, lw=3.4)
    if np.hypot(tipx, tipy) < 0.12:
        axp.plot(0, 0, "o", color=GREEN, ms=8, zorder=6)
    if phi > 0.03:
        axp.add_patch(Arc((1, 0), 0.7, 0.7, theta1=0, theta2=np.degrees(phi), color=MUTED, lw=1.2))
    axp.text(0.5, 0.99, f"Δφ = kdθ = {phi / np.pi:.2f} π", transform=axp.transAxes,
             ha="center", va="top", fontsize=11, color=FG)
    handles = [Line2D([0], [0], color=LIGHT, lw=2.4, label="direct"),
               Line2D([0], [0], color=LIGHT, lw=2.4, ls=(0, (3, 2)), label="exchanged"),
               Line2D([0], [0], color=GREEN, lw=3.2, label="sum")]
    axp.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=3,
               frameon=False, fontsize=8.5, labelcolor=FG, handlelength=1.8, columnspacing=1.3)

    # ---------------- curve for a-b pairs only
    axc = fig.add_subplot(gs[2])
    axc.plot(d_vals[:fi + 1], ratio(d_vals[:fi + 1]), color=GREEN, lw=2.4)
    axc.plot(d, ratio(d), "o", color=GREEN, mec="white", mew=1.2, ms=8, zorder=5)
    axc.axhline(1, color=MUTED, lw=0.8, ls="--")
    axc.axvline(0.25, color=MUTED, lw=0.6, ls=":")
    axc.axvline(0.5, color=MUTED, lw=0.6, ls=":")
    axc.set_xlim(0, 1); axc.set_ylim(-0.1, 2.25)
    axc.set_xlabel("Detector separation d (units of λ/θ)", fontsize=9)
    axc.set_ylabel("Coincidence rate\nrelative to independent photons", fontsize=9)
    axc.set_title("Result for a–b pairs only", fontsize=10, pad=6)
    axc.text(0.99, 1.04, "independent photons", ha="right", va="bottom", color=MUTED, fontsize=8)
    axc.text(0.25, 2.2, "sign flip", ha="center", va="top", color=MUTED, fontsize=8)
    axc.text(0.5, 2.2, "full cancellation", ha="center", va="top", color=MUTED, fontsize=8)
    for s in axc.spines.values():
        s.set_color("#5b7088")

    fig.text(0.5, 0.035,
             "Schematic. Equal-brightness point sources, equal-size amplitudes; for bosons the amplitudes add. "
             "Same-source pairs not shown. Detector separation exaggerated.",
             ha="center", color=MUTED, fontsize=8)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    frames.append(Image.open(buf).convert("RGB"))

# ---------- timing: hold the start, the sign flip and the cancellation
durations = [55] * n_frames
durations[0] = 900
durations[20] = 700      # d = 0.25
durations[40] = 1300     # d = 0.5
durations[-1] = 1500

small = [f.resize((960, int(960 * f.height / f.width)), Image.LANCZOS) for f in frames]
pal = [f.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in small]
gif_path = OUT_DIR / GIF_NAME
pal[0].save(gif_path, save_all=True, append_images=pal[1:], duration=durations,
            loop=0, optimize=True, disposal=1)
frames[0].save(OUT_DIR / "fig4_frame_d0.png")
frames[20].save(OUT_DIR / "fig4_frame_d025.png")
frames[40].save(OUT_DIR / "fig4_frame_d05.png")
frames[60].save(OUT_DIR / "fig4_frame_d075.png")
print("Saved:", gif_path.resolve())
print("ratio at d=0, 0.25, 0.5:", ratio(0.0), ratio(0.25), ratio(0.5))
