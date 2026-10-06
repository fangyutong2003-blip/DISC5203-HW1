# Step 05 - Revised Beam Line Loads

Uses the closed mixed-support polygons from revised Step 04. Units: m, m2, kN and kN/m.

Slab G=3.75 kN/m2; Q=5.00 kN/m2. Beam stem G=0.25(d-0.15)*25 kN/m. For each profile interval q(s)=8.75*b(s)+G_stem. Force-equivalent UDL is total force/L. The midspan-moment-equivalent UDL is 8*M(L/2)/L^2, integrating the simply-supported influence line 0.5*min(s,L-s). Neither is a substitute for the actual shear or moment diagram, especially with asymmetric loading.

[Profile CSV](Step_05_Beam_Load_Profiles.csv) stores exact strip areas divided by strip length (0.01 m strips). [Endpoint forces](Step_05_Beam_Endpoint_Loads.csv) are kept separately. Step 06 reads these distributions directly and no longer reconstructs symmetric shapes from two UDLs.

| Beam | L (m) | Area (m2) | Slab G | Stem G | Q | Total force-equivalent UDL | Midspan-moment-equivalent UDL |
|---|---:|---:|---:|---:|---:|---:|---:|
| D01 | 3.30 | 6.1898 | 7.0339 | 3.4375 | 9.3785 | 19.8498 | 21.1621 |
| D02 | 2.00 | 0.8117 | 1.5219 | 3.4375 | 2.0291 | 6.9885 | 7.8947 |
| D03 | 4.00 | 8.2148 | 7.7014 | 3.4375 | 10.2685 | 21.4074 | 23.4949 |
| D04 | 2.45 | 5.4740 | 8.3785 | 3.4375 | 11.1713 | 22.9873 | 24.4814 |
| D05 | 3.10 | 1.3871 | 1.6779 | 3.4375 | 2.2372 | 7.3527 | 8.6577 |
| D06 | 3.10 | 6.6822 | 8.0833 | 2.8125 | 10.7777 | 21.6735 | 24.7629 |
| D07 | 3.10 | 4.9797 | 6.0238 | 2.8125 | 8.0318 | 16.8681 | 17.5059 |
| D08 | 3.60 | 7.7934 | 8.1181 | 2.8125 | 10.8241 | 21.7547 | 27.0765 |
| D09 | 1.10 | 0.6050 | 2.0625 | 2.8125 | 2.7500 | 7.6250 | 7.6250 |
| D10 | 2.45 | 5.6825 | 8.6978 | 3.4375 | 11.5970 | 23.7323 | 26.0441 |
| D11 | 6.05 | 4.9647 | 3.0773 | 3.4375 | 4.1030 | 10.6178 | 12.7795 |
| D12 | 6.05 | 11.9265 | 7.3925 | 2.8125 | 9.8566 | 20.0616 | 23.8059 |
| D13 | 1.50 | 0.4566 | 1.1414 | 2.8125 | 1.5219 | 5.4757 | 6.1554 |
| D14 | 1.15 | 0.6613 | 2.1563 | 2.8125 | 2.8750 | 7.8438 | 7.8438 |
| D15 | 6.05 | 4.9647 | 3.0773 | 3.4375 | 4.1030 | 10.6178 | 12.7795 |
| D16 | 3.60 | 8.2163 | 8.5587 | 2.8125 | 11.4115 | 22.7827 | 28.6854 |
| D17 | 3.00 | 1.2112 | 1.5141 | 2.8125 | 2.0188 | 6.3453 | 6.8907 |
| D18 | 3.60 | 8.2163 | 8.5587 | 2.8125 | 11.4115 | 22.7827 | 28.6854 |
| D19 | 6.05 | 4.9647 | 3.0773 | 3.4375 | 4.1030 | 10.6178 | 12.7795 |
| D20 | 6.05 | 17.6740 | 10.9550 | 2.8125 | 14.6066 | 28.3741 | 32.1184 |
| D21 | 6.05 | 17.6740 | 10.9550 | 2.8125 | 14.6066 | 28.3741 | 32.1184 |
| D22 | 6.05 | 4.9647 | 3.0773 | 3.4375 | 4.1030 | 10.6178 | 12.7795 |
| D23 | 3.60 | 7.2282 | 7.5293 | 3.4375 | 10.0391 | 21.0059 | 25.2536 |
| D24 | 3.00 | 3.6000 | 4.5000 | 3.4375 | 6.0000 | 13.9375 | 13.9375 |
| D25 | 3.60 | 7.2282 | 7.5293 | 3.4375 | 10.0391 | 21.0059 | 25.2536 |

## D18 worked example

L=3.60 m; A=8.216311 m2; average width A/L=2.282309 m. Slab G=3.75A/L=8.558657 kN/m; stem G=2.812500 kN/m; Q=5A/L=11.411543 kN/m. Integrated simply-supported midspan moment=46.470356 kN m.

![D18 profile](HW2_D18_Worked_Line_Load.png)

The edge-condition assumptions and unresolved core area in Step 04 still govern the scope of these loads.
