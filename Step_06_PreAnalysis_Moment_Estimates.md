# Step 06 - Pre-analysis Moment Estimates

**Date:** 12 October 2026  
**Load case:** Service load, \(G_k+Q_k\)  
**Purpose:** Order-of-magnitude screening before comparison with the OpenSees results

The actual beam loads are non-uniform and the selected beams are continuous. The expression \(qL^2/8\) is therefore used only as a transparent simply supported reference scale. It is not treated as the final continuous-beam moment.

## Beam A

The governing long span is D19 or D11:

\[
L=6.05\ \mathrm{m},\qquad q_{M,eq}=12.7795\ \mathrm{kN/m}.
\]

Using the moment-equivalent service line load from Step 05:

\[
M_{ss}=\frac{qL^2}{8}
=\frac{12.7795(6.05)^2}{8}
=58.47\ \mathrm{kN\,m}.
\]

The expected response is positive sagging within the spans and negative hogging over the internal supports. The actual positive and negative moments need not equal 58.47 kN m because continuity and support stiffness redistribute moment.

## Beam B

The governing exterior span is D16 or D18:

\[
L=3.60\ \mathrm{m},\qquad q_{M,eq}=28.6854\ \mathrm{kN/m}.
\]

\[
M_{ss}=\frac{qL^2}{8}
=\frac{28.6854(3.60)^2}{8}
=46.47\ \mathrm{kN\,m}.
\]

Positive sagging is expected within the exterior spans and negative hogging over the internal supports. The reference value is a screening scale rather than an exact OpenSees target.

## Comparison with the final models

| Beam | Simply supported screening scale (kN m) | Standalone \(M^+\) (kN m) | Standalone \(M^-\) (kN m) | Grid \(M^+\) (kN m) | Grid \(M^-\) (kN m) |
|---|---:|---:|---:|---:|---:|
| A | 58.470 | 35.629 | -50.301 | 29.407 | -46.932 |
| B | 46.470 | 37.046 | -22.291 | 27.314 | -24.907 |

All final peak moments are of the same order as the pre-analysis scales. The sign pattern also agrees with the expected continuous-beam behaviour.
