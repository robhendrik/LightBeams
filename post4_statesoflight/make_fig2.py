"""Figure 2: three states of light, drawn in the same convention as Figure 1.
Phase-space clouds are quadrature uncertainty regions (Wigner-style widths):
vacuum/coherent sigma = 1/2, thermal sigma^2 = nbar + 1/2, Fock = ring of radius sqrt(n).
All three states have the same mean photon number NBAR."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from math import factorial

NBAR = 4
UNIT = 0.24                       # screen units per quadrature unit (Fig 1 scale: sigma_coh = 0.12)
S_COH = 0.5 * UNIT
S_TH = np.sqrt(NBAR + 0.5) * UNIT
R_FOCK = np.sqrt(NBAR) * UNIT
ALPHA = np.sqrt(NBAR) * UNIT
ANG = np.deg2rad(30)
LIM = 1.0
BLUE = "#0b5fc4"
cmap = LinearSegmentedColormap.from_list("c", [(1, 1, 1, 0), (0.04, 0.37, 0.77, 1)])
BG, EDGE = "#fafafa", "#c3c6d1"
plt.rcParams["mathtext.fontset"] = "cm"

g = np.linspace(-LIM, LIM, 700)
X, Y = np.meshgrid(g, g)

def gauss(cx, cy, s):
    return np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * s ** 2))

def ring(R, s):
    return np.exp(-(np.hypot(X, Y) - R) ** 2 / (2 * s ** 2))

coh = gauss(ALPHA * np.cos(ANG), ALPHA * np.sin(ANG), S_COH)
th = gauss(0, 0, S_TH)
fock = ring(R_FOCK, S_COH)

fig, axs = plt.subplots(2, 3, figsize=(9.6, 6.4), dpi=200)
fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.0, hspace=0.0)

def panel(ax):
    ax.set_facecolor(BG)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(EDGE); sp.set_linewidth(1.2)

def arrow(ax, p0, p1):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2, mutation_scale=11, shrinkA=0, shrinkB=0))

for ax, img in zip(axs[0], [coh, th, fock]):
    panel(ax)
    ax.set_xlim(-LIM, LIM); ax.set_ylim(-LIM, LIM); ax.set_aspect("equal")
    ax.imshow(img, extent=[-LIM, LIM, -LIM, LIM], origin="lower", cmap=cmap, vmin=0, vmax=1, interpolation="bilinear", zorder=1)
    arrow(ax, (-0.80, 0), (0.78, 0)); arrow(ax, (0, -0.80), (0, 0.78))
    ax.text(0.82, -0.03, r"$X$", fontsize=15, ha="left", va="center")
    ax.text(0.0, 0.82, r"$P$", fontsize=15, ha="center", va="bottom")
    ax.set_clip_on(False)

n = np.arange(0, 16)
poisson = np.exp(-NBAR) * NBAR ** n / np.array([factorial(k) for k in n])
geom = (NBAR ** n) / (NBAR + 1) ** (n + 1)
fockp = (n == NBAR).astype(float)
cols = ["#4a9be8", "#f0766b", "#b97fcf"]
for ax, p, c in zip(axs[1], [poisson, geom, fockp], cols):
    panel(ax)
    ax.bar(n, 0.62 * p / p.max(), width=0.72, color=c, zorder=2)
    ax.set_xlim(-1.5, 17.8); ax.set_ylim(-0.045, 0.95)
    arrow(ax, (-1.0, 0), (16.0, 0)); arrow(ax, (-1.0, 0), (-1.0, 0.86))
    ax.text(16.4, -0.002, r"$n$", fontsize=15, ha="left", va="center")

# g2(0) labels
for ax, t in zip(axs[1], [r"$g^{(2)}(0)=1$", r"$g^{(2)}(0)=2$", r"$g^{(2)}(0)=1-1/n$"]):
    ax.text(0.97, 0.93, t, transform=ax.transAxes, ha="right", va="top", fontsize=11, color="#444")
for ax, t in zip(axs[0], ["coherent", "thermal", "Fock"]):
    ax.text(0.04, 0.95, t, transform=ax.transAxes, ha="left", va="top", fontsize=11, color="#444")
fig.savefig("./LightBeams/post4_statesoflight/post4_figure_2.png", facecolor="white")
