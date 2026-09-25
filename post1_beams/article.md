# Why Doesn't a Laser Beam Lose Its Shape?

*Shine light through an opening of any shape and diffraction smears it into a blob. Laser beams somehow survive intact — and figuring out how leads straight to a surprising twist.*

![Feature_image](../outputs/feature_twisted_light.png)
> Caption: **A helical wavefront — light with a twist.**
> Alt text: A monochrome 3D rendering of a helical optical wavefront twisting around the direction of propagation, illustrating the spiral phase structure of light carrying orbital angular momentum.

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

Consider a beam that travels in the *z* direction and, for simplicity, has an amplitude that varies only along *x*. Once launched, its transverse profile evolves according to the paraxial wave equation,

$$i \frac{\partial u}{\partial z} = -\frac{1}{2k} \frac{\partial^2 u}{\partial x^2}$$

The second derivative is the important part. Sharp edges and narrow features have a lot of curvature, so they change rapidly as the beam propagates. Diffraction immediately reshapes a slit, a hard edge, or almost any arbitrary profile.

A Gaussian is different. Suppose we try

$$u(x,z) = \frac{1}{\sqrt{w(z)}} \exp\left[-\frac{x^2}{w(z)^2}\right] \exp[iφ(z)]$$

and use this shape in the wave equation. We find that it is an exact solution. The width and phase change as the beam propagates, but the shape does not. Diffraction itself preserves the Gaussian shape, rather than gradually destroying it.

Which raises the obvious question: is it the only one?

![Figure 1](../outputs/figure_1_diffraction_vs_gaussian.png)

> Caption: **Figure 1. Not every beam keeps its shape. After 5 m of free-space propagation, a hard-edged circular beam develops diffraction rings, while a Gaussian beam simply broadens while retaining its Gaussian profile. Both beams were propagated using the same angular-spectrum calculation. Image by author.**
> Alt-text: Four-panel comparison of a hard-edged circular beam and a Gaussian beam before and after 5 m of propagation. The circular beam spreads into a broad central spot surrounded by diffraction rings, while the Gaussian beam becomes wider but retains its smooth Gaussian shape.

## Some Shapes Are Made to Propagate

The Gaussian is not the only shape that survives propagation. We use a rescaled coordinate, ξ = √2 x/w(z), and introduce a function h(ξ) to describe transverse structure. This gives a more general beam shape:

$$
u_n(x,z)=\frac{1}{\sqrt{w(z)}}
e^{ikx^2/2R(z)}
e^{-i\left(n+\tfrac{1}{2}\right)\psi(z)}
h(\xi).
$$

When we put this into the paraxial wave equation, the z-dependence separates out. What remains is an equation for the transverse function h(ξ):

$$
h''(\xi)-2\xi h'(\xi)+2n h(\xi)=0.
$$

This is the Hermite equation. Its finite polynomial solutions exist only for non-negative integers n = 0, 1, 2, …, giving the Hermite polynomials Hₙ(ξ). The corresponding transverse modes are therefore

$$
u_n \propto e^{-\xi^2/2} H_n(\xi).
$$

For n = 0 we get the ordinary Gaussian. For n = 1, 2, 3, …, extra nodes and lobes appear, but the rescaled shape is still preserved during propagation. So the Gaussian is not one special survivor; it is the first member of a whole family.

The integer *n* may look like quantum mechanics, but there is nothing quantum here. It appears because the differential equation and the boundary conditions only allow a discrete set of solutions — just as a guitar string only supports certain standing-wave patterns.

However, there is a simple quantum system that follows exactly the same mathematics: the harmonic oscillator [1]. There, the same integer *n* labels discrete energy levels. Here, it labels transverse beam shapes.

The mathematics is the same, but the physical meaning is different.

![Figure 2](../outputs/figure_2_hermite_gaussian_modes.png)

> Caption: **Figure 2. Gaussian beams come in families. The Hermite–Gaussian modes are labelled by two integers, n and m, which count the transverse structure in the horizontal and vertical directions. The familiar Gaussian beam is simply the lowest member, HG₀₀. Image by author.**
> Alt text: Four-by-four grid showing the intensity profiles of Hermite–Gaussian laser modes for n and m from 0 to 3. HG00 is a single bright Gaussian spot; increasing n divides the beam into more vertical lobes, while increasing m produces more horizontal lobes.

## Two Different Beams Can Propagate in Exactly the Same Way

Now imagine a real beam, varying in both x and y. Since the paraxial equation has no term mixing the two directions, a product of two of the 1D shapes found earlier solves $x$ and $y$ directly:

$$
u_{n,m}(x,y,z)=u_n(x,z)\,u_m(y,z)
$$

The Gouy phase is $(n+m+1)ψ(z)$; only the *sum* n+m enters, not n and m individually. This means that two beams with different shapes but the same $n+m$ accumulate identical phase as they propagate, any combination fixed at the waist stays fixed forever.

Take the simplest pair with n+m=1: TEM₁₀ and TEM₀₁, one lobed along x, the other along y. Add and subtract them, and the result is unsurprising — the same two-lobed pattern, just rotated by 45°. Recombining real modes with real coefficients only ever rotates the picture; it can't do anything more interesting, because both ingredients are already real, node-and-lobe patterns.

But nothing forces the coefficient to be real. Combine them with a *quarter-cycle phase* instead of a sign —

$$\text{HG}_{10} + i\,\text{HG}_{01}$$

— and the result stops looking like a rotated version of anything you started with. The intensity turns into a doughnut, and buried in that combination is a phase that winds smoothly around the dark centre, rather than flipping sign across a node the way every real combination did.

![Figure 3](../outputs/figure_3_hg_to_lg.png)
> Caption: **Figure 3. From two lobes to a vortex. HG₁₀ and HG₀₁ can be combined in different ways. Adding or subtracting them produces the same two-lobed pattern at a rotated angle. Add a quarter-cycle (π/2) phase shift between them instead, and the intensity becomes a doughnut. The two doughnuts look identical here—but their hidden phases wind in opposite directions. Image by author.**
> Alt text: Six intensity plots arranged in two rows and three columns. The first column shows the perpendicular two-lobed HG10 and HG01 modes. Adding and subtracting them produces diagonally rotated two-lobed patterns. Combining them with positive or negative pi-over-two relative phase produces identical doughnut-shaped intensity patterns with a dark centre.

## The Doughnut Is Hiding a Twist

The doughnut-shaped intensity is easy to see, but it isn't the interesting part — a ring of light, by itself, is just a shape like any other. The interesting part is hidden in the phase.

Write $\text{HG}_{10} + i\,\text{HG}_{01}$ in polar coordinates, $x = ρ\cosφ$, $y = ρ\sinφ$. Since $\text{HG}_{10}\propto x$ and $\text{HG}_{01}\propto y$ (times the same radial envelope),

$$\text{HG}_{10} + i\,\text{HG}_{01} \;\propto\; (x+iy)\cdot(\text{envelope}) \;=\; ρ\,e^{iφ}\cdot(\text{envelope})$$

An explicit $e^{iφ}$ falls out. Walk once around the beam axis, φ goes from 0 to 2π, and the phase completes one full turn along with it. Follow a surface of constant phase as you also move forward in z, and that surface traces a helix around the beam axis.

Nothing like this happened for any of the real combinations — HG₁₀, HG₀₁, or their sum — where the phase only jumped by π across a node. Here the phase winds smoothly and continuously around the axis.

More generally, a combination that winds ℓ times, $e^{iℓφ}$, is possible for higher-order modes — ℓ = 1 was just the simplest case. The doughnut you see is the shadow this winding casts on the intensity; the winding itself is the real object.

```{=html}
<!--
Possible pull quote:
The doughnut is what we see. The twist is in the phase.
-->
```

## Mode conversion in experiments

This isn't just algebra — the same conversion can be done with real optics. Take a Hermite-Gaussian beam oriented at 45° to a pair of cylindrical lenses. In the lenses' own frame, that diagonal mode is nothing more than the horizontal and vertical modes added together, HG₁₀ + HG₀₁ — the "in-phase" combination that, as we saw, is just a rotated pair of lobes.

The trick is what happens as the beam passes between the two lenses. Because the lenses focus the beam differently along their two axes, the horizontal and vertical components pick up different amounts of Gouy phase on the way through — an astigmatic version of the same phase you tracked earlier, now split unevenly between x and y instead of shared equally. Tune the lens spacing so that difference comes out to exactly a quarter cycle, and the output is HG₁₀ + i HG₀₁ — precisely the combination that produces the doughnut.

This mode converter was built and demonstrated in 1993 by Beijersbergen and colleagues in Leiden [2], using nothing more exotic than two cylindrical lenses at a fixed separation. Send in a diagonally-oriented two-lobed beam, and a vortex comes out the other side — the winding phase isn't a mathematical curiosity conjured by adding amplitudes on paper, it's something a beam of light can be made to acquire simply by passing through the right piece of glass.

![Figure 4](../outputs/figure_4_cylindrical_mode_converter.png)
> Caption: **Figure 4. Turning lobes into a vortex. A pair of cylindrical lenses converts a Hermite–Gaussian mode, oriented at 45° to the lens axes, into a Laguerre–Gaussian mode. The lenses focus the beam differently along the two transverse directions, introducing the relative phase shift that turns the two-lobed input into a doughnut-shaped output. Image by author.**
> Alt text: 3D illustration of a laser beam passing through two transparent cylindrical lenses. The input beam has two bright diagonal lobes, while the output has a bright doughnut-shaped intensity profile. The beam narrows asymmetrically between the lenses, illustrating the astigmatic mode conversion.

## Some of Light's Momentum Points Sideways

We know light carries momentum: a beam can push on whatever absorbs it. The more intense the beam, the harder it pushes — that part is intuitive.

For a plane wave, that push is *E*/*c*, no exceptions. But our beams aren't plane waves — they have transverse structure, and we saw that structure comes with a cost: the phase of a higher-order mode runs behind a plane wave's, more so for larger *n*+*m*. So, does that phase lag cost the beam anything mechanical? It does: the same beam, absorbed, delivers *less* forward momentum than *E*/*c*. Everything else being equal, a higher-order beam pushes less hard.

Where did the forward momentum go? Into the beam's transverse momentum. Those sideways components can cancel as ordinary linear momentum while still leaving something behind: angular momentum.

In a vortex beam they don't point randomly outward and inward. Locally, the momentum has an azimuthal component — it circulates around the axis. Opposite sides of the beam push in opposite linear directions, so there is no net sideways shove. But because those pushes occur on opposite sides of the axis, their torques add rather than cancel.

The doughnut is where this stops being boring. The sideways linear momenta still cancel when you add them across the whole beam — there is no net push to the left or right. But their angular momenta do not cancel. Every local azimuthal component circulates around the axis with the same handedness, so their torques add. That is orbital angular momentum: momentum flowing around an axis rather than simply along it.

![Figure 5](../outputs/figure_5_OAM.png)
> Caption: **Figure 5. A twist with mechanical consequences. A vortex beam carries momentum forward and around its axis. Its azimuthal momentum can transfer angular momentum to a trapped particle; reversing the phase winding reverses the direction of rotation. Image by author.**
> Alt text: Three transverse views of a doughnut-shaped vortex beam. The first marks forward momentum out of the page and azimuthal momentum around the dark axis. The other two show particles on identical bright rings moving in opposite directions for phase winding numbers +1 and −1.

## Light Can Actually Make Matter Rotate

We've seen that a beam can carry orbital angular momentum, and that the higher the order of the doughnut, the more it carries. But angular momentum is conserved — it can't come from nowhere. So, think back to the mode converter: a beam with zero orbital angular momentum goes in, a beam with some comes out. Where did it come from?

It has to come from the lenses. There's no other source. If the light picks up clockwise orbital angular momentum on the way through, the lens system has to recoil counterclockwise — a real, physical kick, exactly as much as the light gained.

This wasn't obvious in 1992. Allen, Beijersbergen, Spreeuw and Woerdman, working in Leiden, were the ones who first worked out that a light beam's spatial structure alone carries angular momentum [3]. And they didn't stop at the idea: they wanted to *weigh* it. Robert Spreeuw, one of the four, later wrote a personal account of what came next [4]. They hung a pair of cylindrical lenses on a torsion fibre in vacuum and sent a vortex beam through, looking for the tiny twist as the lenses absorbed the reaction. It turned out to be "prohibitively difficult," in Spreeuw's own words — buried under systematic noise no amount of care could fully remove. Sometimes physics is exactly this: right idea, right setup, and nature simply won't hand you a clean number.

The direct proof came from somewhere else entirely. In 1995, He, Friese, Heckenberg and Rubinsztein-Dunlop skipped the torsion pendulum and went straight for a particle sitting in the beam itself [5]. Small absorbing particles illuminated by a vortex beam started to rotate. Reverse the vortex's handedness, and the particles reversed too.

So the chain is complete: a stable transverse mode → a winding phase → sideways momentum → orbital angular momentum → mechanical rotation.

And none of it needed a single photon. We even ran into 'quantized' modes along the way — the integer *n* labelling the Hermite-Gaussian family — but that quantization came straight out of the classical paraxial equation, a boundary condition doing its usual job, nothing more. This triggers the question: what happens once we stop borrowing the oscillator's *mathematics* and actually apply quantum mechanics to the light itself? How do these modes, and this angular momentum, look in a theory where photons rule?

That is where the next post begins.

## Bonus
![Bonus Figure](../outputs/bonus_higher_order_vortex.png)
> Caption: **Bonus figure — Building a higher-order vortex. A third-order Laguerre–Gaussian mode can be constructed from four degenerate Hermite–Gaussian modes with carefully chosen amplitudes and phases. Although the resulting LG₀⁺³ intensity is still a simple doughnut, its hidden phase winds three times around the dark centre — a total phase change of 6π.**
> Alt text: Four third-order Hermite–Gaussian intensity patterns, labelled HG₃₀, i√3 HG₂₁, −√3 HG₁₂, and −i HG₀₃, combine into an LG₀⁺³ mode. The resulting mode has a bright circular ring surrounding a dark centre.

## References

[1] G. Nienhuis and L. Allen, "Paraxial wave optics and harmonic oscillators," *Phys. Rev. A* **48**, 656–665 (1993). https://doi.org/10.1103/PhysRevA.48.656

[2] M. W. Beijersbergen, L. Allen, H. E. L. O. van der Veen, and J. P. Woerdman, "Astigmatic laser mode converters and transfer of orbital angular momentum," *Opt. Commun.* **96**, 123–132 (1993). https://doi.org/10.1016/0030-4018(93)90535-D

[3] L. Allen, M. W. Beijersbergen, R. J. C. Spreeuw, and J. P. Woerdman, "Orbital angular momentum of light and the transformation of Laguerre-Gaussian laser modes," *Phys. Rev. A* **45**, 8185–8189 (1992). https://doi.org/10.1103/PhysRevA.45.8185

[4] R. J. C. Spreeuw, "Spiraling light: from donut modes to a Magnus effect analogy," *Nanophotonics* **11**, 633–644 (2021). https://doi.org/10.1515/nanoph-2021-0458

[5] H. He, M. E. J. Friese, N. R. Heckenberg, and H. Rubinsztein-Dunlop, "Direct observation of transfer of angular momentum to absorptive particles from a laser beam with a phase singularity," *Phys. Rev. Lett.* **75**, 826–829 (1995). https://doi.org/10.1103/PhysRevLett.75.826