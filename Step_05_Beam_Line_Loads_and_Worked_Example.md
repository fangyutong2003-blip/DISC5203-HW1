# Step 05 - Beam Line Loads and Worked Example

## 1. Load basis

The adopted slab dead load is 3.75 kN/m2 and the live load is 5.00 kN/m2, consistent with HW1. No finishes value is shown, so no superimposed finish load is invented. Beam self-weight is added as the concrete stem below the 150 mm slab to avoid double-counting the slab thickness:

\[g_{beam}=0.25(d-0.15)(25)\]

For each beam, the total-load-equivalent slab UDL is tributary area times area load divided by beam length. The separately reported moment-equivalent UDL reproduces the simply-supported midspan moment of the sampled triangular/trapezoidal service-load shape; it is not equivalent for local shear.

## 2. Line-load summary

| Beam | Span (m) | Area (m2) | Shape | Slab G (kN/m) | Beam stem G (kN/m) | Total G (kN/m) | Q (kN/m) | G+Q total-load UDL (kN/m) | G+Q midspan-moment UDL (kN/m) |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| D01 | 3.30 | 6.0049 | trapezoidal/truncated + partial cantilever UDL | 6.824 | 3.437 | 10.261 | 9.098 | 19.360 | 20.511 |
| D02 | 2.00 | 2.7052 | triangular/truncated, one-sided | 5.072 | 3.437 | 8.510 | 6.763 | 15.273 | 15.646 |
| D03 | 4.00 | 8.7583 | trapezoidal + cantilever UDL | 8.211 | 3.437 | 11.648 | 10.948 | 22.596 | 24.137 |
| D04 | 2.45 | 4.9717 | triangular/truncated + cantilever UDL | 7.610 | 3.437 | 11.047 | 10.146 | 21.194 | 22.155 |
| D05 | 3.10 | 2.3992 | triangular, one-sided | 2.902 | 3.437 | 6.340 | 3.870 | 10.209 | 12.470 |
| D06 | 3.10 | 8.7323 | two-sided triangular/trapezoidal | 10.563 | 2.812 | 13.376 | 14.084 | 27.460 | 24.789 |
| D07 | 3.10 | 4.4440 | trapezoidal/truncated + short cantilever UDL | 5.376 | 2.812 | 8.188 | 7.168 | 15.356 | 15.843 |
| D08 | 3.60 | 6.4238 | two-sided triangular | 6.691 | 2.812 | 9.504 | 8.922 | 18.426 | 23.539 |
| D09 | 1.10 | 0.6049 | truncated triangular, core-side | 2.062 | 2.812 | 4.875 | 2.750 | 7.624 | 7.625 |
| D10 | 2.45 | 4.7921 | truncated triangular + cantilever UDL | 7.335 | 3.437 | 10.772 | 9.780 | 20.552 | 21.527 |
| D11 | 6.05 | 7.6476 | trapezoidal, one-sided | 4.740 | 3.437 | 8.178 | 6.320 | 14.498 | 17.327 |
| D12 | 6.05 | 10.9761 | two-sided trapezoidal + one-way strip | 6.803 | 2.812 | 9.616 | 9.071 | 18.687 | 21.515 |
| D13 | 1.50 | 1.1248 | truncated triangular, one-sided | 2.812 | 2.812 | 5.624 | 3.749 | 9.374 | 9.380 |
| D14 | 1.15 | 0.6662 | truncated triangular, one-sided | 2.172 | 2.812 | 4.985 | 2.897 | 7.881 | 7.882 |
| D15 | 6.05 | 7.6522 | trapezoidal, one-sided | 4.743 | 3.437 | 8.181 | 6.324 | 14.505 | 17.330 |
| D16 | 3.60 | 6.4915 | two-sided triangular | 6.762 | 2.812 | 9.574 | 9.016 | 18.590 | 23.840 |
| D17 | 3.00 | 1.2160 | partial uniform one-way strip | 1.520 | 2.812 | 4.332 | 2.027 | 6.359 | 6.907 |
| D18 | 3.60 | 6.4812 | two-sided triangular | 6.751 | 2.812 | 9.564 | 9.002 | 18.565 | 23.822 |
| D19 | 6.05 | 7.6513 | trapezoidal, one-sided | 4.743 | 3.437 | 8.180 | 6.323 | 14.503 | 17.329 |
| D20 | 6.05 | 16.7187 | trapezoidal + one-way UDL, two-sided | 10.363 | 2.812 | 13.175 | 13.817 | 26.992 | 29.824 |
| D21 | 6.05 | 16.7174 | trapezoidal + one-way UDL, two-sided | 10.362 | 2.812 | 13.175 | 13.816 | 26.991 | 29.822 |
| D22 | 6.05 | 7.6518 | trapezoidal, one-sided | 4.743 | 3.437 | 8.180 | 6.324 | 14.504 | 17.330 |
| D23 | 3.60 | 6.3483 | triangular + partial cantilever UDL | 6.613 | 3.437 | 10.050 | 8.817 | 18.867 | 22.785 |
| D24 | 3.00 | 3.6000 | partial cantilever UDL only | 4.500 | 3.437 | 7.938 | 6.000 | 13.938 | 13.937 |
| D25 | 3.60 | 6.3538 | triangular + partial cantilever UDL | 6.619 | 3.437 | 10.056 | 8.825 | 18.881 | 22.801 |

## 3. Worked example - D18

D18 is the right-hand span of marked Beam B. It is an interior beam between P5 and P9, so both slab sides contribute. The 45-degree construction produces a combined triangular/trapezoidal distribution rather than a uniform peak load.

- Span: L = 3.60 m.
- Tributary area: A = 6.4812 m2.
- Mean tributary width: A/L = 1.8003 m.
- Slab dead-load UDL by total load: 3.75A/L = 6.751 kN/m.
- Beam-stem self-weight: 2.812 kN/m.
- Total dead-load UDL: 9.564 kN/m.
- Live-load UDL by total load: 5.00A/L = 9.002 kN/m.
- Service UDL by total load: 18.565 kN/m.
- Service UDL reproducing simply-supported midspan moment: 23.822 kN/m.

![D18 worked line load](HW2_D18_Worked_Line_Load.png)

The actual non-uniform load will be retained for the OpenSees discretised model. The total-load UDL is used for reaction checks, while the midspan-moment-equivalent UDL is used only for the stated hand moment comparison.

## 4. Verification

- Every D01-D25 beam has one census row and one line-load row.
- The sum of beam and direct-wall tributary areas reconciles to the 179.250 m2 HW1 ordinary slab area.
- Slab dead and live beam loads reconcile to beam tributary area multiplied by 3.75 and 5.00 kN/m2 respectively.
- Beam-stem self-weight uses metres and kN consistently and excludes the slab thickness already counted in the area load.
- Total-load and moment-equivalent UDLs are labelled separately because they answer different questions.

## 5. Assumptions to freeze before Task 3

1. Confirm D05/D11/D19 as Beam A and D16-D18 as Beam B.
2. Confirm the image-derived 250x600 and 250x700 beam sections.
3. Confirm the core-side P4/P6 support interpretation and whether D14 receives P6 edge-strip load.
4. Confirm that no finishes load should be added.
5. Freeze the non-uniform line-load profiles before generating the OpenSees briefing and model files.
