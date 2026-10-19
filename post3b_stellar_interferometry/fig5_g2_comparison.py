"""Imagine g2<1: counts per time window at two detectors behind a 50/50 beam splitter, with realistic statistics.
(1) chaotic source (exponentially distributed intensity), fixed splitter, Poisson clicks given the intensity
(2) steady source, independent Poisson clicks at each detector
(3) imagined perfect single-photon source: exactly M photons per window, each goes to detector 1 or 2 at random (binomial)
Run: python fig_imagine_g0.py  (numpy, matplotlib)"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
BG, FG, MUTED = '#0e1621', '#d7e0ea', '#8fa3b8'
BLUE, YEL, PANEL, GREEN = '#7cc4f2', '#fbbf24', '#2d3b52', '#4ade80'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none',
    'text.color': FG, 'axes.facecolor': BG, 'axes.labelcolor': MUTED, 'axes.edgecolor': PANEL,
    'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False})
rng = np.random.default_rng(8)
M, NW, TC = 12, 1200, 4.0                                  # mean counts per window, windows, coherence time (windows)

# chaotic source: |E|^2 of a complex Gaussian (Ornstein-Uhlenbeck) field -> exponential intensity, mean 1
a = np.exp(-1 / TC); s = np.sqrt((1 - a * a) / 2)
xi = (rng.normal(size=NW) + 1j * rng.normal(size=NW)) * s
E = np.empty(NW, complex); E[0] = xi[0] / s * np.sqrt(.5)
for i in range(1, NW): E[i] = a * E[i - 1] + xi[i]
I = np.abs(E) ** 2
c1, c2 = rng.poisson(M * I / 2), rng.poisson(M * I / 2)       # fixed 50/50 splitter, clicks random given the intensity
l1, l2 = rng.poisson(M / 2, NW), rng.poisson(M / 2, NW)       # steady source, independent clicks
f1 = rng.binomial(M, .5, NW); f2 = M - f1                      # exactly M photons per window, each to 1 or 2

cases = [('Fixed 50/50 splitter,\nfluctuating (chaotic) source', c1, c2, YEL, 'in sync (blurred by click noise):\na band along the diagonal', 'Allows semi-classical explanation'),
         ('Steady source,\nindependent clicks', l1, l2, BLUE, 'unrelated: a round cloud', 'Allows semi-classical explanation'),
         ('Imagine $g^{(2)}<1$:\nlight in 1 means less light in 2', f1, f2, GREEN, 'mirror images: a line from\ntop left to bottom right', 'Not allowed (semi-)classically')]
fig, axs = plt.subplots(2, 3, figsize=(13, 7.8), facecolor=BG,
                        gridspec_kw=dict(height_ratios=[.9, 1.25], hspace=.55, wspace=.25, left=.06, right=.985, top=.84, bottom=.15))
LIM, w0, win = 27, 200, 60
for c, (ttl, n1, n2, col, note, verdict) in enumerate(cases):
    a0 = axs[0, c]; a0.set_title(ttl, fontsize=12, fontweight='bold', color=GREEN if c == 2 else FG, pad=10)
    t = np.arange(win)
    a0.step(t, n1[w0:w0 + win], where='mid', color=BLUE, lw=1.8, label='counts at 1')
    a0.step(t, n2[w0:w0 + win], where='mid', color=YEL, lw=1.8, label='counts at 2')
    a0.set(xlim=(0, win - 1), ylim=(0, 31)); a0.set_xlabel('time window')
    if c == 0: a0.set_ylabel('counts per window')
    a0.legend(loc='upper right', frameon=False, ncol=2, fontsize=8.5, labelcolor=FG)
    a1 = axs[1, c]; jit = lambda v: v + rng.uniform(-.25, .25, len(v))
    a1.scatter(jit(n1), jit(n2), s=9, color=col, alpha=.4, lw=0)
    a1.set(xlim=(-1, LIM), ylim=(-1, LIM)); a1.set_aspect('equal')
    a1.axhline(0, color=PANEL, lw=.8); a1.axvline(0, color=PANEL, lw=.8)
    a1.set_xlabel('counts at detector 1'); a1.set_title(note, fontsize=10, color=FG, pad=8)
    r = np.corrcoef(n1, n2)[0, 1]
    g2 = np.mean(n1 * n2) / (n1.mean() * n2.mean())
    a1.text(.97, .08, f'g² = {g2:.2f}', transform=a1.transAxes, ha='right', va='bottom', color=col, fontsize=12, weight='bold')
    a1.text(.5, -.30, verdict, transform=a1.transAxes, ha='center', va='top', fontsize=10, color=GREEN if c == 2 else MUTED, style='italic' if c == 2 else 'normal')
    if c == 0: a1.set_ylabel('counts at detector 2')
    print(ttl.replace('\n', ' '), 'g2=%.2f' % g2, 'r=%.2f' % r, 'mean n1=%.1f n2=%.1f' % (n1.mean(), n2.mean()))
fig.suptitle('Splitting a beam: what the two detectors can show', fontsize=15, fontweight='bold', color=FG, y=.97)
fig.savefig(OUT / 'figure_5.png', dpi=200, facecolor=BG)
