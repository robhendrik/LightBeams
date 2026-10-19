"""Figure 3 prototype: classical two-source intensity correlation vs baseline d.

Two mutually incoherent chaotic point sources a, b at angles +/- theta/2.
Detector 1 fixed at x=0, detector 2 at baseline d.
  E1 = a + b
  E2 = a e^{i phi} + b e^{-i phi},  phi = k d theta / 2 = pi * d   (d in units of lambda/theta)
Intensities I_j = |E_j|^2.  Normalized <I1 I2>/(<I1><I2>) = 1 + cos^2(pi d).
The same random source realization is reused for every d.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle
from PIL import Image
import io

rng = np.random.default_rng(7)

import os

os.chdir("LightBeams")
os.chdir("post3b_stellar_interferometry")
cwd = os.getcwd()
print(cwd)
# ---------- chaotic sources: complex Ornstein-Uhlenbeck (Gaussian, finite coherence time)
N = 240_000
tau_c = 12.0                       # coherence time in samples
rho = np.exp(-1.0 / tau_c)

def chaotic(n):
    w = (rng.normal(size=n) + 1j * rng.normal(size=n)) / np.sqrt(2)
    x = np.empty(n, dtype=complex)
    x[0] = w[0]
    s = np.sqrt(1 - rho**2)
    for i in range(1, n):
        x[i] = rho * x[i - 1] + s * w[i]
    return x

a = chaotic(N)
b = chaotic(N)

def intensities(d):
    phi = np.pi * d
    E1 = a + b
    E2 = a * np.exp(1j * phi) + b * np.exp(-1j * phi)
    return np.abs(E1) ** 2, np.abs(E2) ** 2

def g2(d):
    I1, I2 = intensities(d)
    return np.mean(I1 * I2) / (np.mean(I1) * np.mean(I2))

# ---------- animation parameters
d_max = 2.5
n_frames = 100
d_vals = np.linspace(0, d_max, n_frames)
d_fine = np.linspace(0, d_max, 600)
g2_theory = 1 + np.cos(np.pi * d_fine) ** 2
g2_sim = np.array([g2(d) for d in d_vals])

W = 260                              # samples shown in the traces
t0 = 4000
t = np.arange(W)
scatter_slice = slice(t0, t0 + 1600)

# ---------- style (dark, as Figure 1)
BG = "#0e1621"
FG = "#d7e0ea"
MUTED = "#8fa3b8"
BLUE = "#7cc4f2"
YEL = "#fbbf24"
PANEL = "#2d3b52"
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG,
    "axes.edgecolor": "#5b7088", "font.size": 10,
})

frames = []
for fi, d in enumerate(d_vals):
    I1, I2 = intensities(d)
    m1, m2 = I1.mean(), I2.mean()
    n1, n2 = I1 / m1, I2 / m2          # normalized to mean = 1

    fig = plt.figure(figsize=(11.3, 5.9), dpi=100)
    gs = GridSpec(2, 3, figure=fig, width_ratios=[0.8, 1.35, 1.35],
                  height_ratios=[1, 1], left=0.04, right=0.97, top=0.86,
                  bottom=0.12, wspace=0.32, hspace=0.55)
    fig.suptitle("Two fixed chaotic sources: intensity correlation versus detector separation",
                 fontsize=14, y=0.96)

    # --- geometry
    axg = fig.add_subplot(gs[:, 0])
    axg.set_xlim(0, 10); axg.set_ylim(-5.2, 5.2); axg.axis("off")
    axg.set_title("Geometry (schematic)", fontsize=10, color=FG)
    axg.add_patch(Circle((1.0, 0.45), 0.22, color=YEL))
    axg.add_patch(Circle((1.0, -0.45), 0.22, color=BLUE))
    axg.text(0.35, 0.45, "a", ha="right", va="center", color=YEL)
    axg.text(0.35, -0.45, "b", ha="right", va="center", color=BLUE)
    ydet2 = -4.0 + 8.0 * (d / d_max)       # detector 2 position (exaggerated)
    y1 = -4.0
    axg.plot([9, 9], [-4.4, 4.4], color=PANEL, lw=3, alpha=0.6, zorder=0)
    for yd, lab, col in ((y1, "1", "#c9d6e2"), (ydet2, "2", "#c9d6e2")):
        for src_y, c in ((0.45, YEL), (-0.45, BLUE)):
            axg.plot([1.25, 9], [src_y, yd], color=c, lw=0.7, alpha=0.35)
        axg.add_patch(Circle((9, yd), 0.28, facecolor=BG, edgecolor=col, lw=1.8, zorder=3))
        axg.text(9.55 if lab == "1" else 8.45, yd, lab, va="center",
                 ha="left" if lab == "1" else "right", color=col)
    axg.annotate("", xy=(7.6, ydet2), xytext=(7.6, y1),
                 arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
    if d > 0.08:
        axg.text(7.3, (y1 + ydet2) / 2, "d", ha="right", va="center", color=MUTED, style="italic")
    axg.text(5, -5.0, "Separation exaggerated", ha="center", color=MUTED, fontsize=8)

    # --- traces
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 1])
    for ax, y, lab in ((ax1, n1[t0:t0 + W], "Detector 1"), (ax2, n2[t0:t0 + W], "Detector 2")):
        ax.plot(t, y, color="#c9d6e2", lw=1.1)
        ax.axhline(1, color=MUTED, lw=0.7, ls="--")
        ax.set_ylim(0, 7); ax.set_xlim(0, W)
        ax.set_ylabel("Intensity / mean", fontsize=9)
        ax.set_title(lab, fontsize=10, loc="left", pad=3)
        ax.set_xticks([])
        for s in ax.spines.values(): s.set_color("#5b7088")
    ax2.set_xlabel("Time (arbitrary units)", fontsize=9)
    ax1.set_title("Detector 1 (fixed)", fontsize=10, loc="left", pad=3)
    ax2.set_title("Detector 2 (moving)", fontsize=10, loc="left", pad=3)

    # --- right column top: scatter
    axs = fig.add_subplot(gs[0, 2])
    axs.scatter(n1[scatter_slice], n2[scatter_slice], s=4, color=YEL, alpha=0.45, lw=0)
    axs.set_xlim(0, 7); axs.set_ylim(0, 7)
    axs.plot([0, 7], [0, 7], color=MUTED, lw=0.6, ls=":")
    axs.set_xlabel("I\u2081 / mean", fontsize=9); axs.set_ylabel("I\u2082 / mean", fontsize=9)
    axs.set_title("Each moment: I₂ against I₁", fontsize=10, pad=3)
    axs.set_aspect("equal", adjustable="box")
    for s in axs.spines.values(): s.set_color("#5b7088")

    # --- right column bottom: correlation vs d
    axc = fig.add_subplot(gs[1, 2])
    axc.plot(d_fine, g2_theory, color=BLUE, lw=0, alpha=0)   # keep axis limits fixed
    axc.plot(d_vals[:fi + 1], g2_sim[:fi + 1], color=BLUE, lw=2.2)
    axc.plot(d_vals[fi], g2_sim[fi], "o", color=YEL, ms=7)
    axc.axhline(1, color=MUTED, lw=0.7, ls="--")
    axc.axhline(2, color=MUTED, lw=0.5, ls=":")
    axc.set_xlim(0, d_max); axc.set_ylim(0.8, 2.25)
    axc.set_xlabel("Detector separation d (units of \u03bb/\u03b8)", fontsize=9)
    axc.set_ylabel("\u27e8I\u2081I\u2082\u27e9 / (\u27e8I\u2081\u27e9\u27e8I\u2082\u27e9)", fontsize=9)
    axc.set_title("Correlation from the full record at each d", fontsize=10, pad=3)
    axc.text(d_max * 0.99, 1.04, "no correlation", ha="right", va="bottom", color=MUTED, fontsize=8)
    for s in axc.spines.values(): s.set_color("#5b7088")

    fig.text(0.5, 0.025,
             "Simulation: two independent Gaussian chaotic sources, same random record reused at every d. "
             "Illustrative, not an experimental measurement.",
             ha="center", color=MUTED, fontsize=8)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    frames.append(Image.open(buf).convert("RGB"))

# hold first and last frames
durations = [60] * n_frames
durations[0] = 900
durations[-1] = 1500

small = [f.resize((960, int(960 * f.height / f.width)), Image.LANCZOS) for f in frames]
pal = [f.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in small]
pal[0].save("fig3_hbt_classical.gif", save_all=True, append_images=pal[1:],
            duration=durations, loop=0, optimize=True, disposal=1)
frames[0].save("fig3_frame_d0.png")
frames[n_frames // 5].save("fig3_frame_mid.png")
idx_null = int(np.argmin(np.abs(d_vals - 0.5)))
frames[idx_null].save("fig3_frame_null.png")
frames[-1].save("fig3_frame_last.png")
print("g2 sim range:", g2_sim.min(), g2_sim.max())
print("g2 at d=0, 0.5, 1.0:", g2(0), g2(0.5), g2(1.0))
