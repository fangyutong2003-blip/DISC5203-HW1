# Step 05 - Coefficient-Route versus Area-Route Check

This independent check applies HKConcrete 2013 Table 6.7 only to clean rectangular, four-edge, two-way panels P2, P3, P7 and P9. The coefficient-route equivalent slab line load is q = 0.75 beta_v n l_x, where n=8.75 kN/m2, l_x is the short span and alpha=l_y/l_x. Beam-stem self-weight is excluded from both routes.

The table values are linearly interpolated in alpha. beta_vx applies to edges of length l_y; beta_vy applies to edges of length l_x. The official source is the Hong Kong Buildings Department Code of Practice for Structural Use of Concrete 2013 (2020 Edition), Table 6.7: https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/CoP_SUC2013e.pdf

| Panel | Edge | Supports | beta_v | Coefficient q (kN/m) | Area q (kN/m) | Difference |
|---|---|---|---:|---:|---:|---:|
| P2 | top C | D04;W_T3 | 0.4084 | 8.3081 | 8.9571 | -7.2% |
| P2 | bottom C | D08 | 0.4084 | 8.3081 | 8.9571 | -7.2% |
| P2 | left S | D05 | 0.2400 | 4.8825 | 3.9152 | +24.7% |
| P2 | right C | D06 | 0.3600 | 7.3238 | 6.7812 | +8.0% |
| P3 | left S | D11 | 0.3544 | 8.3738 | 7.1803 | +16.6% |
| P3 | right C | D12 | 0.5389 | 12.7313 | 12.4366 | +2.4% |
| P3 | bottom C | D16 | 0.3600 | 8.5050 | 9.9851 | -14.8% |
| P3 | top C | D08 | 0.3600 | 8.5050 | 9.9851 | -14.8% |
| P7 | left S | D19 | 0.3544 | 8.3738 | 7.1803 | +16.6% |
| P7 | right C | D20 | 0.5389 | 12.7313 | 12.4366 | +2.4% |
| P7 | bottom C | D23 | 0.3600 | 8.5050 | 9.9851 | -14.8% |
| P7 | top C | D16 | 0.3600 | 8.5050 | 9.9851 | -14.8% |
| P9 | right S | D22 | 0.3544 | 8.3738 | 7.1803 | +16.6% |
| P9 | left C | D21 | 0.5389 | 12.7313 | 12.4366 | +2.4% |
| P9 | bottom C | D25 | 0.3600 | 8.5050 | 9.9851 | -14.8% |
| P9 | top C | D18 | 0.3600 | 8.5050 | 9.9851 | -14.8% |

## Panel force closure

| Panel | alpha | Panel load (kN) | Coefficient edge sum (kN) | Area edge sum (kN) | Coefficient closure | Area closure |
|---|---:|---:|---:|---:|---:|---:|
| P2 | 1.1613 | 97.6500 | 97.6579 | 97.6500 | 100.0% | 100.0% |
| P3 | 1.6806 | 190.5750 | 188.9212 | 190.5750 | 99.1% | 100.0% |
| P7 | 1.6806 | 190.5750 | 188.9212 | 190.5750 | 99.1% | 100.0% |
| P9 | 1.6806 | 190.5750 | 188.9212 | 190.5750 | 99.1% | 100.0% |

The area route closes exactly by construction. Rounded code coefficients are approximate and are used here as a scale check, not to overwrite the closed polygons. Irregular P1/P5, one-way P4/P6/P8, openings, split core supports and cantilevers are outside this table check; applying Table 6.7 to them would imply unsupported assumptions.
