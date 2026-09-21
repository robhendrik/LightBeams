# Why Doesn't a Laser Beam Lose Its Shape?

*Light passing through a shape quickly turns into a blob. Yet laser
beams seem to keep their shape. What does this have to do with momentum
--- and how can light make matter rotate?*

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
## Diffraction Destroys Shapes --- Yet Laser Beams Survive

Start with the puzzle.

A beam of light passing through a circular hole initially has a
perfectly clear shape. Let it propagate, however, and diffraction
immediately starts changing that shape. In the far field the circle has
become an Airy pattern.

A laser beam behaves differently. A Gaussian beam spreads too, but its
transverse profile remains Gaussian. It does not simply reproduce a
picture carried along by the light. It is a propagation mode.

This is the first conceptual step: **some transverse shapes are natural
solutions of the wave equation.**

**Figure 1 --- A shape versus a mode.** A hard circular aperture and a
Gaussian TEM₀₀ beam start with roughly the same diameter. After
propagation, the aperture has diffracted into an Airy-like pattern,
while the Gaussian has expanded but kept the same basic shape. A laser
beam is not a rigid cylinder of light; its transverse profile is a
propagation mode.

## Some Shapes Are Made to Propagate

The familiar Gaussian spot is only the simplest member of a much larger
family.

Introduce the Hermite--Gaussian modes: TEM₀₀, TEM₁₀, TEM₀₁ and a few
higher-order examples. Their lobes and nodes may look increasingly
elaborate, but each is a well-defined solution that propagates in a
controlled way.

This is where the mathematical structure begins to appear. In the
paraxial approximation, the transverse modes can be organized with
mathematics closely related to the two-dimensional harmonic oscillator.
The resemblance is not just visual bookkeeping: the same ladder-operator
structure can be used to generate the family of modes.

Keep the oscillator connection light here. It is useful classical
mathematics now, and gives us something to return to in Post 2 when the
field itself is quantized.

**Figure 2 --- A family of beams.** The Gaussian TEM₀₀ mode is only the
ground floor. Higher-order Hermite--Gaussian modes form a structured
family of propagating solutions, with TEM₁₀ and TEM₀₁ as the simplest
two-lobed examples. Their organization mirrors the mathematics of a
two-dimensional harmonic oscillator.

## Two Different Beams Can Propagate in Exactly the Same Way

Now focus on TEM₁₀ and TEM₀₁.

They look different, but they belong to the same degenerate mode order:
they accumulate the same longitudinal and Gouy phase as they propagate.
That means they can be combined coherently without their relative
structure washing away.

Put them together directly and we obtain another pattern. Put them
together with a quarter-cycle phase difference,

**HG₁₀ + i HG₀₁,**

and something much more interesting appears: a Laguerre--Gaussian mode.

The intensity becomes doughnut-shaped. More importantly, the phase winds
around the dark centre.

This is also something optics can do physically, not merely
algebraically. Astigmatic mode converters built from cylindrical lenses
can transform between Hermite--Gaussian and Laguerre--Gaussian modes by
introducing the required relative phase.

**Figure 3 --- From two lobes to a vortex.** Two degenerate
Hermite--Gaussian modes, HG₁₀ and HG₀₁, combined with a quarter-cycle
phase shift form a Laguerre--Gaussian mode. The intensity is a doughnut,
but the crucial feature is hidden in the phase: it winds by 2π around
the dark centre. Cylindrical-lens mode converters can perform this HG↔LG
transformation experimentally.

## The Doughnut Is Hiding a Twist

A doughnut-shaped intensity profile is easy to see, but it is not what
gives the beam orbital angular momentum.

The important part is the phase.

For an LG mode it contains a factor of the form

**exp(iℓφ).**

Move once around the beam axis and the phase advances by ℓ complete
turns. The wavefront is therefore helical rather than flat.

The local momentum of a wave points normal to its phase front. A helical
phase front therefore gives the light a momentum component around the
beam axis. The beam is travelling forward, but some of its momentum
points sideways.

That circulating momentum is orbital angular momentum. For a pure LG
mode, the integer ℓ labels the handedness and amount of that twist.

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
