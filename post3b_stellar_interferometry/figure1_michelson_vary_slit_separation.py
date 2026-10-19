"""Numerically sum incoherent point-source fringes while varying slit separation.

Run: pip install numpy matplotlib pillow
     python michelson_vary_slit_separation.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

OUT = Path(__file__).with_suffix('.gif')
N_EMITTERS = 801
SOURCE_FRACTION = 0.20  # illuminated fraction of the full source object
MAX_BASELINE = 15.0  # d / (lambda / full angular source width)
N_SWEEP, N_HOLD, FPS = 92, 24, 15

# Dimensionless source and screen angles in units of full source-object width.
source_y = np.linspace(-SOURCE_FRACTION/2, SOURCE_FRACTION/2, N_EMITTERS)
screen_y = np.linspace(-0.85, 0.85, 1100)
baselines = np.linspace(0, MAX_BASELINE, N_SWEEP)

fig = plt.figure(figsize=(12.6, 6.6), facecolor='#101724')
gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.25], height_ratios=[1.8, 1],
                      left=.06, right=.97, top=.88, bottom=.10, hspace=.42, wspace=.26)
ax_geo = fig.add_subplot(gs[:, 0]); ax_screen = fig.add_subplot(gs[0, 1]); ax_vis = fig.add_subplot(gs[1, 1])
for ax in (ax_geo, ax_screen, ax_vis):
    ax.set_facecolor('#101724')
    ax.tick_params(colors='#cbd5e1')
    for spine in ax.spines.values(): spine.set_color('#617187')

ax_geo.set_xlim(0, 10); ax_geo.set_ylim(-1.5, 1.5); ax_geo.axis('off')
sx, dx, ex = 1.1, 5.55, 9.1
ax_geo.plot([sx,sx],[-1.2,1.2],color='#334155',lw=10,solid_capstyle='butt')
ax_geo.plot([sx,sx],[-.24,.24],color='#fbbf24',lw=10,solid_capstyle='butt')
ax_geo.plot([ex,ex],[-1.35,1.35],lw=4,color='#b6c3d3')
for x, lab in [(sx,'Source (20%)'),(dx,'Two slits'),(ex,'Screen')]:
    ax_geo.text(x,1.46,lab,ha='center',color='white',fontsize=11)
ax_geo.text(5.05,-1.46,'Schematic; slit separation exaggerated',color='#94a3b8',ha='center',fontsize=9)
# Three opaque sections leave two openings centered at +/- slit_offset.
slit_segments = [ax_geo.plot([],[],lw=6,color='#b6c3d3',solid_capstyle='butt')[0] for _ in range(3)]
slit_markers = ax_geo.scatter([],[],s=35,c='#101724',edgecolors='#fbbf24',zorder=7)

ax_screen.set_xlim(screen_y.min(),screen_y.max()); ax_screen.set_ylim(-.12,2.18)
ax_screen.set_xlabel('Screen angle (units of full object width)',color='#cbd5e1')
ax_screen.set_ylabel('Mean intensity',color='#cbd5e1')
ax_screen.set_title('Numerical sum of point-source fringes',color='white',fontsize=12)
fringe_line, = ax_screen.plot([],[],color='#7dd3fc',lw=2.2)
ax_screen.axhline(1,color='#64748b',ls='--',lw=.8)
info = ax_screen.text(.02,.97,'',transform=ax_screen.transAxes,va='top',color='#fde68a',fontsize=10)

ax_vis.set_xlim(0,MAX_BASELINE); ax_vis.set_ylim(-.26,1.07)
ax_vis.set_xlabel(r'Slit separation $d$ (units $\lambda/W$)',color='#cbd5e1')
ax_vis.set_ylabel('Signed fringe coefficient',color='#cbd5e1')
ax_vis.set_title('Extracted from numerical intensity (no sinc imposed)',color='white',fontsize=11)
ax_vis.axhline(0,color='#64748b',lw=.8)
for zero in (5,10,15):
    ax_vis.axvline(zero,color='#94a3b8',lw=.8,ls=':',alpha=.65)
ax_vis.text(5.12,.9,'first null',color='#94a3b8',fontsize=9)
vis_line, = ax_vis.plot([],[],color='#fbbf24',lw=2.1)
vis_dot, = ax_vis.plot([],[],'o',color='#fbbf24',ms=6)
fig.suptitle('Fixed extended source: varying the double-slit separation',color='white',fontsize=16)

# Numerical simulation: at each baseline, sum intensity patterns of ALL
# incoherent source points. No analytic sinc or Fourier formula used.
intensities = []
coefficients = []
for baseline in baselines:
    phases = 2*np.pi*baseline*source_y
    # Add source-point intensities numerically. Equivalent to averaging
    # 1 + cos(2*pi*baseline*(source_y + screen_y)) for every source point.
    # The sum is factored into cos/sin terms to avoid a huge temporary array.
    c = np.cos(phases).mean()
    s = np.sin(phases).mean()
    intensity = 1 + c*np.cos(2*np.pi*baseline*screen_y) - s*np.sin(2*np.pi*baseline*screen_y)
    intensities.append(intensity)
    coefficients.append(c)  # signed coefficient extracted from numerical point sums


def update(frame):
    i = min(frame, N_SWEEP-1)
    baseline = baselines[i]
    fringe_line.set_data(screen_y, intensities[i])
    vis_line.set_data(baselines[:i+1],coefficients[:i+1])
    vis_dot.set_data([baseline],[coefficients[i]])
    # Geometric depiction: opening separation grows; schematic scale only.
    offset = .14 + .65 * baseline/MAX_BASELINE
    half_gap = .045
    segments = [(-1.35,-offset-half_gap),(-offset+half_gap,offset-half_gap),(offset+half_gap,1.35)]
    for artist,(lo,hi) in zip(slit_segments,segments):
        artist.set_data([dx,dx],[lo,hi])
    slit_markers.set_offsets(np.array([[dx,-offset],[dx,offset]]))
    info.set_text(f'801 independent emitters, source fixed at 20%\n'
                  f'Slit separation: {baseline:.2f} $\\lambda/W$'
                  f'    Signed contrast: {coefficients[i]:+.3f}')
    return fringe_line,vis_line,vis_dot,info,slit_markers,*slit_segments

animation = FuncAnimation(fig,update,frames=N_SWEEP+N_HOLD,interval=1000/FPS,blit=False)
animation.save(str(OUT),writer=PillowWriter(fps=FPS),dpi=90)
plt.close(fig)
print(f'Created {OUT}')
