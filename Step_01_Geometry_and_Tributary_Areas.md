# HW1 - Plan 3 Geometry and Preliminary Tributary-Area Partition

## 1. Units and coordinate system

The drawing does not state its units explicitly. Based on the scale of the dimensions, plan dimensions such as 3.20, 5.80, and 19.20 are interpreted in metres, while column and wall section dimensions such as 400×400 and 2000×250 are interpreted in millimetres. All dimensions are converted to metres before calculation.

The origin is set at the lower-left corner of the main building footprint, excluding projection P14. The x-axis points to the right and the y-axis points upward.

| Outline vertex | x (m) | y (m) |
|---|---:|---:|
| V1 | 0.00 | 0.00 |
| V2 | 10.20 | 0.00 |
| V3 | 10.20 | 12.10 |
| V4 | 7.75 | 12.10 |
| V5 | 7.75 | 19.20 |
| V6 | 2.45 | 19.20 |
| V7 | 2.45 | 15.20 |
| V8 | 0.00 | 15.20 |

## 2. Slab area

The main footprint is decomposed into three rectangles:

\[
A_\mathrm{body}=10.20(12.10)+7.75(3.10)+5.30(4.00)=168.645\ \mathrm{m^2}
\]

| Panel | Dimensions (m) | Area (m²) |
|---|---|---:|
| P10 | 2.65×0.50 | 1.325 |
| P11 | 2.45×1.00 | 2.450 |
| P12 | 0.50×4.30 | 2.150 |
| P13 | 2.45×0.90 | 2.205 |
| P14 | 8.20×1.20 | 9.840 |
| Total | | 17.970 |

The gross slab area before deducting openings is:

\[
A_\mathrm{gross}=168.645+17.970=186.615\ \mathrm{m^2}
\]

The detailed structural drawing confirms that the two upper core rectangles O1 and O2 contain no ordinary slab panel. It also shows the enclosure bounded by T6, T7, and T8 as a stair/core zone rather than a normal flat-slab panel.

![Original structural drawing used to review the core](Plan3_original_structural_drawing.png)

Under the current geometric reconstruction, O1 is 1.05×1.25 m, O2 is 0.55×1.25 m, and the clear stair/core zone S1 is 1.85×2.90 m:

\[
A_\mathrm{excluded}=1.05(1.25)+0.55(1.25)+1.85(2.90)=7.365\ \mathrm{m^2}
\]

The adopted effective slab area is:

\[
\boxed{A_\mathrm{flat\ slab}=186.615-7.365=179.250\ \mathrm{m^2}}
\]

O1 and O2 are treated as voids. S1 is excluded from the ordinary 150 mm flat-slab allocation and must receive a separate stair/core load model in the vertical-load calculation. Exclusion from this flat-slab calculation does not mean that S1 carries zero structural load.

## 3. Vertical structural elements and coordinates

The vertical-load-resisting elements identified in the drawing are nine columns (C1-C9) and twelve structural wall elements (T1-T12). Coordinates are measured in the coordinate system defined in Section 1. Column coordinates refer to section centres. Wall coordinates refer to finite geometric centreline segments.

The coordinates were reconstructed from the dimensioned floor-plan image and the detailed structural drawing. They are therefore classified as **image-derived geometric data**, rather than original CAD coordinates. Main wall lengths match the labelled section lengths. Short wall returns are reconstructed approximately from the raster image.

### Column centres

| Column | x (m) | y (m) | Section (mm) |
|---|---:|---:|---:|
| C1 | 7.550 | 15.900 | 400×400 |
| C2 | 0.200 | 15.000 | 400×400 |
| C3 | 0.200 | 11.900 | 400×400 |
| C4 | 3.600 | 11.900 | 400×400 |
| C5 | 10.000 | 11.900 | 400×400 |
| C6 | 0.200 | 6.050 | 400×400 |
| C7 | 3.600 | 6.050 | 450×450 |
| C8 | 6.600 | 6.050 | 400×400 |
| C9 | 10.000 | 6.050 | 400×400 |

### Main wall-axis segments

| Wall | Axis start (m) | Axis end (m) | Section (mm) |
|---|---|---|---:|
| T1 | (5.750, 19.075) | (7.750, 19.075) | 2000×250 |
| T2 | (2.575, 17.200) | (2.575, 19.200) | 250×2000 |
| T3 | (1.700, 15.075) | (3.700, 15.075) | 2000×250 |
| T4 | (4.700, 11.975) | (7.750, 11.975) | 3050×250 |
| T5 | (5.875, 10.350) | (5.875, 12.100) | 250×1750 |
| T6 | (4.700, 10.475) | (6.800, 10.475) | 2100×250 |
| T7 | (6.675, 7.200) | (6.675, 10.600) | 250×3400 |
| T8 | (4.700, 7.325) | (6.800, 7.325) | 2100×250 |
| T9 | (0.125, 0.000) | (0.125, 2.000) | 250×2000 |
| T10 | (2.450, 0.125) | (4.450, 0.125) | 2000×250 |
| T11 | (5.750, 0.125) | (7.750, 0.125) | 2000×250 |
| T12 | (10.075, 0.000) | (10.075, 2.000) | 250×2000 |

The machine-readable file [Step_01B_Vertical_Element_Coordinates.csv](Step_01B_Vertical_Element_Coordinates.csv) also records the short return segments used in the tributary-area model. This CSV is the input geometry for subsequent load calculations.

## 4. Support axes and tributary boundaries

Columns are represented by their centre points. Walls are reconstructed using their section outlines and represented by finite geometric centreline segments. Main wall segments and short returns carrying the same ID are grouped as one structural element.

### Manual review and correction

The first agent-generated diagram showed support axes and several local midpoint boundaries, but it did not form closed tributary-area polygons. I manually marked the expected wall centre axes, midpoint divisions, and 45-degree divisions at orthogonal wall corners to identify the missing connections.

This sketch was used as a review document rather than as direct calculation input. It records the human checking and correction stage of the AI-assisted workflow. The final boundaries were then reconstructed computationally, closed at actual intersections, and checked by area conservation.

![Manual review sketch showing proposed axes and boundary corrections](manual_review_sketch.png)

The first figure shows only the structural elements, support axes, and closed dashed boundaries. It is intended to resemble the construction shown in the assignment example.

![Plan 3 support axes and dashed tributary boundaries](FloorPlan3_tributary_boundaries.png)

The closed partition uses rectilinear (L1) distance. Each slab point is assigned to the nearest column centre or finite wall-axis segment. For an orthogonal layout, this produces midpoint boundaries, horizontal or vertical segments, 45-degree wall-corner divisions, and actual intersections that close every tributary-area polygon.

The partition is clipped by the slab outline, O1/O2, and S1. A 0.01 m calculation grid is used. Recalculation with a 0.02 m grid changes the area of any single element by no more than approximately 0.073 m².

## 5. Tributary areas

The second figure applies colour to the same closed regions used for area calculation.

![Plan 3 closed tributary-area regions](FloorPlan3_tributary_regions_straight.png)

| Element | Tributary area (m²) | Element | Tributary area (m²) |
|---|---:|---|---:|
| C1 | 7.2973 | T1 | 8.3630 |
| C2 | 2.6293 | T2 | 6.3181 |
| C3 | 7.8498 | T3 | 14.1177 |
| C4 | 5.4765 | T4 | 12.1027 |
| C5 | 4.3862 | T5 | 1.0133 |
| C6 | 9.2966 | T6 | 7.1752 |
| C7 | 10.4308 | T7 | 8.7395 |
| C8 | 9.0280 | T8 | 10.4369 |
| C9 | 7.3866 | T9 | 8.4668 |
| | | T10 | 15.1329 |
| | | T11 | 15.1360 |
| | | T12 | 8.4668 |

Area-conservation check:

\[
\sum A_i=179.250\ \mathrm{m^2}=A_\mathrm{flat\ slab}
\]

All assumed slab cells are assigned exactly once. The closed regions do not overlap and collectively cover the complete effective slab area adopted in this model.

## 6. Assumptions requiring confirmation

1. O1 and O2 are treated as voids because neither carries a slab-panel designation in the detailed structural drawing.
2. S1, bounded by T6, T7, and T8, is treated as a stair/core zone. It is excluded from ordinary flat-slab area and requires a separate load model in Step 02.
3. Short wall returns are reconstructed approximately from the image and should be checked against the original CAD drawing or instructor guidance.
4. The horizontal location of P10 is not fully dimensioned. This does not affect its area but affects its local tributary partition.
5. Geometric wall centrelines are used. If the required fixation lines differ, the support axes and tributary regions must be recalculated.
6. Column and wall footprints remain within the plan allocation. Their self-weight must be handled consistently later to avoid double-counting material volumes.
7. This is a reproducible geometric partition based on the stated assumptions. It is not, by itself, a validated stiffness-based structural load-path model.
