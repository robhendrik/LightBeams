# Michelson and Hanbury Brown–Twiss: Handwritten Derivation

*Transcription of eight handwritten pages, arranged by the circled page numbers (1–8). Mathematical notation has been typeset and obvious shorthand expanded only where necessary for legibility. The transcription is kept separate from the physics and notation review below.*

## Page 1 — Geometry, Fields and Brightness

Two sources at angular positions $\xi_a,\xi_b$, with

$$
\xi_a-\xi_b=\Theta.
$$

- **Michelson:** two slits at separation $d=d_1-d_2$, detector at position $\delta$.
- **HBT:** two detectors at separation $d$.

### Distances from sources to slits/detectors

Between paths 1 and 2:

$$
\Delta \ell_a=\xi_a d,\qquad \Delta \ell_b=\xi_b d.
$$

From slits to the Michelson detector:

$$
\Delta\ell=d\delta.
$$

Thus, schematically, the relative optical path differences are:

**Michelson**, source $i$, slit $j$, detector at $\delta$:

$$
\ell\ \text{(relative)}=(\xi_i+\delta)d_j.
$$

**HBT**, source $i$, detector $j$:

$$
\ell\ \text{(relative)}=\xi_i d_j.
$$

### Fields

$$
E_a^{(i)}=\alpha\,e^{ik\ell_{ai}}e^{i\phi_a},
\qquad
E_b^{(i)}=\beta\,e^{ik\ell_{bi}}e^{i\phi_b}.
$$

The independent source phases obey

$$
\left\langle e^{i\Delta\phi}\right\rangle=0,
\qquad
\left\langle e^{2i\Delta\phi}\right\rangle=0,
\qquad \Delta\phi=\phi_a-\phi_b.
$$

Source intensities:

$$
I_a=|\alpha|^2,\qquad I_b=|\beta|^2.
$$

The notes also write a contrast-like quantity

$$
V_0=\frac{|I_a-I_b|}{I_a+I_b}.
$$

*This is the minimum fringe visibility for unequal point sources, attained when their fringe contributions are out of phase ($kd\Theta=(2n+1)\pi$). The absolute value makes visibility nonnegative.*

## Page 2 — Michelson, Two Point Sources

The field at the recombination detector consists of four contributions, one from each source through each slit:

$$
E=E_a^{(1)}+E_b^{(1)}+E_a^{(2)}+E_b^{(2)}.
$$

The measured intensity is

$$
I(\delta)=EE^*.
$$

Expansion gives 16 terms. Eight mixed-source terms vanish under ensemble averaging because the two sources have uncorrelated phases. Four terms are individual slit/source intensities, and four are interference terms connecting the two slits for the same source:

$$
\begin{aligned}
\langle I(\delta)\rangle={}&
\langle|E_a^{(1)}|^2\rangle+\langle|E_a^{(2)}|^2\rangle
+\langle|E_b^{(1)}|^2\rangle+\langle|E_b^{(2)}|^2\rangle\\
&+\left\langle E_a^{(1)}E_a^{(2)*}+E_a^{(2)}E_a^{(1)*}\right\rangle\\
&+\left\langle E_b^{(1)}E_b^{(2)*}+E_b^{(2)}E_b^{(1)*}\right\rangle.
\end{aligned}
$$

For the path differences of page 1:

$$
\boxed{
\langle I(\delta)\rangle
=2(I_a+I_b)
+2I_a\cos\!\big(kd(\xi_a+\delta)\big)
+2I_b\cos\!\big(kd(\xi_b+\delta)\big).
}
$$

Let $\Theta=\xi_a-\xi_b$. Combining the two cosines yields

$$
\boxed{
\langle I(\delta)\rangle
=2(I_a+I_b)+2A(d)\cos(kd\delta+\varphi(d)),
}
$$

where

$$
A(d)=\sqrt{I_a^2+I_b^2+2I_aI_b\cos(kd\Theta)}.
$$

The handwritten sketch shows the fringe amplitude falling toward $|I_a-I_b|$ at $kd\Theta=\pi$, then rising again. The detector coordinate $\delta$ sets the fringe position; the slit separation $d$ changes the fringe amplitude.

## Page 3 — Michelson, Extended Source

Replace the two point sources by a continuous angular intensity distribution $B(\xi)$:

$$
\langle I(\delta)\rangle
=2\int B(\xi)\,d\xi
+2\int B(\xi)\cos\big(kd(\xi+\delta)\big)\,d\xi.
$$

We retain the same two-slit normalization as on page 2: $B(\xi)$ represents the brightness contribution of one source direction through one slit, so both the background and fringe terms carry a factor of 2.

Using the cosine addition identity, the notes define

$$
I_{\mathrm{tot}}=\int B(\xi)\,d\xi,
$$

$$
C(d)=\int B(\xi)\cos(kd\xi)\,d\xi,
$$

$$
S(d)=\int B(\xi)\sin(kd\xi)\,d\xi.
$$

The expansion **with the stated definitions** is

$$
\boxed{
\langle I(\delta)\rangle
=2I_{\mathrm{tot}}+2C(d)\cos(kd\delta)-2S(d)\sin(kd\delta).
}
$$

*With the chosen geometric convention, positive $\xi$ shifts the fringe maximum toward negative $\delta$. Thus the sine term has a minus sign. The handwritten plus sign has been corrected here; see review.*

Write this as one cosine:

$$
\langle I(\delta)\rangle
=2I_{\mathrm{tot}}+2A(d)\cos(kd\delta+\varphi(d)),
$$

with

$$
A(d)=\sqrt{C(d)^2+S(d)^2},\qquad
\varphi(d)=\operatorname{atan2}(S(d),C(d)).
$$

For an even source distribution centered at the angular origin, $S(d)=0$. **Strictly, $A(d)=|C(d)|$**, not $C(d)$ when the latter is negative.

In general, the fringe amplitude **and phase** determine the complex visibility:

$$
\boxed{
C(d)+iS(d)=\int B(\xi)e^{ikd\xi}\,d\xi.
}
$$

With sufficient baseline coverage, its inverse Fourier transform reconstructs the angular brightness distribution:

$$
B(\xi)=\frac{k}{2\pi}\int_{-\infty}^{\infty}
\big[C(d)+iS(d)\big]e^{-ikd\xi}\,dd.
$$

Each baseline $d$ supplies one spatial Fourier component at frequency $kd$.

## Page 4 — HBT: Local Intensities and Their Squares

HBT measures intensities $I_1(d)$ and $I_2(d)$. Compare

$$
\langle I_1^2\rangle,\quad \langle I_2^2\rangle,\quad
\langle I_1\rangle^2,\quad \langle I_2\rangle^2,\quad
\langle I_1I_2\rangle.
$$

At detector $i$, the instantaneous intensity is

$$
\begin{aligned}
I_i&=(E_a^{(i)}+E_b^{(i)})(E_a^{(i)*}+E_b^{(i)*})\\
&=|E_a^{(i)}|^2+|E_b^{(i)}|^2
+2\operatorname{Re}\!\left[E_a^{(i)}E_b^{(i)*}\right].
\end{aligned}
$$

Averaging removes the mixed-source interference terms:

$$
\langle I_i\rangle
=\langle I_a^{(i)}\rangle+\langle I_b^{(i)}\rangle
=I_a+I_b.
$$

For the squared intensity, there are 16 terms. Six survive averaging over the independent random source phases:

$$
\boxed{
\langle I_i^2\rangle
=\langle (I_a^{(i)})^2\rangle
+\langle (I_b^{(i)})^2\rangle
+4\langle I_a^{(i)}\rangle\langle I_b^{(i)}\rangle.
}
$$

For ideal chaotic light with Gaussian field statistics,

$$
\langle (I_a^{(i)})^2\rangle=2\langle I_a^{(i)}\rangle^2,
\qquad
\langle (I_b^{(i)})^2\rangle=2\langle I_b^{(i)}\rangle^2.
$$

Therefore

$$
\begin{aligned}
\langle I_i^2\rangle
&=2I_a^2+2I_b^2+4I_aI_b\\
&=2(I_a+I_b)^2\\
&=2\langle I_i\rangle^2.
\end{aligned}
$$

The sum of independent Gaussian chaotic fields is itself Gaussian chaotic light.

**Next:** the cross-intensity correlation $\langle I_1I_2\rangle$.

## Page 5 — HBT: The Six Surviving Cross-Detector Terms

The two detector intensities are

$$
I_1=(E_a^{(1)}+E_b^{(1)})(E_a^{(1)*}+E_b^{(1)*}),
$$

$$
I_2=(E_a^{(2)}+E_b^{(2)})(E_a^{(2)*}+E_b^{(2)*}).
$$

Their product has 16 terms. Ten average to zero for independent circular random phases, leaving six:

$$
\begin{aligned}
\langle I_1I_2\rangle={}&
\langle I_a^{(1)}I_a^{(2)}\rangle
+\langle I_b^{(1)}I_b^{(2)}\rangle\\
&+\langle I_a^{(1)}I_b^{(2)}\rangle
+\langle I_b^{(1)}I_a^{(2)}\rangle\\
&+\left\langle E_a^{(1)}E_b^{(1)*}E_a^{(2)*}E_b^{(2)}\right\rangle\\
&+\left\langle E_a^{(1)*}E_b^{(1)}E_a^{(2)}E_b^{(2)*}\right\rangle.
\end{aligned}
$$

Only the last two terms retain the **relative geometrical phase** of the two sources. Using the propagation phases:

$$
\begin{aligned}
&\left\langle E_a^{(1)}E_b^{(1)*}E_a^{(2)*}E_b^{(2)}\right\rangle
+\text{c.c.}\\
&\qquad=2I_aI_b\cos\!\left(kd(\xi_a-\xi_b)\right)\\
&\qquad=\boxed{2I_aI_b\cos(kd\Theta)}.
\end{aligned}
$$

The handwritten derivation expresses this as the sum of two conjugate exponentials whose random source phases cancel.

## Page 6 — HBT: Two Chaotic Point Sources

Collect the four intensity terms and the two phase-dependent terms:

$$
\begin{aligned}
\langle I_1I_2\rangle={}&
\underbrace{\langle(I_a^{(1)}+I_b^{(1)})(I_a^{(2)}+I_b^{(2)})\rangle}_{\text{four intensity-product terms}}\\
&+2I_aI_b\cos(kd\Theta).
\end{aligned}
$$

For independent, ideal chaotic point sources and equally efficient detectors:

$$
\langle I_a^{(1)}\rangle=\langle I_a^{(2)}\rangle=I_a,
\qquad
\langle I_b^{(1)}\rangle=\langle I_b^{(2)}\rangle=I_b.
$$

Same-source intensity correlations carry the thermal factor of 2:

$$
\langle I_a^{(1)}I_a^{(2)}\rangle=2I_a^2,
\qquad
\langle I_b^{(1)}I_b^{(2)}\rangle=2I_b^2.
$$

Different-source intensity correlations factorize:

$$
\langle I_a^{(1)}I_b^{(2)}\rangle
=\langle I_b^{(1)}I_a^{(2)}\rangle=I_aI_b.
$$

Hence

$$
\boxed{
\langle I_1I_2\rangle
=2I_a^2+2I_b^2+2I_aI_b+2I_aI_b\cos(kd\Theta).
}
$$

Normalize by $\langle I_1\rangle\langle I_2\rangle=(I_a+I_b)^2$:

$$
\boxed{
g^{(2)}(d)
=1+\frac{I_a^2+I_b^2}{(I_a+I_b)^2}
+\frac{2I_aI_b}{(I_a+I_b)^2}\cos(kd\Theta).
}
$$

For equally bright sources, $I_a=I_b$:

$$
\begin{aligned}
g^{(2)}(d)
&=1+\frac12+\frac12\cos(kd\Theta)\\
&=\frac32+\frac12\cos(kd\Theta)\\
&=\boxed{1+\cos^2\!\left(\frac{kd\Theta}{2}\right)}.
\end{aligned}
$$

## Page 7 — HBT: Extended Source

Every pair of angular positions $\xi,\xi'$ contributes. Define

$$
I_0=\langle I_1\rangle=\langle I_2\rangle
=\int B(\xi)\,d\xi.
$$

The two-source sum generalizes to

$$
\boxed{
g^{(2)}(d)=1+\frac{1}{I_0^2}
\iint B(\xi)B(\xi')
\cos\big(kd(\xi-\xi')\big)\,d\xi\,d\xi'.
}
$$

Using $\cos(u-v)=\cos u\cos v+\sin u\sin v$, the double integral becomes

$$
\begin{aligned}
&\iint B(\xi)B(\xi')\cos\big(kd(\xi-\xi')\big)
\,d\xi\,d\xi'\\
&=\left[\int B(\xi)\cos(kd\xi)\,d\xi\right]^2
+\left[\int B(\xi)\sin(kd\xi)\,d\xi\right]^2\\
&=C(d)^2+S(d)^2.
\end{aligned}
$$

Therefore

$$
\boxed{g^{(2)}(d)=1+\frac{C(d)^2+S(d)^2}{I_0^2}.}
$$

The numerator is the Fourier magnitude squared:

$$
\begin{aligned}
C(d)^2+S(d)^2
&=\left|\int B(\xi)e^{ikd\xi}\,d\xi\right|^2\\
&=\iint B(\xi)B(\xi')
 e^{ikd(\xi-\xi')}\,d\xi\,d\xi'.
\end{aligned}
$$

**Conclusion in the notes:** HBT does not retain the object's absolute position or the full Fourier phase; its result is a *brightness autocorrelation* measurement. See the qualification about orientation in the review.

## Page 8 — Brightness Autocorrelation

Define the angular brightness autocorrelation:

$$
\boxed{
A(\Delta\xi)=\int B(\xi)B(\xi-\Delta\xi)\,d\xi.
}
$$

Let

$$
F(d)=\int B(\xi)e^{ikd\xi}\,d\xi.
$$

The HBT result is

$$
\boxed{g^{(2)}(d)=1+\frac{|F(d)|^2}{I_0^2}.}
$$

Expanding the squared magnitude,

$$
\begin{aligned}
|F(d)|^2
&=\left|\int B(\xi)e^{ikd\xi}\,d\xi\right|^2\\
&=\iint B(\xi)B(\xi')e^{ikd(\xi-\xi')}\,d\xi\,d\xi'\\
&=\int A(\Delta\xi)e^{ikd\Delta\xi}\,d(\Delta\xi).
\end{aligned}
$$

Thus

$$
\boxed{
g^{(2)}(d)=1+\frac{\mathcal F[A](kd)}{I_0^2},
}
$$

where the Fourier convention is $\mathcal F[A](q)=\int A(\Delta\xi)e^{iq\Delta\xi}\,d(\Delta\xi)$.

**HBT measures the Fourier transform of the brightness autocorrelation.**

---

# Consistency and Physics Review

The following are **review notes**, not silent alterations of the handwritten argument.

1. **Page 1 — $V_0$ clarified as minimum visibility.** The original signed expression is the intensity imbalance; its absolute value is the minimum Michelson fringe visibility. For the two-point-source visibility obtained on page 2, the normalized fringe amplitude is
   $$
   V(d)=\frac{\sqrt{I_a^2+I_b^2+2I_aI_b\cos(kd\Theta)}}{I_a+I_b}.
   $$
   Its minimum is $|I_a-I_b|/(I_a+I_b)$, occurring at $kd\Theta=(2n+1)\pi$. This is the intended meaning of $V_0$.

2. **Page 3 — sign convention resolved.** We retain $d(\xi+\delta)$: increasing source angle $\xi$ shifts the fringe toward negative screen angle $\delta$. Accordingly, the correct expansion is $C(d)\cos(kd\delta)-S(d)\sin(kd\delta)$. The handwritten plus sign was corrected in the typeset derivation. The single-cosine form with $\varphi=\operatorname{atan2}(S,C)$ is consistent with this choice.

3. **Pages 2–3 — normalization resolved.** Keep the two-slit factor of 2 in both the constant background and interference terms on page 3, consistent with page 2. The revised page 3 does this without redefining $B(\xi)$. The HBT section uses its own detector-intensity normalization, $I_0=\int B(\xi)\,d\xi$, as appropriate for one detector.

4. **Page 3 — even source and fringe sign.** For a centered even source, $S(d)=0$, but the *nonnegative* fringe amplitude is $|C(d)|$. The sign of $C$ represents a $\pi$ phase reversal.

5. **Pages 4–6 — random phase alone does not imply the thermal factor of two.** The identities $\langle I_a^2\rangle=2\langle I_a\rangle^2$ and $\langle I_a^{(1)}I_a^{(2)}\rangle=2I_a^2$ require ideal circular complex Gaussian chaotic fields and (for the cross-detector equality) full spatial coherence for each individual point source. Incoherence between sources by itself is insufficient.

6. **Page 5 — why six terms survive.** The criterion is equal numbers of $E$ and $E^*$ *for each independent source* in a product, assuming independent uniformly random phases. There are four intensity-product terms and two conjugate phase-sensitive terms. This counting is correct.

7. **Page 6 — the “naive” contribution is not just $\langle I_1\rangle\langle I_2\rangle$.** The four phase-independent intensity terms sum to $2I_a^2+2I_b^2+2I_aI_b$, which for equal sources is $3I_a^2\times2=6I_a^2$, yielding $3/2$ after normalization. The naive *product of mean intensities* gives 1 instead. The distinction matters for the article's explanatory narrative.

8. **Pages 7–8 — passage to a continuous source.** The formula is correct for an ideal spatially incoherent, Gaussian chaotic source (narrowband, zero detection-time delay, matched detector responses). The continuum derivation is safest when obtained from the Gaussian field coherence relation $\langle I_1I_2\rangle=I_0^2+|\langle E_1^*E_2\rangle|^2$. Treating the $\xi=\xi'$ line as a finite “diagonal contribution” in an ordinary continuous double integral would be misleading: that line has zero measure. The discrete two-source result nevertheless follows exactly when $B$ is a sum of delta functions.

9. **Page 7 — orientation claim is too broad.** HBT magnitude-only measurements lose absolute position and cannot distinguish a brightness distribution from its mirror image (or, in two dimensions, its inversion). They do **not** necessarily lose all orientation information: a rotated asymmetric source generally has a rotated Fourier-magnitude pattern when baseline directions are sampled. The safe conclusion is loss of Fourier phase and non-uniqueness of reconstruction.

10. **Page 8 — Fourier-transform notation.** $\mathcal F[A](kd)$ is real and nonnegative because $A$ is an autocorrelation. Its inverse transform returns $A$, not uniquely $B$. Any $2\pi$ factors depend on Fourier convention.

11. **Physical measurement caveat.** The ideal formula $g^{(2)}(0)=2$ assumes temporal resolution sufficient to resolve the light's coherence time. Finite detector timing and bandwidth reduce the observed excess correlation without changing the underlying spatial Fourier relation.

## Resolved Editorial Conventions

- $V_0=|I_a-I_b|/(I_a+I_b)$ denotes **minimum fringe visibility**, not visibility at zero baseline.
- The path convention is $d(\xi+\delta)$: a positive source displacement shifts the fringe in the negative detector-coordinate direction.
- The Michelson two-slit factor of 2 is retained on pages 2 and 3, with no silent change in the definition of $B$.
- HBT loses Fourier phase and absolute position, and has an inversion ambiguity, but directional baseline sampling can still reveal orientation information.

The main remaining qualifications concern the ideal Gaussian-chaotic-light assumptions, measurement bandwidth, and the difference between magnitude-only and phase-resolved imaging.

[pdf of handwritten notes](Michelson-HBT_Handwritten_notes.pdf)