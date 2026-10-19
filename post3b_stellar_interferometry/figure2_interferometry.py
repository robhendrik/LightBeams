"""Figure 2: Michelson versus Hanbury Brown-Twiss stellar interferometry (dark style).

Run: python figure2_interferometry.py
Requires: numpy, matplotlib
Produces PNG, SVG and PDF next to the script.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import os

os.chdir("LightBeams")
os.chdir("post3b_stellar_interferometry")
cwd = os.getcwd()
print(cwd)
OUT = Path(__file__).resolve().parent

# palette shared with Figs 1, 3, 4, 5
BG, FG, MUTED = '#0e1621', '#d7e0ea', '#8fa3b8'
BLUE, YEL, PANEL = '#7cc4f2', '#fbbf24', '#2d3b52'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none',
    'text.color': FG, 'axes.facecolor': BG, 'axes.labelcolor': MUTED, 'axes.edgecolor': PANEL,
    'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.spines.top': False, 'axes.spines.right': False,
})
fig = plt.figure(figsize=(12.8, 8.3), facecolor=BG)
gs = fig.add_gridspec(2, 2, height_ratios=[0.62, 1], hspace=.30, wspace=.17,
                      left=.075, right=.975, top=.885, bottom=.145)


def setup_scheme(ax, title, ray_end, arrow_x):
    ax.set(xlim=(0, 10), ylim=(.8, 5.6))
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=8, color=FG)
    # one-dimensional uniformly bright star: same source in both panels
    ax.add_patch(Rectangle((.5, 2.58), .19, .84, facecolor=YEL, edgecolor='none'))
    ax.text(.6, 2.3, 'Star', ha='center', va='top', color=FG)
    for yy in (2.2, 3.8):
        ax.plot([.7, ray_end], [3, yy], color=YEL, lw=1.55, alpha=.8)
    ax.annotate('', (arrow_x, 3.8), (arrow_x, 2.2),
                arrowprops=dict(arrowstyle='<->', color=FG, lw=1.2))
    ax.text(arrow_x + .2, 3, '$d$', va='center', fontsize=14, color=FG)


# ---------------- A: Michelson ----------------
a = fig.add_subplot(gs[0, 0])
setup_scheme(a, 'A   Michelson — amplitude interferometry', ray_end=4.25, arrow_x=4.67)
a.plot([4.28, 4.28], [1.85, 2.08], lw=5, color=MUTED)
a.plot([4.28, 4.28], [2.32, 3.68], lw=5, color=MUTED)
a.plot([4.28, 4.28], [3.92, 4.15], lw=5, color=MUTED)
a.text(4.28, 1.62, 'Two apertures', ha='center', va='top', fontsize=9, color=FG)
a.plot([4.36, 7.35], [3.8, 3.05], color=BLUE, lw=2.4)
a.plot([4.36, 7.35], [2.2, 3.05], color=BLUE, lw=2.4)
a.add_patch(Rectangle((7.26, 2.79), .18, .54, angle=45,
                      facecolor=PANEL, edgecolor=BLUE, lw=1))
a.plot([7.48, 8.65], [3.05, 3.05], color=BLUE, lw=2.4)
a.add_patch(FancyBboxPatch((8.65, 2.8), .55, .5, boxstyle='round,pad=0.04,rounding_size=0.07',
                           facecolor=PANEL, edgecolor=MUTED, lw=1.5))
a.text(8.92, 2.6, 'One detector', ha='center', va='top', fontsize=9, color=FG)
a.text(7.4, 3.75, 'Beam combiner', ha='center', va='bottom', fontsize=9, color=FG)
a.text(5.6, 5.2, 'Optical fields are combined', ha='center', fontsize=10.5, color=BLUE)

# ---------------- B: HBT ----------------
b = fig.add_subplot(gs[0, 1])
setup_scheme(b, 'B   HBT — intensity interferometry', ray_end=3.6, arrow_x=5.85)
for yy, name in ((3.8, 'Detector 1'), (2.2, 'Detector 2')):
    b.add_patch(FancyBboxPatch((3.6, yy - .28), 1.85, .56, boxstyle='round,pad=0.04,rounding_size=0.07',
                               facecolor=PANEL, edgecolor=MUTED, lw=1.5))
    b.text(4.525, yy, name, ha='center', va='center', fontsize=9.5, color=FG)
# dashed wires = electronic signals, leaving the outer edges of the detectors
dash = dict(ls=(0, (4, 3)), lw=1.8, color=MUTED)
b.plot([4.525, 4.525, 7.3, 7.3], [4.1, 4.55, 4.55, 3.0], **dash)
b.plot([4.525, 4.525, 7.3, 7.3], [1.9, 1.45, 1.45, 3.0], **dash)
b.plot([7.3, 7.55], [3, 3], **dash)
b.add_patch(FancyBboxPatch((7.55, 2.55), 1.85, .9, boxstyle='round,pad=.05,rounding_size=.12',
                           facecolor='#2a2414', edgecolor=YEL, lw=1.5))
b.text(8.475, 3, 'Correlator', ha='center', va='center', fontsize=10, color=FG)
b.text(5.9, 1.12, 'Electronic signals', ha='center', va='center', fontsize=9, color=MUTED)
b.text(5.6, 5.2, 'Detector signals are correlated', ha='center', fontsize=10.5, color=YEL)

# ---------------- C: fringes ----------------
c = fig.add_subplot(gs[1, 0])
x = np.linspace(-1, 1, 900)
V = .68
c.plot(x, 1 + V * np.cos(7 * np.pi * x), color=BLUE, lw=2.4)
c.axhline(1, ls=':', color=MUTED, lw=1)
c.set(xlim=(-1, 1), ylim=(.1, 2.85), xlabel='Position / scanned optical phase',
      ylabel='Detected intensity (a.u.)')
c.set_title('Fringes: measure their visibility', fontsize=12, color=FG, pad=10)
c.annotate('', xy=(0, 1 + V), xytext=(0, 1 - V),
           arrowprops=dict(arrowstyle='<->', color=FG, lw=1.4))
c.text(0, 1.8, '$V$', va='bottom', ha='center', color=FG, fontsize=13)
# inset above the fringes: how V falls with the baseline
inset = c.inset_axes([.60, .67, .36, .22])
inset.set_facecolor(BG)
u = np.linspace(0, 3.25, 350)
inset.plot(u, np.abs(np.sinc(u)), color=BLUE, lw=1.9)
inset.set(xlim=(0, 3.25), ylim=(0, 1.08))
inset.tick_params(labelsize=7.5, length=2)
inset.set_xticks([0, 1, 2, 3]); inset.set_yticks([0, 1])
inset.set_title('$V$ versus baseline $d$', fontsize=8.5, color=MUTED, pad=3)
for s in ('top', 'right'):
    inset.spines[s].set_visible(True)
    inset.spines[s].set_color(PANEL)

# ---------------- D: HBT correlation ----------------
e = fig.add_subplot(gs[1, 1])
u = np.linspace(0, 3.25, 500)
e.plot(u, 1 + np.sinc(u) ** 2, color=YEL, lw=2.6)
e.axhline(1, color=MUTED, ls=':', lw=1.1)
e.text(3.2, 1.045, 'Uncorrelated level', ha='right', color=MUTED, fontsize=9)
e.set(xlim=(0, 3.25), ylim=(.91, 2.12), xlabel='Detector separation / baseline $d$ (normalized)',
      ylabel='Normalized intensity correlation $g^{(2)}(d)$')
e.set_title('Correlate intensities at two detectors', fontsize=12, color=FG, pad=10)
e.set_xticks([0, 1, 2, 3])

fig.suptitle('Two ways to measure the angular size of a star',
             fontsize=17, fontweight='bold', color=FG, y=.975)
fig.text(.5, .035,
         'Illustrative 1D top-hat star:  V(d) = |sinc(d)|   and   g²(d) = 1 + sinc²(d)  (chaotic light, equal optical paths).',
         ha='center', fontsize=9, color=MUTED)
for ext in ('png', 'svg', 'pdf'):
    fig.savefig(OUT / f'figure2_interferometry.{ext}', dpi=220, facecolor=BG)
plt.close(fig)
print('Saved', OUT / 'figure2_interferometry.png', '(+ .svg, .pdf)')
