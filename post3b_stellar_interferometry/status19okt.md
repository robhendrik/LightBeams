# They Wanted to Measure a Star. They Ended Up Questioning the Photon.
## A century of stellar interferometry, a controversy over photons, and the surprising discovery that classical waves cannot explain everything.

A photodetector clicks, and each click is a discrete event. It is tempting to read it as a photon arriving. But treat the light as a classical wave and only the detector quantum mechanically, and the clicks still appear. They come at random times, at a rate set by the intensity of the light. The discreteness can come from the detector rather than from the light.

A bright wave gives many clicks, a weak wave few, and a fluctuating wave gives clicks that follow its fluctuations. The photoelectric effect, the historical argument for photons, can be explained in this way [1]. So the clicks themselves, and the rate at which they arrive, do not require a quantum theory of light.

> **Individual Clicks Don’t Prove Light Is Quantum**

Then what would? Not the clicks of a single detector, but how clicks at different times and places are related to each other: their correlations. These turned up first in an unexpected place, the measurement of the size of a star.

## It All Started with Measuring a Star

A star is so far away that even a large telescope shows it as a point of light. Add atmospheric turbulence and measuring the size of a star directly becomes impossible. Already in the nineteenth century, Hippolyte Fizeau suggested using interference. Every point on the star creates a fringe pattern behind a double slit, shifted slightly depending on its position. Different points on the star emit independently, so the detector adds the intensities of all these patterns. For a source of angular width *w* there is a specific slit separation *d* at which the fringes disappear for the first time. For slightly shorter and slightly larger separations they are visible, so the disappearance is a sharp feature that is (relatively) easy to locate. So, scan the slit separation until the fringes become invisible, and you can determine the angular size of the source. The wider the source, the smaller that separation.

It took until 1920 for this idea to be put into practice. At Mount Wilson in California, Michelson and Pease added a stellar interferometer to the new 100-inch telescope. They aimed it at Betelgeuse, in Orion, and for the first time measured the diameter of a star other than the Sun.

**[Figure 1: as in your draft]**

## A New Way to Measure Starlight

Before and after the Second World War, radio astronomy flourished. As in optical astronomy, radio astronomers wanted a way to measure the angular diameter of celestial sources. Using the principle of Michelson and Pease would mean combining the radio waves from two antennas far apart, with long cables whose phase had to stay stable, while the ionosphere kept disturbing that phase. Hanbury Brown and Twiss proposed to skip the optical combination and move to what they called “intensity interferometry”. Rather than two slits with one detector, they used two detectors at a certain distance, and compared the intensity signals.

Starlight is chaotic: its intensity flickers randomly, so each detector produces what looks like noise. The question is whether the correlation between these two noisy signals carries relevant information.

Take a simple case, two independent point sources *a* and *b* a small angle θ apart. Each detector receives light from both sources: the field at each detector contains a contribution from *a* and one from *b*. The resulting correlation depends on the geometric phase difference between the light from *a* and from *b*. That phase difference is related to their angular separation.

> **Michelson used interference to measure a star. HBT discovered that correlations could do the same job.**

The correlation between the two signals oscillates with the detector separation: it is largest when the detectors sit on top of each other, falls to the level of unrelated signals, and returns to its maximum after one period. The period tells us the angular separation of the sources. For an extended source the oscillations wash out, and the first drop to the unrelated level gives its size, just as the first disappearance of the fringes did for Michelson.

**[Figure 2: `figure2_interferometry.png` (dark version); the old link `figure2_interferometry(2).png` is broken]**

**[Figure 3: as in your draft]**

## Photons Aren’t Supposed to Arrive Together. Or Are They?

HBT quickly realized that their intensity interference was relevant not only for radio waves, but would also work for optical sources. To test it in the laboratory, they used light from a mercury vapour lamp. The title of their 1956 paper was “Correlation between photons in two coherent beams of light”. Where before we spoke about waves, we now bring photons into the game. Other scientists, most prominently Brannen and Ferguson, stated that such a correlation, if it existed, would call for a major revision of fundamental concepts in quantum mechanics. Their own experiment found no correlation. A controversy was born.

> **The classical calculation was never in doubt: the photon picture was.**

Edward Purcell, who had won the Nobel Prize for nuclear magnetic resonance, stepped in. He argued that the two experiments were not in conflict, because the effect is small and Brannen and Ferguson’s apparatus could not have seen it. And the effect, far from requiring a revision of quantum mechanics, is an instructive illustration of its elementary principles. As he wrote to Brannen: “Talking about interference of photons is the easiest way to go astray in such matters. The electromagnetic field is a classical field after all, which is why the Brown–Twiss effect only appears odd if one looks at it from a particle point of view; its oddness being simply the peculiarity of bosons.”

So the controversy was to a large extent about the intuitive picture of a photon as a particle. Or, as HBT wrote of Brannen and Ferguson’s mistake: “The error appears to have arisen because of a too literal reliance on the corpuscular picture of light.”

So how do we explain the HBT effect in a photon picture?

## Purcell: Photons Are Not Independent

In HBT we see the effect as a correlation between detectors at different locations: a correlation in space. The same effect shows up as a correlation between measurements at different moments, a correlation in time. In the photon picture, if each photon arrived independently there would be no correlations. The HBT signal shows that photons tend to group together. Purcell called this clumping; the term we use more commonly is bunching. For chaotic light, the bosonic nature of photons explains this. To understand how it gives information on the size of a source, consider the following argument.

Take two independent sources *a* and *b*, and detectors 1 and 2. A coincidence with one photon from each source can come about in two ways: *a* is detected at 1 and *b* at 2, or *a* at 2 and *b* at 1. If nothing tells us which of the two happened, they are not separate events, and their amplitudes add: they can strengthen or cancel each other. Note the subtlety: this is not interference of photons with each other, but of the amplitudes of two indistinguishable alternatives that lead to the same outcome. The relative phase between them is geometrical, set by the difference between the extra paths to detector 2 from *a* and from *b*; it equals *kd*θ. The random phases of the sources are the same in both alternatives and drop out.

> **Purcell explained why the resulting bunching did not contradict quantum mechanics.**

Adding the two amplitudes gives a cross-source contribution that varies as 1 + cos(*kd*θ). It is twice the independent value when the detectors sit on top of each other, zero at half a period, and back to twice after a full period. This is only the part of the coincidences with one photon from each source. Photons from the same source also coincide, independent of *d*, so the total in Figure 3 stays at or above the independent level.

**[Figure 4: two indistinguishable alternatives; keep or cut, see notes]**

## Two Explanations, One Effect

With the work of Purcell, Mandel and others, the classical description and the quantum view were reconciled. What a classical wave source describes as correlated intensity fluctuations of chaotic light, the quantum picture describes as bunched photons. The HBT effect also triggered further development of how correlations are described in the quantum framework. So bunching, however it is described, does not show that light is quantum: a classical fluctuating wave and a click rate that follows its intensity are enough.

But this triggers a question: if photons can bunch, could they also antibunch? Can we imagine a scheme where photons arrive more regularly than random? If that is possible, it would be an effect that cannot be explained classically. A true signature of the quantum nature of light.

## What If Photons Avoid Each Other Instead?

To compare bunching and antibunching we need one number. We express the correlation as g²: g²(d) for two detectors a distance *d* apart, or g²(τ) for clicks separated by a delay τ. It is the average of the product of the two intensities, I₁I₂, divided by the product of their averages. For unrelated signals it equals 1. Let’s look at what it means for g² to be larger than, equal to, or smaller than 1. Figure 5 shows the three cases. Detector 1 always sees the same noisy signal.

> **And Kimble, Dagenais and Mandel finally measured a correlation that could not be explained without quantizing the light itself.**

In the first case, detector 2 sees the same signal (the splitter splits the incoming light into two equal beams) and g² > 1. In the middle panel, the signal at detector 2 is not correlated to that at detector 1, as if the light came from independent sources, or as if the noise came from the independent detection process at each detector (g² = 1). In the third case, the signal at detector 2 has the opposite fluctuations from detector 1: if one goes high, the other goes low (and vice versa) (g² < 1). With a passive beam splitter, this cannot be explained in a classical model. The light, and not only the detector, would have to be quantized. A stream of photons that arrive at regular spacing, each going to one detector or the other, would give exactly this signal. This would be a true quantum effect, beyond the semiclassical interpretation. But is this a figment of the imagination, or could this type of light really be made?

**[Figure 5: `fig_imagine_g0.png`. Draft caption: Counts per time window at two detectors behind a 50/50 beam splitter. Left: chaotic light, the two counts rise and fall together (g² = 1.94). Middle: a steady source with independent clicks, no relation between the two (g² = 0.99). Right: an imagined source that sends about 12 photons per window, each to one detector or the other, so more at one means fewer at the other (g² = 0.93).]**

## When Photons Avoid Each Other, Classical Physics Falls Short

Imagine a single atom as a light source. The atom is excited by a laser and produces a photon when it falls back to the ground state. Right after emitting, it cannot emit again: it first has to be excited again, which typically takes nanoseconds. Such an isolated atom would produce an antibunched photon stream, with g² smaller than 1. In 1977, Kimble, Dagenais and Mandel at the University of Rochester did the experiment. A laser beam crossed a thin beam of sodium atoms, so thin that only one or two atoms were in the field of view at any moment. They used a beam splitter to split the light from the atoms to two detectors. One detector started a timer upon detecting a photon, the other stopped the timer. The histogram of the measured delays is the correlation g²(τ). Figure 6 shows the idea: one atom, a beam splitter, two detectors, and the correlation built up one delay at a time. They found the fewest pairs at zero delay, and more and more pairs as the delay grew. Corrected for stray laser light, g² at zero delay came out at about 0.4 (not 0, because sometimes more than one atom radiated). This was a clear experimental result that could not be explained by treating light as a classical wave. Kimble, Dagenais and Mandel were the first to observe photon antibunching: direct evidence that the light itself has to be quantized.

**[Figure 6: `fig5_antibunching_quadratures.gif` or `fig5_antibunching.gif`. Draft caption: One atom, a beam splitter and two detectors; the correlation is built up one delay at a time. For an ideal single atom the dip at zero delay goes to about 0; Kimble, Dagenais and Mandel measured about 0.4.]**

## Quantum Optics

In this discussion of the HBT effect we have alternated between light as a wave, light as a stream of indivisible particles, and the bosonic picture in which detector clicks tend to group together. At the time of this story these intuitions co-existed, and Hanbury Brown and Twiss themselves appealed to Bohr’s complementarity: a given experiment can show the wave aspect of light or the particle aspect, but not both. The HBT effect and the controversy around it forced sharper thinking about light as a quantum phenomenon. As we have seen, it prepared the way for experiments on states of light that have no (semi)classical explanation. Some consider this episode the beginning of quantum optics. The first lasers, in 1960, made the question urgent: what are the correlations of photons in a laser beam? The theory of quantum optics was developed by Glauber. In his Nobel lecture he describes the HBT correlation as something altogether new that called for a clear explanation. Of Dirac’s remark that a photon only interferes with itself, he writes: “It is not the photons that interfere physically, it is their probability amplitudes that interfere.” The HBT puzzle set him on the path to the theory that describes the difference between thermal light and laser light. In the next post we follow Glauber and look at the different states of light, and how they fit into one all-encompassing theory. 

And what happened to the ambition of HBT to measure stars? From th lab they took the optical measurements back outside and during the notorious winter of 56/57 they measured the diameter of Sirius. From this success they could build the Narrabri Stellar Intensity Interferometer in Australia. They successfully measured the precise angular diameters of many stars, still considered a landmark result.

Leave a comment, and do not forget to subscribe.

## References

1. Lamb, W. E. and Scully, M. O. (1969). The photoelectric effect without photons. In *Polarisation, Matière et Rayonnement* (Jubilee volume for A. Kastler), Presses Universitaires de France, 363–369. (As in post 2; page range from Silva and Freire 2013, note 100.)
2. Hanbury Brown, R., Jennison, R. C. and Das Gupta, M. K. (1952). Apparent angular sizes of discrete radio sources. *Nature* **170**, 1061.
3. Hanbury Brown, R. and Twiss, R. Q. (1956). Correlation between photons in two coherent beams of light. *Nature* **177**, 27.
4. Brannen, E. and Ferguson, H. I. S. (1956). The question of correlation between photons in coherent light rays. *Nature* **178**, 481.
5. Purcell, E. M. (1956). The question of correlation between photons in coherent light rays. *Nature* **178**, 1449.
6. Hanbury Brown, R. and Twiss, R. Q. (1957). Interferometry of the intensity fluctuations in light. I. Basic theory: the correlation between photons in coherent beams of radiation. *Proc. R. Soc. Lond. A* **242**, 300. (DOI to add.)
7. Mandel, L. (1958). Fluctuations of photon beams and their correlations. *Proc. Phys. Soc.* **72**, 1037.
8. Glauber, R. J. (1963). The quantum theory of optical coherence. *Phys. Rev.* **130**, 2529.
9. Kimble, H. J., Dagenais, M. and Mandel, L. (1977). Photon antibunching in resonance fluorescence. *Phys. Rev. Lett.* **39**, 691.
10. Silva, I. and Freire, O. Jr. (2013). The concept of the photon in question: the controversy surrounding the HBT effect circa 1956–1958. *Historical Studies in the Natural Sciences* **43**(4), 453–491. (Journal and volume to verify.)
11. Glauber, R. J. (2005). One hundred years of light quanta. Nobel Lecture, 8 December 2005. (Print reference to add.)
12. Silva, I. (2019). Source of the Purcell letter to Brannen quoted in section 4. (Full reference to add: not in hand.)

—

## Notes for Rob (delete before publishing)

- **Section 5 / Figure 4:** Fano is removed. The two-alternatives argument is now unattributed. Keep it and Figure 4, or cut to a sentence? Bhatta (2024) notes that calling thermal-light HBT “two-photon interference” is not agreed by everyone, so do not present it as the history or the only explanation.
- **Figure numbers:** the new g² figure is Figure 5 and the atom animation is Figure 6 (the text in section 8 said “Figure 5”). If Figure 4 is cut, renumber. Optional candidates not placed: `fig_scatter_intuition.png`, `fig_g2_intuition.png` (third column is a stand-in source).
- **Closing:** header open; the quote is cut at “that interfere” (the original sentence continues).
- **Not yet verified against scans or sources:** Purcell and HBT quotes (section 4), Kimble’s 0.4 (section 8), Fizeau’s year and the Michelson–Pease numbers (section 2).
- **References:** only works cited in the text are listed (Fano, Bhatta, Rebka and Pound, Michelson and Pease, Fizeau are not). HBT 1957 DOI, Glauber lecture print reference and Silva 2019 are missing; Silva and Freire journal details to verify. In-text reference markers still to be placed (only [1] is in the text).
- **Intro:** not yet explicitly confirmed by you.
- **Optional additions (not in text):** classical limit sentence in section 8 (g²(0) ≥ 1 classically; g²(τ) ≤ g²(0)); detector-speed sentence; Grangier–Roger–Aspect 1986 link to post 2; Hanbury Brown (1991) “no satisfactory mental picture of light” quote; intensity correlations surviving ionospheric scintillation (section 3).
