# How Do We Know Light Is Really Quantum?

*A detector click isn't enough. The real evidence appears when we compare what detectors see.*

In the previous post, we saw how quantizing the electromagnetic field leads naturally to photons: discrete excitations of its modes, each carrying energy ℏω. But how do we know that light really behaves this way? After all, a detector responding to light produces individual clicks, even when the incoming light is described as a classical electromagnetic wave. A semiclassical model, combining classical light with a quantum detector, can already explain these discrete detection events. A click alone is therefore not enough to establish that the light itself is quantum.

The difference emerges when we start comparing detection events. Instead of looking at individual clicks, we can study correlations between detections in different optical modes, or between detections at different times. Some of these correlations can still be explained by classical electromagnetic waves. Others cannot. They reveal behaviour that requires a quantum description of light itself. **And that gives us a way to answer our original question: how do we know that light is really quantum?**


## A Click Is Not Proof of a Photon

Almost everyone has seen the famous double-slit experiment. Light passes through two narrow openings and reaches a screen, where individual dots appear, seemingly at random. As more dots accumulate, a familiar interference pattern slowly emerges. This is often presented as one of the clearest demonstrations of the wave-particle duality of light: each photon arrives as a particle, yet somehow interferes like a wave.

But does this experiment really demonstrate that light consists of photons?

Consider what happens if we describe the incoming light as an ordinary classical electromagnetic wave. The wave passes through both slits, and the two contributions interfere at the screen. If their electric fields are E₁ and E₂, the resulting intensity is proportional to

$$
I(x) \propto |E_1(x)+E_2(x)|^2.
$$

Nothing quantum is needed for this interference pattern. It follows directly from Maxwell's equations.

Now consider the screen itself. Its atoms and electrons are quantum systems, and they can absorb energy through discrete transitions. Even when illuminated by a continuous classical field, an ideal photodetector can produce individual, randomly timed clicks. The probability of a click in a short time interval depends on the local light intensity.

Put these two things together. The classical field determines where the intensity is high or low, while the quantum detector produces individual detection events with probabilities proportional to that intensity. At first, the dots appear randomly scattered. As their number increases, they gradually reveal the familiar interference pattern.

**We have reproduced the point-by-point buildup of the double-slit interference pattern without quantizing the electromagnetic field.**

This is not a new interpretation invented for our argument. Semiclassical photodetection theory was developed by Mandel, Sudarshan and Wolf [1], and explicit semiclassical simulations of the double-slit experiment have reproduced this gradual buildup [2].

Of course, this does not mean that light is not quantum. Nor does it mean that every experiment involving individual photons can be explained semiclassically. It means something more specific: the interference pattern and its gradual appearance through individual detection events do not, by themselves, establish that the electromagnetic field is quantized.

So what additional measurement would allow us to distinguish classical light from genuinely quantum light?

### Figure 1 — Proposed, Image Not Yet Selected

**Placeholder:** Four progressively accumulated detection screens (e.g., 100, 1,000, 10,000, 100,000 events) showing an interference pattern emerging from discrete spots. Prefer a clearly labeled author-created semiclassical simulation. A famous Tonomura sequence shows **electrons**, not photons; do not miscaption that image as photodetection. Source and reuse rights to be checked once an image is selected.

**Draft caption:** *Figure 1. An interference pattern, one click at a time.* Individual detection events appear randomly on a screen. As more events accumulate, the familiar double-slit interference pattern emerges. This gradual buildup does not, by itself, require a quantized electromagnetic field: a classical wave combined with a quantum detector can produce the same visible pattern.

### References for This Section

[1] Mandel, L., Sudarshan, E. C. G., and Wolf, E. (1964). *Theory of Photoelectric Detection of Light Fluctuations.* Proceedings of the Physical Society **84**, 435–444. https://doi.org/10.1088/0370-1328/84/3/313

[2] Rashkovskiy, S. A. (2015). *Semiclassical Simulation of the Double-Slit Experiments with Single Photons.* Progress of Theoretical and Experimental Physics **2015**, 123A03. https://doi.org/10.1093/ptep/ptv162

### Editorial Continuity Notes (Not Article Prose)

- **Agreed story arc:** Open with the iconic point-by-point double-slit buildup, show why a classical field plus quantum detector explains the visible distribution, develop cross-mode and temporal detection correlations through the beam-splitter sections, and **return at the end** to explain what additional evidence establishes nonclassical light.
- **End-of-article experimental anchor:** Grangier, Roger & Aspect (1986), *Experimental Evidence for a Photon Anticorrelation Effect on a Beam Splitter: A New Light on Single-Photon Interferences*, Europhysics Letters **1**, 173–179, https://doi.org/10.1209/0295-5075/1/4/004 . Their experiments involve interference and a separate beam-splitter anticorrelation test, **not** a literal double-slit screen with measured spatial-dot correlations. Make this explicit.
- Distinguish a **weak classical source** from a **prepared single-photon state**; the screen image alone does not certify preparation or quantum statistics.
- The following section centers a **50/50 beam splitter** as a way to compare two detector outputs, then develops lossless two-mode unitary transformations, with polarization and HG–LG converters as brief connections to Post 1. Quantization and correlations follow.
- **Figure renumbering:** New double-slit sequence is Figure 1; former mode-mixing figure becomes Figure 2, former unitarity figure becomes Figure 3, and former one/two-photon figure becomes Figure 4. Existing outline is preserved separately.
- **Status (12 October 2026):** Intro is the agreed baseline; first body section is a draft for review; figure, copyright, and final sources need editorial review.


## Beam Splitter — Development Notes (Not Yet Drafted)

**Current editorial decision (12 October 2026):** The beam splitter is the central worked example after the semiclassical double-slit section. The narrative goal is to understand *correlations between outputs*, not to make mode conversion the main story.

- Begin with two classical input amplitudes and a lossless 50/50 beam splitter. When light enters only one input, the power divides equally; when both inputs are illuminated, their relative phase matters.
- Write the two-output relation as a 2×2 matrix and use conservation of total input power to motivate a unitary transformation. The intentionally incorrect equal-sign matrix is a possible illustration; its failure is exposed with two equal input beams.
- Briefly connect the same general lossless two-mode mathematics to wave plates and the HG–LG converter from Post 1. These optical components are **not physically identical** to a spatial beam splitter.
- Then use the creation and annihilation operators introduced in Post 2. The operator combinations in a passive beam-splitter coupling, such as `a†b + b†a`, have an intuitive meaning: remove an excitation from one mode and add it to the other, conserving total photon number.
- For a single excitation, the beam splitter gives a coherent superposition of two output-mode possibilities. **Do not describe its unitary evolution as a random photon jump:** probabilities enter when outcomes are measured.
- The two-photon case and interference of alternative histories lead to HOM correlations. Later, distinguish correlations between spatial output modes from correlations at different detection times.
- Return in the concluding section to the opening double-slit question. Grangier–Roger–Aspect (1986) is a complementary demonstration involving interferometry and antibunching, not a literal double-slit screen with spatial coincidence measurements.

**Open:** How much of the coupling Hamiltonian belongs in the main article versus a brief aside? Whether to combine the classical matrix and quantum-operator discussion in one section or retain them as two sections. No beam-splitter prose has yet been agreed.

**Source outline:** See `article_post3_outline(1).md` for the provisional full structure and earlier figure plan; its numbering predates the new double-slit Figure 1.
