# HW1 Checkpoint Report

**Course:** DISC 5203 - Computer (& AI) Methods for Structural Engineering  
**Student:** Fangyutong  
**Student ID:** 21353319  
**Email:** yfangbu@connect.ust.hk  
**Checkpoint date:** 22 September 2026

## 1. Checkpoint status

This repository contains a reproducible intermediate solution for Floor Plan 3. The floor geometry, vertical structural elements, tributary areas, gravity loads, five-storey axial-load accumulation, and independent verification have been completed.

The current result is suitable for the Week 4 checkpoint. It is not presented as the final submission because the image-derived support axes and the provisional stair/core load model still require final engineering review.

| Completed item | Evidence |
|---|---|
| Floor outline and gross area | `Step_01_Geometry_and_Tributary_Areas.md` |
| Columns, walls, and coordinates | `Step_01B_Vertical_Element_Coordinates.csv` |
| Closed tributary regions | `FloorPlan3_tributary_boundaries.png` and `FloorPlan3_tributary_regions_straight.png` |
| Tributary-area schedule | `Step_01C_Tributary_Areas.csv` |
| Dead, live, and axial loads | `Step_02_Vertical_Load_and_Axial_Force_Calculation.md` |
| Floor-by-floor accumulation | `Step_02_Axial_Loads_by_Level.csv` |
| Independent checks | `Step_03_Verification_and_Checkpoint.md` |
| Reproducible code | Python scripts and Git history in this repository |

## 2. Input and assumptions

The supplied plan is treated as a typical floor of a five-storey reinforced-concrete building.

| Input | Adopted value |
|---|---:|
| Number of storeys | 5 |
| Storey height | 3.00 m |
| Slab thickness | 0.150 m |
| Concrete unit weight | 25.00 kN/m3 |
| Slab dead load | 3.750 kN/m2 |
| Live area load | 5.000 kN/m2 |

Plan dimensions are interpreted in metres. Column and wall section dimensions are interpreted in millimetres. Coordinates are image-derived because an original CAD model was not supplied.

## 3. Methodology

1. Reconstruct the external slab outline and projections from the dimensioned image.
2. Deduct the two openings O1/O2 and separate the stair/core zone S1 from the ordinary flat slab.
3. Establish column centres and finite wall centreline segments in a common coordinate system.
4. Construct midpoint divisions and 45-degree wall-corner divisions by assigning slab cells to the nearest support axis using rectilinear distance.
5. Close and clip every tributary region against the slab outline and excluded zones.
6. Apply slab dead and live loads to each tributary area and add the self-weight of the corresponding vertical element.
7. Accumulate loads through five identical storeys and calculate service and provisional reporting combinations.
8. Recompute the main outputs independently and compare them with the generated schedules.

The manual sketch below records the human review used to identify missing wall axes, midpoint boundaries, and corner divisions in an earlier agent-generated diagram.

![Manual review sketch](manual_review_sketch.png)

## 4. Geometry and tributary areas

The gross plan area is:

\[
A_\mathrm{gross}=186.615\ \mathrm{m^2}
\]

The adopted excluded area consists of O1/O2 (2.000 m2) and S1 (5.365 m2). Therefore:

\[
A_\mathrm{flat\ slab}=186.615-2.000-5.365=179.250\ \mathrm{m^2}
\]

Nine columns (C1-C9) and twelve walls (T1-T12) are included. Their coordinates and axis segments are recorded in `Step_01B_Vertical_Element_Coordinates.csv`.

![Support axes and closed tributary boundaries](FloorPlan3_tributary_boundaries.png)

![Closed tributary regions](FloorPlan3_tributary_regions_straight.png)

The 21 tributary areas sum to 179.250 m2. All adopted ordinary slab cells are assigned once, with no gaps or overlaps in the numerical partition.

## 5. Vertical-load results

The stair/core zone S1 is provisionally represented by its horizontal plan area. Its dead and live loads are distributed to T6, T7, and T8 in proportion to bordering lengths 2.10:3.40:2.10.

| Result | Value |
|---|---:|
| Ordinary slab dead load per floor | 672.188 kN |
| S1 equivalent dead load per floor | 20.119 kN |
| Vertical-element self-weight per floor | 606.188 kN |
| Total permanent load per floor | 1298.494 kN |
| Total variable load per floor | 923.075 kN |
| Five-storey base permanent load | 6492.469 kN |
| Five-storey base variable load | 4615.375 kN |
| Five-storey base service load, G+Q | 11107.844 kN |
| Five-storey base ULS load, 1.35G+1.50Q | 15687.895 kN |

The 1.35G+1.50Q and G+0.30Q factors are provisional reporting assumptions retained from the original submission. Their course-code basis must be confirmed before design use; the latter is not classified as seismic mass or quasi-permanent load in the current reproducible workflow.

The current element-level base results are:

| Element | Location or main axis (m) | Tributary area (m2) | Base G (kN) | Base Q (kN) | Base G+Q (kN) | Base ULS (kN) |
|---|---|---:|---:|---:|---:|---:|
| C1 | (7.550, 15.900) | 7.2973 | 196.82 | 182.43 | 379.26 | 539.36 |
| C2 | (0.200, 15.000) | 2.6293 | 109.30 | 65.73 | 175.03 | 246.15 |
| C3 | (0.200, 11.900) | 7.8498 | 207.18 | 196.25 | 403.43 | 574.07 |
| C4 | (3.600, 11.900) | 5.4765 | 162.68 | 136.91 | 299.60 | 424.99 |
| C5 | (10.000, 11.900) | 4.3862 | 142.24 | 109.65 | 251.90 | 356.51 |
| C6 | (0.200, 6.050) | 9.2966 | 234.31 | 232.41 | 466.73 | 664.94 |
| C7 | (3.600, 6.050) | 10.4308 | 271.51 | 260.77 | 532.28 | 757.70 |
| C8 | (6.600, 6.050) | 9.0280 | 229.28 | 225.70 | 454.98 | 648.07 |
| C9 | (10.000, 6.050) | 7.3866 | 198.50 | 184.66 | 383.16 | 544.97 |
| T1 | (5.750, 19.075) to (7.750, 19.075) | 8.3630 | 344.31 | 209.07 | 553.38 | 778.43 |
| T2 | (2.575, 17.200) to (2.575, 19.200) | 6.3181 | 305.96 | 157.95 | 463.92 | 649.98 |
| T3 | (1.700, 15.075) to (3.700, 15.075) | 14.1177 | 452.21 | 352.94 | 805.15 | 1139.89 |
| T4 | (4.700, 11.975) to (7.750, 11.975) | 12.1027 | 512.86 | 302.57 | 815.43 | 1146.22 |
| T5 | (5.875, 10.350) to (5.875, 12.100) | 1.0133 | 183.06 | 25.33 | 208.39 | 285.13 |
| T6 | (4.700, 10.475) to (6.800, 10.475) | 7.1752 | 359.21 | 216.44 | 575.65 | 809.59 |
| T7 | (6.675, 7.200) to (6.675, 10.600) | 8.7395 | 527.62 | 278.49 | 806.11 | 1130.02 |
| T8 | (4.700, 7.325) to (6.800, 7.325) | 10.4369 | 420.36 | 297.98 | 718.35 | 1014.46 |
| T9 | (0.125, 0.000) to (0.125, 2.000) | 8.4668 | 346.25 | 211.67 | 557.92 | 784.95 |
| T10 | (2.450, 0.125) to (4.450, 0.125) | 15.1329 | 471.24 | 378.32 | 849.56 | 1203.66 |
| T11 | (5.750, 0.125) to (7.750, 0.125) | 15.1360 | 471.30 | 378.40 | 849.70 | 1203.86 |
| T12 | (10.075, 0.000) to (10.075, 2.000) | 8.4668 | 346.25 | 211.67 | 557.92 | 784.95 |
| **Total** | | **179.2500** | **6492.47** | **4615.38** | **11107.84** | **15687.90** |

![Base ULS axial-load comparison](Step_02_Base_ULS_Axial_Loads.png)

The full 21-element summary is provided in `Step_02_Element_Load_Summary.csv`. The complete 105-row schedule for all elements and levels is provided in `Step_02_Axial_Loads_by_Level.csv`.

## 6. Verification

The independent Step 03 script performs 23 checks. All 23 checks pass.

The checks include:

- element-ID and row-count consistency;
- area closure to 179.250 m2 and gross-area closure to 186.615 m2;
- independent slab-load and member-self-weight calculations;
- whole-floor and five-storey load reconciliation;
- service and provisional reporting combinations;
- the 1:2:3:4:5 floor-accumulation sequence for every element;
- representative hand checks for C1 and T7; and
- nonnegative areas and loads.

The maximum difference between independently recomputed values and the four-decimal CSV outputs is 0.00005 kN or m2, which is attributable to output rounding.

## 7. AI-agent and Git workflow evidence

Codex was used as an AI agent within the project folder to inspect source files, create and revise scripts, run calculations, inspect generated figures, verify outputs, and maintain the repository. The student manually reviewed the structural interpretation and supplied a correction sketch before the final tributary regions were generated.

The Git history retains separate commits for the geometry, manual review, detailed opening review, coordinate schedule, vertical-load calculation, and deterministic verification. Earlier steps have not been deleted or replaced.

The main reproducible commands are:

```powershell
python tributary_regions.py
python step02_loads.py
python verify_results.py
```

The first command uses the adopted rectilinear L1 method by default and regenerates both Step 01 CSV inputs. The non-submission Euclidean comparison requires `--euclidean-diagnostic` and does not overwrite those validated CSV files.

## 8. Current limitations and next work

- Coordinates and short wall returns remain image-derived and should be checked against original CAD data if it becomes available.
- Geometric wall centrelines are used. The model must be updated if the required fixation lines differ.
- S1 uses an equivalent horizontal-area approximation rather than explicit stair-flight and landing geometry.
- Short wall returns are excluded from self-weight to avoid uncertain overlap and double-counting.
- Finishes, partitions, facade, beam self-weight, and live-load reduction are not included because project values were not supplied.
- The final submission will consolidate the detailed step reports and improve the unknown-plan generalisation workflow.

## 9. Detailed records

- [Step 01 - Geometry and tributary areas](Step_01_Geometry_and_Tributary_Areas.md)
- [Step 02 - Vertical loads and axial forces](Step_02_Vertical_Load_and_Axial_Force_Calculation.md)
- [Step 03 - Verification and checkpoint](Step_03_Verification_and_Checkpoint.md)
- [Project navigation and reproduction guide](README.md)
