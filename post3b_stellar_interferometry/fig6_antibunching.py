"""Figure 6 - antibunching, simple version (animated GIF, dark style, same recipe as Fig 3).

One source only: a single driven two-level atom (resonance fluorescence).
Static geometry: atom, beam splitter, two detectors, a delay line on detector 2, a correlator.
Animated variable: the delay tau applied to detector 2.
  panel B: the two click records, detector 2 shifted by tau; clicks that line up are highlighted
  panel C: coincidence rate relative to independent clicks, versus tau,
           computed from the full simulated record at each tau (like Fig 3).
Illustrative: ideal single atom, every photon counted.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
from PIL import Image
import os

os.chdir("LightBeams")
os.chdir("post3b_stellar_interferometry")
cwd = os.getcwd()
print(cwd)
OUT_DIR = Path(".")
GIF_NAME = "fig6_antibunching.gif"

BG, FG, MUTED = "#0e1621", "#d7e0ea", "#8fa3b8"
BLUE, YEL, PANEL = "#7cc4f2", "#fbbf24", "#2d3b52"
GREEN = "#4ade80"

# ---------------- physics: one driven two-level atom ----------------
A = 1 / 16.3                    # Einstein A, sodium 3P (per ns)
OMEGA = 2.25 * A                # Rabi frequency (Kimble et al.: 2-2.5 A)
RATE = A * (OMEGA**2 / 2) / (OMEGA**2 + A**2 / 2)
T_TOTAL = 4.0e6                 # ns of simulated record
SIG = 1.0                       # detector pulse width (ns, Gaussian)
W = 2.0 * SIG                   # overlap threshold used only for the green highlight (ns)
TAU_MAX = 100.0
rng = np.random.default_rng(11)

dtau, tmax = 0.02, 900.0
M = np.array([[0, -0.5j * OMEGA], [-0.5j * OMEGA, -0.5 * A]])
w_, V = np.linalg.eig(M)
tau_grid = np.arange(0, tmax, dtau)
c0 = np.linalg.inv(V) @ np.array([1, 0], dtype=complex)
amp = (V[None] * np.exp(w_[None] * tau_grid[:, None])[:, None, :]) @ c0
surv = np.abs(amp[:, 0]) ** 2 + np.abs(amp[:, 1]) ** 2
cdf = 1 - surv
waits = np.interp(rng.random(int(T_TOTAL * RATE * 1.05)) * cdf[-1], cdf, tau_grid)
t = np.cumsum(waits)
t = t[t < T_TOTAL]
to1 = rng.random(t.size) < 0.5            # beam splitter: detector 1 or 2
s, q = t[to1], t[~to1]                    # click times on detectors 1 and 2

# all delays d = t2 - t1 within +-(TAU_MAX + W + 2)
lim = TAU_MAX + W + 2
lo, hi = np.searchsorted(q, s - lim), np.searchsorted(q, s + lim)
n = hi - lo
off = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
delays = np.sort(q[np.repeat(lo, n) + off] - np.repeat(s, n))

SD = np.sqrt(2) * SIG           # pulse*pulse overlap is a Gaussian of this width
def g2_at(tau):
    i0, i1 = np.searchsorted(delays, tau - 6 * SD), np.searchsorted(delays, tau + 6 * SD)
    d = delays[i0:i1]
    kk = np.exp(-(d - tau) ** 2 / (2 * SD**2)) / (np.sqrt(2 * np.pi) * SD)
    return T_TOTAL * kk.sum() / (s.size * q.size)

taus = np.arange(0, TAU_MAX + 1e-9, 1.25)
g2_meas = np.array([g2_at(x) for x in taus])
tt = np.linspace(0, TAU_MAX, 400)
lam = np.sqrt(OMEGA**2 - A**2 / 16)
g2_theory = 1 - np.exp(-0.75 * A * tt) * (np.cos(lam * tt) + 0.75 * A / lam * np.sin(lam * tt))
gaps = np.diff(t)
P5_atom = (gaps < 5).mean(); P5_rand = 1 - np.exp(-RATE * 5)
P12_atom = (gaps < 12).mean(); P12_rand = 1 - np.exp(-RATE * 12)
print('spacings <5 ns: atom %.3f random %.3f; <12 ns: atom %.3f random %.3f' % (P5_atom, P5_rand, P12_atom, P12_rand))
print("g2 at tau=0: %.3f  peak %.2f  late %.2f" % (g2_meas[0], g2_meas.max(), g2_meas[-8:].mean()))

# ---- choose a typical 500 ns display window (not cherry-picked: median coincidence count) ----
WIN = 500.0
def coincidences(lo_t, tau):
    s_w = s[(s >= lo_t) & (s < lo_t + WIN)]
    out = []
    for si in s_w:
        j = np.searchsorted(q, si + tau - W), np.searchsorted(q, si + tau + W)
        out += [si for _ in range(j[1] - j[0])]
    return out
cands = np.arange(2000, 2000 + 40 * WIN, WIN)
totals = np.array([sum(len(coincidences(c, x)) for x in taus) for c in cands])
T0 = cands[np.argsort(totals)[len(totals) // 2]]
print("display window starts at %.0f ns (median of %d candidates, total %d, range %d-%d)" %
      (T0, len(cands), totals[np.argsort(totals)[len(totals) // 2]], totals.min(), totals.max()))
s_win = s[(s >= T0 - 5) & (s < T0 + WIN + 5)]
q_win = q[(q >= T0 - 5) & (q < T0 + WIN + TAU_MAX + 10)]

# ---------------- figure ----------------
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": FG})
fig = plt.figure(figsize=(10, 6), dpi=96, facecolor=BG)
axA = fig.add_axes([0.015, 0.50, 0.46, 0.43]); axA.set_facecolor(BG)
axB = fig.add_axes([0.60, 0.575, 0.38, 0.31]); axB.set_facecolor(BG)
axC = fig.add_axes([0.075, 0.095, 0.905, 0.33]); axC.set_facecolor(BG)
for a in (axB, axC):
    for sp in a.spines.values():
        sp.set_color(PANEL)
    a.tick_params(colors=MUTED, labelsize=9, length=3)

fig.text(0.015, 0.955, "A   One atom, two detectors, one delay", color=FG, fontsize=11.5, weight="bold", va="center")
fig.text(0.50, 0.955, "B   Detector signals", color=FG, fontsize=11.5, weight="bold", va="center")
fig.text(0.015, 0.455, "C   Correlation of the two signals versus the delay τ", color=FG, fontsize=11.5, weight="bold", va="center")

# ---- A: static geometry ----
axA.set_xlim(0, 11.2); axA.set_ylim(0.2, 5.9); axA.set_aspect("equal"); axA.axis("off")
atom = np.array([0.9, 3.0]); BS = np.array([3.6, 3.0])
D1 = np.array([5.7, 4.8]); D2 = np.array([5.7, 1.2])
line = dict(color=PANEL, lw=1.8, zorder=1)
axA.plot([atom[0], BS[0]], [atom[1], BS[1]], **line)
axA.plot([BS[0], D1[0]], [BS[1], D1[1]], **line)
axA.plot([BS[0], D2[0]], [BS[1], D2[1]], **line)
axA.add_patch(Circle(atom, 0.42, fc=GREEN, ec="none", zorder=3))
axA.text(atom[0], atom[1] + 0.8, "one atom", ha="center", color=GREEN, fontsize=9.5)
axA.annotate("", xy=(atom[0], atom[1] - 0.55), xytext=(atom[0], 0.75),
             arrowprops=dict(arrowstyle="-|>", color=YEL, lw=1.6, alpha=0.7))
axA.text(atom[0] + 0.25, 1.3, "laser", color=YEL, fontsize=9, alpha=0.85, va="center")
axA.add_patch(Polygon([BS + [0, .3], BS + [.3, 0], BS + [0, -.3], BS + [-.3, 0]], fc=PANEL, ec=MUTED, lw=1, zorder=2))
axA.text(3.25, 2.3, "beam splitter", color=MUTED, fontsize=8.5, ha="right", va="center")
for p, col, lab in ((D1, BLUE, "1"), (D2, YEL, "2")):
    axA.add_patch(Circle(p, 0.5, fc=BG, ec=col, lw=2, zorder=3))
    axA.text(*p, lab, color=col, ha="center", va="center", fontsize=10.5, weight="bold", zorder=4)
dash = dict(ls=(0, (4, 3)), lw=1.6, color=MUTED, zorder=1)
XV = 8.7
axA.plot([D1[0] + .5, XV, XV], [D1[1], D1[1], 3.4], **dash)
axA.plot([D2[0] + .5, 6.5], [D2[1], D2[1]], **dash)
axA.plot([8.0, XV, XV], [D2[1], D2[1], 2.6], **dash)
axA.add_patch(FancyBboxPatch((6.5, D2[1] - .32), 1.5, .64, boxstyle="round,pad=0.03,rounding_size=0.1",
                             fc="#2a2414", ec=YEL, lw=1.4, zorder=2))
axA.text(7.25, D2[1], "delay τ", color=FG, fontsize=9.5, ha="center", va="center", zorder=3)
axA.plot([XV, 9.0], [3, 3], **dash)
axA.add_patch(FancyBboxPatch((9.0, 2.6), 1.95, .8, boxstyle="round,pad=0.04,rounding_size=0.1",
                             fc=PANEL, ec=MUTED, lw=1.4, zorder=2))
axA.text(9.975, 3.0, "Correlator", color=FG, fontsize=9.5, ha="center", va="center", zorder=3)
axA.text(7.3, 5.45, "electronic signals", color=MUTED, fontsize=8.5, ha="center", va="center")

# ---- B: click records ----
axB.set_ylim(-0.12, 2.3); axB.set_yticks([]); axB.set_xlim(T0, T0 + WIN)
axB.set_xlabel("time (ns)", color=MUTED, fontsize=9)
axB.text(0.99, 0.96, "I₁(t)  detector 1", transform=axB.transAxes, color=BLUE, fontsize=9.5, ha="right", va="top")
axB.text(0.99, 0.87, "I₂(t + τ)  detector 2", transform=axB.transAxes, color=YEL, fontsize=9.5, ha="right", va="top")
axB.axhline(0, color=PANEL, lw=0.8, zorder=0)
tau_txt = axB.text(0.01, 0.95, "", transform=axB.transAxes, color=FG, fontsize=10, va="top")
B_art = []
tgrid = np.linspace(T0, T0 + WIN, 1600)
def pulses(times):
    y = np.zeros_like(tgrid)
    for c in times:
        if T0 - 8 < c < T0 + WIN + 8:
            y += np.exp(-(tgrid - c) ** 2 / (2 * SIG**2))
    return y
y1 = pulses(s_win)
def draw_B(tau):
    for a in B_art:
        a.remove()
    B_art.clear()
    q_shift = q_win - tau
    y2 = pulses(q_shift)
    for y, col, z in ((y1, BLUE, 2), (y2, YEL, 3)):
        B_art.append(axB.fill_between(tgrid, 0, y, color=col, alpha=0.30, lw=0, zorder=z))
        l, = axB.plot(tgrid, y, color=col, lw=1.5, zorder=z + 1)
        B_art.append(l)
    for si in s_win:
        if T0 <= si < T0 + WIN and np.any(np.abs(q_shift - si) < W):
            B_art.append(axB.axvspan(si - W, si + W, ymin=0.02, ymax=0.62, color=GREEN, alpha=0.35, lw=0, zorder=1))
    tau_txt.set_text("delay τ = %.0f ns" % tau)
    if tau < 0.5:
        B_art.append(axB.text(0.01, 0.72, "τ = 0: blue and yellow together are the atom's\nlight before the beam splitter; they never overlap",
                              transform=axB.transAxes, color=MUTED, fontsize=8.3, va="top"))

# ---- C: curve ----
axC.set_xlim(0, TAU_MAX); axC.set_ylim(0, 1.9)
axC.set_yticks([0, 1]); axC.set_xticks(range(0, 101, 20))
axC.set_xlabel("delay τ applied to detector 2 (ns)", color=MUTED, fontsize=9.5)
axC.set_ylabel("⟨I₁(t) I₂(t+τ)⟩ relative to\nindependent clicks", color=MUTED, fontsize=9)
axC.axhline(1, color=MUTED, lw=1, ls=(0, (4, 3)), alpha=0.8)
axC.text(TAU_MAX - 1, 1.04, "independent clicks", color=MUTED, fontsize=9, ha="right", va="bottom")
line_C, = axC.plot([], [], color=GREEN, lw=2.6, zorder=3)
dot_C, = axC.plot([], [], "o", color=GREEN, mec="white", mew=1.2, ms=8, zorder=4)
note_C = axC.text(0.995, 0.05, "from the full record at each τ", transform=axC.transAxes,
                  color=MUTED, fontsize=8.5, ha="right", va="bottom")
extra = []

def draw_C(k, final=False):
    line_C.set_data(taus[:k + 1], g2_meas[:k + 1])
    dot_C.set_data([taus[k]], [g2_meas[k]])
    for a in extra:
        a.remove()
    extra.clear()
    if final:
        th, = axC.plot(tt, g2_theory, color=GREEN, lw=1.3, ls=(0, (3, 2)), alpha=0.8, zorder=2)
        extra.append(th)
        extra.append(axC.text(0.995, 0.26, "chance that the next photon follows within 5 ns:\nsingle atom %.0f %%,  random light %.0f %%" % (100 * P5_atom, 100 * P5_rand),
                              transform=axC.transAxes, color=FG, fontsize=9, ha="right", va="center"))
        extra.append(axC.annotate("g²(0) ≈ 0: below 1, which no classical\nwave can do (it needs g²(0) ≥ 1)",
                                  xy=(1.2, 0.04), xytext=(14, 0.42), color=GREEN, fontsize=9.5, va="center",
                                  arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.2), zorder=6))

def grab():
    fig.canvas.draw()
    return Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())

frames, durs = [], []
K = len(taus)
for k in range(K):
    draw_B(taus[k]); draw_C(k)
    frames.append(grab())
    durs.append(1500 if k == 0 else 1100 if taus[k] in (1.25,) else 90)
durs[-1] = 1200
draw_B(taus[-1]); draw_C(K - 1, final=True)
frames.append(grab()); durs.append(3500)

for name, idx in (("a", 0), ("b", 12), ("c", 28), ("d", len(frames) - 1)):
    frames[idx].save(OUT_DIR / f"fig6_frame_{name}.png")
pal = [f.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
out = OUT_DIR / GIF_NAME
pal[0].save(out, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)
print("saved", out.resolve(), "%.1f MB" % (out.stat().st_size / 1e6), len(frames), "frames")
