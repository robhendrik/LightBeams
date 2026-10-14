import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

s = 1 / np.sqrt(2)
I = 1j

# (label of entries, integer-ish matrix before the 1/sqrt2 factor, test input, verdict, reason)
panels = [
    ("Allowed", [[1, 1], [1, -1]],   (1, 1),   True,  "columns do not overlap"),
    ("Allowed", [[1, I], [I, 1]],    (1, -I),  True,  "columns do not overlap"),
    ("Allowed", [[-1, 1], [1, 1]],   (1, 1),   True,  "columns do not overlap"),
    ("Not allowed", [[1, 1], [1, 1]],   (1, 1),  False, "overlap = 1"),
    ("Not allowed", [[1, I], [I, -1]],  (1, -I), False, "overlap = i"),
    ("Not allowed", [[1, I], [1, I]],   (1, -I), False, "overlap = i"),
]


def cstr(z):
    z = complex(z)
    if abs(z.imag) < 1e-12:
        v = z.real
        n = int(round(v))
        return f"{n}" if n >= 0 else f"\u2212{abs(n)}"
    if abs(z.real) < 1e-12:
        v = z.imag
        return "i" if abs(v - 1) < 1e-12 else ("\u2212i" if abs(v + 1) < 1e-12 else f"{v}i")
    return str(z)


def amp_str(z):
    """amplitude of the form k*sqrt2 * phase (k real or imaginary)"""
    z = complex(z)
    if abs(z) < 1e-12:
        return "0"
    r = z / np.sqrt(2)  # coefficient of sqrt2
    if abs(r.imag) < 1e-12:
        v = r.real
        return "\u221a2" if abs(v - 1) < 1e-9 else ("\u2212\u221a2" if abs(v + 1) < 1e-9 else f"{v:.2f}\u221a2")
    if abs(r.real) < 1e-12:
        v = r.imag
        return "i\u221a2" if abs(v - 1) < 1e-9 else ("\u2212i\u221a2" if abs(v + 1) < 1e-9 else f"{v:.2f}i\u221a2")
    return f"{z:.2f}"


GREEN = "#2a7a4b"
RED = "#b03a3a"
BLUE = "#2a6fa8"

fig, axes = plt.subplots(2, 3, figsize=(11, 7.4))
fig.suptitle("Lossless means unitary: three allowed phase patterns, three forbidden ones",
             fontsize=14, y=0.985)

report = []
for ax, (grp, M, inp, ok, reason) in zip(axes.flat, panels):
    M = np.array(M, dtype=complex)
    U = s * M
    x = np.array(inp, dtype=complex)
    out = U @ x
    pin = float(np.sum(abs(x) ** 2))
    pout = float(np.sum(abs(out) ** 2))
    overlap = np.conj(U[0, 0]) * U[0, 1] + np.conj(U[1, 0]) * U[1, 1]
    col_norms = np.sum(abs(U) ** 2, axis=0)
    unitary = np.allclose(U.conj().T @ U, np.eye(2))
    assert unitary == ok, (M, unitary, ok)
    assert np.allclose(col_norms, 1)          # every column carries unit power
    assert abs(pin - 2) < 1e-9
    if ok:
        assert abs(pout - pin) < 1e-9
        assert abs(overlap) < 1e-12
    else:
        assert abs(pout - 4) < 1e-9
        assert abs(overlap) > 0.99
    report.append((M.tolist(), inp, out.round(3).tolist(), pin, round(pout, 6), np.round(overlap, 3)))

    col = GREEN if ok else RED
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.15, 0.15), 9.7, 9.7, boxstyle="round,pad=0.02,rounding_size=0.3",
                                fill=True, fc="#f4faf6" if ok else "#fbf3f3",
                                ec=col, lw=2.2))
    # verdict mark
    ax.text(9.35, 9.1, "\u2713" if ok else "\u2717", color=col, fontsize=26, ha="right", va="center",
            fontweight="bold")
    ax.text(0.7, 9.1, grp, color=col, fontsize=12, ha="left", va="center", fontweight="bold")

    # matrix with prefactor
    ax.text(1.0, 6.7, r"$\frac{1}{\sqrt{2}}$", fontsize=17, ha="center", va="center")
    xs = [3.7, 5.7]
    ys = [7.4, 6.0]
    for r in range(2):
        for c in range(2):
            ax.text(xs[c], ys[r], cstr(M[r, c]), fontsize=17, ha="center", va="center")
    # brackets
    for sx, sgn in ((2.55, 1), (6.85, -1)):
        ax.plot([sx + sgn * 0.25, sx, sx, sx + sgn * 0.25], [8.1, 8.1, 5.3, 5.3], color="black", lw=1.5)

    # test input and output
    a, b = inp
    ax.text(0.7, 4.0, f"input (a, b) = ({cstr(a)}, {cstr(b)})", fontsize=11.5, ha="left", va="center")
    ax.text(0.7, 3.0, f"output (c\u2081, c\u2082) = ({amp_str(out[0])}, {amp_str(out[1])})",
            fontsize=11.5, ha="left", va="center")

    # power readout
    ax.text(0.7, 1.75, f"power  in {pin:.0f}  \u2192  out {pout:.0f}", fontsize=13, ha="left",
            va="center", color=col, fontweight="bold")
    ax.text(0.7, 0.8, reason, fontsize=10.5, ha="left", va="center", color="#444444", style="italic")

    if not ok:
        # diagonal strike line through the matrix area, as a non-colour cue
        ax.plot([2.3, 7.1], [8.4, 4.9], color=col, lw=2, alpha=0.30, zorder=0)

fig.text(0.5, 0.012,
         "Each matrix is a classical amplitude rule, not a specific device.  "
         "All six are 50/50 and carry the factor 1/\u221a2; only the phases differ.",
         ha="center", fontsize=10, color="#333333")
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
fig.savefig("post3_fig_unitarity_six_panels.png", dpi=200)

for r in report:
    print(r)
print("all checks passed")
