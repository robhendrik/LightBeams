# A Photon Is Not a Tiny Wave Packet

*Classical light can already be localized, carry momentum and twist
matter. So what does quantizing the electromagnetic field actually add?*

```{=html}
<!--
POST 2 STORY ARC

Post 1 ended with a classical light mode carrying real momentum and angular momentum.
Now confront the intuitive picture that a photon is simply a small localized piece
of that classical wave.

Start classically: waves can be localized into packets, and classical fields already
carry energy, momentum and angular momentum. So none of those properties by themselves
defines a photon.

Then introduce the normal-mode decomposition of the electromagnetic field. Each mode
behaves mathematically like a harmonic oscillator. Quantizing those oscillators gives
discrete excitation numbers and the creation/annihilation operators.

Only then return to structured light/OAM: one excitation of an LG mode has energy
ℏω and orbital angular momentum ℓℏ. The photon inherits the properties of the mode
that is excited.

End by returning to localization: a photon localized in space generally requires a
superposition of modes. "Photon" and "wave packet" are therefore different ideas.

Possible callback to Post 1: the harmonic oscillator appeared there as a surprisingly
useful way to organize transverse modes. Here it returns in a much deeper role.
-->
```
## A Wave Packet Is Still Just a Classical Wave

Begin with the most natural intuition.

A monochromatic plane wave fills all of space, so if we want a pulse of
light in one place we superpose many waves with slightly different
frequencies and wavevectors. Their interference creates a localized wave
packet.

That packet can travel, spread, carry energy and momentum, and interact
with matter. Nothing quantum has happened.

This is the key reset for the post: **localization does not make light
into photons.**

A classical electromagnetic field can already be shaped into a pulse.

**Figure 1 --- Making a pulse without photons.** Several extended waves
with nearby wavevectors are superposed. Individually they extend across
space; together their phases reinforce only over a limited region,
creating a localized wave packet. A localized packet of light is
perfectly possible in classical electromagnetism.

## Even Momentum Does Not Make It a Photon

Post 1 gave us an even stronger warning.

A classical LG beam carries linear momentum and orbital angular
momentum. It can transfer that momentum to matter and make a particle
rotate. Classical electromagnetism already assigns energy and momentum
to the field.

So the familiar list ---

**localized, carries energy, carries momentum, pushes matter**

--- still does not tell us what is specifically quantum about light.

To find that, stop trying to make the classical wave smaller. Instead,
look at how the electromagnetic field itself is built.

## The Electromagnetic Field Is a Collection of Oscillators

Any electromagnetic field can be decomposed into normal modes.

The simplest examples are plane-wave modes, but the idea is much
broader. In a laser or optical cavity we can equally choose Gaussian,
Hermite--Gaussian or Laguerre--Gaussian modes.

For each independent mode, Maxwell's equations leave us with two
quantities that oscillate back and forth in precisely the mathematical
form of a harmonic oscillator.

Schematically, the energy of one mode can be written as

**H = ½(P² + ω²Q²).**

This is the bridge.

In Post 1 the harmonic oscillator appeared because its mathematics
organized the spatial structure of paraxial beams. Here an oscillator
appears again, but for a different and deeper reason: **each normal mode
of the electromagnetic field is dynamically a harmonic oscillator.**

**Figure 2 --- One field, many oscillators.** Decompose an
electromagnetic field into independent optical modes. Each mode has its
own amplitude and phase and behaves mathematically like a harmonic
oscillator. Quantizing light means quantizing these mode oscillators ---
not chopping a classical wave into little pieces.

## Quantization Changes What the Oscillator Can Contain

Classically, an oscillator can have any energy.

Quantum mechanics changes that. A quantum harmonic oscillator has
discrete energy levels,

**Eₙ = (n + ½)ℏω.**

The step from one level to the next is always ℏω.

We introduce the annihilation and creation operators to move between
these levels: one lowers the excitation number by one, the other raises
it by one.

For an electromagnetic mode, those excitations are what we call photons.

A state with n photons is therefore not a classical wave divided into n
little packets. It is the nth excitation state of a particular field
mode.

```{=html}
<!--
Possible pull quote:
A photon is not a piece of a mode. It is one quantum of excitation of that mode.
-->
```
**Figure 3 --- Where the photon enters.** A classical field mode behaves
like a harmonic oscillator whose energy can vary continuously. After
quantization, that same oscillator has discrete excitation levels
separated by ℏω. Moving up one level adds one photon to the mode; moving
down removes one.

## A Photon Inherits the Shape of Its Mode

Now return to the structured beams from Post 1.

Suppose the mode we quantize is a Laguerre--Gaussian mode with azimuthal
index ℓ. Classically, that mode carries orbital angular momentum in
proportion to its energy.

After quantization, the result becomes strikingly simple: each
excitation of that mode carries

**energy: ℏω**

and

**orbital angular momentum: ℓℏ.**

The photon did not acquire orbital angular momentum because a tiny
object started orbiting the beam axis. The angular momentum was already
encoded in the spatial structure of the optical mode.

Quantization tells us how that energy and angular momentum are exchanged
in discrete amounts.

This also gives a clean interpretation of the experiments from Post 1.
Classical optics describes the average torque of the beam. Quantum
optics lets us describe the same exchange as individual excitations
transferring angular momentum in units set by ℏ.

**Figure 4 --- One quantum of a twisted mode.** Quantizing an LG mode
does not replace its helical spatial structure with a tiny particle
trajectory. A single excitation of a mode with azimuthal index ℓ has
energy ℏω and orbital angular momentum ℓℏ. The photon's OAM is a
property of the mode it occupies.

## So Where Is the Photon?

Now return to the picture we started with.

A single photon in one perfectly defined monochromatic mode is not
generally a little localized lump. A plane-wave one-photon state is
delocalized just as the corresponding plane-wave mode is.

To make a localized single-photon pulse, we again need a superposition
of modes --- much as a classical localized wave packet requires a
superposition of waves.

But the two ideas must not be confused.

**The wave packet describes the spatial and temporal mode.\
The photon number describes the quantum excitation of that mode.**

We can have a classical-looking field in a localized mode containing
many photons. We can have a one-photon state in a localized wave packet.
And we can have a one-photon excitation of a highly delocalized mode.

The photon is therefore not the little envelope drawn around a few
cycles of an electromagnetic wave.

It is the quantum state of the field.

```{=html}
<!--
Potential final callback:

In Post 1 we started with a beam that somehow kept its shape and ended with light
turning matter. The harmonic oscillator looked almost like a mathematical
coincidence along the way.

It wasn't.

Once the electromagnetic field is decomposed into modes, harmonic oscillators are
exactly what we need to turn classical light into quantum light.
-->
```

------------------------------------------------------------------------

### Feature Image

A single twisted Laguerre--Gaussian optical mode shown as a continuous
helical field, with a subtle ladder of discrete excitation levels beside
or emerging from it. Avoid drawing a photon as a glowing ball travelling
inside the wave. The visual should suggest that quantization changes the
allowed excitation of the mode rather than breaking the mode into
particles.