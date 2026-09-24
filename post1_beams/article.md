# Why Doesn't a Laser Beam Lose Its Shape?

*Shine light through an opening of any shape and diffraction smears it into a blob. Laser beams somehow survive intact — and figuring out how leads straight to a surprising twist.*

```{=html}
<!--
POST 1 STORY ARC

A hole diffracts → a Gaussian propagates as a mode → Gaussian beams come in whole
families → two apparently different mode families are closely related → an LG mode
has a helical phase → that phase means azimuthal momentum and orbital angular
momentum → the angular momentum can physically act on matter.

Keep this post classical. The harmonic-oscillator connection can foreshadow Post 2,
but quantization belongs there.
-->
```

Light seems able to take on any shape you shine it through — a keyhole, a leaf, a nebula. In reality none of those shapes should survive: send light through an opening of any form and diffraction blurs it into a formless smear within meters. Yet a laser beam refuses to do this — its bright spot travels for kilometers and comes out looking almost exactly as it started. How can that be?

It turns out there are some beam shapes that have this property: they may grow as they travel, but they keep their shape. Look closer, and some of these beams carry momentum sideways, circling the axis instead of pointing straight ahead. That sideways momentum is orbital angular momentum — real enough to make an object rotate.
## Diffraction Destroys Shapes — Yet a Gaussian Survives

Consider a beam that travels in the *z* direction and has an amplitude only in *x* direction for simplicity. Once launched, its transverse profile evolves according to one equation — the paraxial wave equation,

$$i \frac{\partial u}{\partial z} = -\frac{1}{2k} \frac{\partial^2 u}{\partial x^2}$$

— which says how the shape *u(x)* at one distance determines the shape at the next. Crucially, u depends on z: whatever profile you start with, this equation reshapes it as it travels. A sharp feature — a narrow slit, a hard edge — corresponds to rapid variation in x, and rapid variation is exactly what the second-derivative term acts on most strongly. So a shape that starts out crisp does not, in general, stay crisp; the equation itself is a rule for how much a profile *must* change with z, not whether it does.

A Gaussian avoids this fate, and the equation shows why directly. Try

$$u(x,z) = \frac{1}{\sqrt{w(z)}} \exp\left[-\frac{x^2}{w(z)^2}\right] \exp[iφ(z)]$$

as an ansatz, and it satisfies the equation exactly — the only z-dependence needed is in the width w(z) and an overall phase φ(z); the underlying shape, "Gaussian," never changes. There's no residual term forcing the profile to distort into something else. The beam widens, but it does so by stretching the same curve, not by growing new structure. A laser beam's spot isn't a fixed picture being carried along and gradually blurred — it's one of the rare shapes the equation lets pass through essentially untouched, which raises the natural question: is it the only one?


**Figure 1 --- A shape versus a mode.** A hard circular aperture and a
Gaussian TEM₀₀ beam start with roughly the same diameter. After
propagation, the aperture has diffracted into an Airy-like pattern,
while the Gaussian has expanded but kept the same basic shape. A laser
beam is not a rigid cylinder of light; its transverse profile is a
propagation mode.

## Some Shapes Are Made to Propagate

The Gaussian is not a special exception — it is only the simplest member of a family. Try a more general version of the same ansatz, keeping the same width w(z) and radius of curvature but replacing the fixed Gaussian bump with some other transverse shape h(ξ), written in the rescaled coordinate ξ = √2 x/w(z):

$$u_n(x,z) = \frac{1}{\sqrt{w(z)}} \exp\left[\frac{ikx^2}{2R(z)}\right] \exp[-i(n+\tfrac{1}{2})ψ(z)]\, h(ξ)$$

Substitute this into the paraxial equation, and almost everything from before goes through unchanged — the same w(z), the same curvature R(z). What's left over is a single condition that h(ξ) alone must satisfy, with all the z-dependence cancelled out:

$$h''(ξ) - 2ξ\,h'(ξ) + 2n\,h(ξ) = 0$$

This equation only has solutions that stay finite, rather than blowing up as ξ grows, when n is a non-negative integer: 0, 1, 2, … Each integer picks out one particular shape hₙ(ξ) — a Gaussian multiplied by a polynomial with n nodes. n = 0 recovers the plain Gaussian from before. n = 1, 2, 3, … are new shapes, each with its own pattern of lobes, and each one just as immune to diffraction's usual smoothing as the Gaussian was. The equation doesn't hand us one lucky survivor — it hands us an entire ladder of them.

This equation only has solutions that stay finite, rather than blowing up as ξ grows, when n is a non-negative integer: 0, 1, 2, … Each integer picks out one particular shape hₙ(ξ) — a Gaussian multiplied by a polynomial with n nodes. n = 0 recovers the plain Gaussian from before. n = 1, 2, 3, … are new shapes, each with its own pattern of lobes, and each one just as immune to diffraction's usual smoothing as the Gaussian was. The equation doesn't hand us one lucky survivor — it hands us an entire ladder of them.

This kind of quantization is nothing exotic — it's the same reason a guitar string only rings at certain frequencies: a differential equation plus a boundary condition (stay finite, don't blow up) forces a continuous problem to admit only a discrete set of solutions. No energy levels, no ℏ, nothing quantum required.

The genuinely striking part is that the same equation reappears with a different meaning in quantum mechanics. The Schrödinger equation for a two-dimensional harmonic oscillator has identical mathematical form — but there, the roles are different: it governs a wavefunction evolving in time, and the integer n labels discrete energy. Our beam equation governs a field's shape evolving in space (z stands in for t), and n labels discrete transverse shapes, not discrete energies — a beam of order n can carry any energy at all; nothing here restricts it. Same math, two completely different physical quantities being quantized, for two completely different physical reasons.

**Figure 2 --- A family of beams.** The Gaussian TEM₀₀ mode is only the
ground floor. Higher-order Hermite--Gaussian modes form a structured
family of propagating solutions, with TEM₁₀ and TEM₀₁ as the simplest
two-lobed examples. Their organization mirrors the mathematics of a
two-dimensional harmonic oscillator.

## Two Different Beams Can Propagate in Exactly the Same Way

## Two Different Beams Can Propagate in Exactly the Same Way

Now imagine a real beam, varying in both x and y. Since the paraxial equation has no term mixing the two directions, a product of two of the 1D shapes found earlier,

$$u_{n,m}(x,y,z) = χ_n(x)\,χ_m(y)$$

is itself an exact solution — solve x and y separately, then just multiply. Its Gouy phase is $(n+m+1)ψ(z)$, and only the *sum* n+m enters, not n and m individually. That single fact is the key to everything that follows: two beams with different shapes but the same n+m accumulate identical phase as they propagate, so their relative phase never drifts — any combination fixed at the waist stays fixed forever.

Take the simplest pair with n+m=1: TEM₁₀ and TEM₀₁, one lobed along x, the other along y. Add and subtract them, and the result is unsurprising — the same two-lobed pattern, just rotated by 45°. Recombining real modes with real coefficients only ever rotates the picture; it can't do anything more interesting, because both ingredients are already real, node-and-lobe patterns.

But nothing forces the coefficient to be real. Combine them with a *quarter-cycle phase* instead of a sign —

$$\text{HG}_{10} + i\,\text{HG}_{01}$$

— and the result stops looking like a rotated version of anything you started with. The intensity turns into a doughnut, and buried in that combination is a phase that winds smoothly around the dark centre, rather than flipping sign across a node the way every real combination did.

**Figure 3 --- From two lobes to a vortex.** Two degenerate
Hermite--Gaussian modes, HG₁₀ and HG₀₁, combined with a quarter-cycle
phase shift form a Laguerre--Gaussian mode. The intensity is a doughnut,
but the crucial feature is hidden in the phase: it winds by 2π around
the dark centre. Cylindrical-lens mode converters can perform this HG↔LG
transformation experimentally.

## The Doughnut Is Hiding a Twist

## The Doughnut Is Hiding a Twist

The doughnut-shaped intensity is easy to see, but it isn't the interesting part — a ring of light, by itself, is just a shape like any other. The interesting part is hidden in the phase.

Write $\text{HG}_{10} + i\,\text{HG}_{01}$ in polar coordinates, $x = ρ\cosφ$, $y = ρ\sinφ$. Since $\text{HG}_{10}\propto x$ and $\text{HG}_{01}\propto y$ (times the same radial envelope),

$$\text{HG}_{10} + i\,\text{HG}_{01} \;\propto\; (x+iy)\cdot(\text{envelope}) \;=\; ρ\,e^{iφ}\cdot(\text{envelope})$$

An explicit $e^{iφ}$ falls out. Walk once around the beam axis, φ goes from 0 to 2π, and the phase completes one full turn along with it. Nothing like this happened for any of the real combinations — HG₁₀, HG₀₁, or their sum — where the phase only ever jumped by a flat π across a node. This is smooth and continuous: the phase front isn't a flat plane, and it isn't a set of flipped plane segments either. It's a helix, winding once around the axis for every step forward in z.

More generally, a combination that winds ℓ times, $e^{iℓφ}$, is possible for higher-order modes — ℓ = 1 was just the simplest case. The doughnut you see is the shadow this winding casts on the intensity; the winding itself is the real object.


```{=html}
<!--
Possible pull quote:
The doughnut is what we see. The twist is in the phase.
-->
```
## Some of Light's Momentum Points Sideways

Make the geometry explicit here: a longitudinal momentum component
carries the beam forward, while the azimuthal component circles the
axis.

This is the bridge from an abstract phase pattern to a mechanical
quantity. Changing the sign of ℓ reverses the helical phase and
therefore reverses the azimuthal momentum.

The word *orbital* is important. This angular momentum comes from the
spatial structure of the beam, not from circular polarization and the
spin angular momentum of light.

The mathematics of a structured wave has acquired a physical
consequence.

## Light Can Actually Make Matter Rotate

End with the experimental payoff.

If the azimuthal momentum is real, matter should be able to feel it.

That is exactly what experiments demonstrated. A vortex beam can
transfer orbital angular momentum to matter, producing a torque. In the
1995 experiment by He and colleagues, absorbing particles trapped in a
beam carrying a phase singularity rotated; reversing the handedness of
the optical vortex reversed the direction of rotation.

So the chain is complete:

**a stable transverse mode → a winding phase → sideways momentum →
orbital angular momentum → mechanical rotation.**

**Figure 4 --- The twist becomes mechanical.** A helical optical phase
gives the beam an azimuthal momentum component and therefore orbital
angular momentum. When that angular momentum is transferred to matter it
produces a torque. In the experiment of He *et al.* (1995), absorbing
particles rotated in a vortex beam, and reversing the beam's handedness
reversed the rotation.

The surprising part is that none of this required photons yet.
Everything so far has been classical wave optics.

But the harmonic oscillator appeared for a reason. What happens if,
instead of only using its mathematics to organize classical modes, we
quantize the oscillator?

That is where the next post begins.

------------------------------------------------------------------------

### Feature Image

A visually clean three-dimensional Laguerre--Gaussian beam: a bright
doughnut-like intensity distribution wrapped around a clearly visible
helical phase/wavefront. No equations or explanatory labels. The image
should make the beam look as though it is propagating forward while
secretly twisting around its own axis.
