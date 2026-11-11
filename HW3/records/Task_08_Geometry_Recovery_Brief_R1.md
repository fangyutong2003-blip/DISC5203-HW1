# Task 8 - Supplementary geometry recovery R1, prospective brief

Date: 2026-11-11. Agent-authored engineering proposal, not a student-signed prediction. The student instructed continued work. Freeze this brief and its parameters before execution.

## Status and method boundary

The original fixed pipeline, masks, forest and failure scores remain unchanged. The ten local flags now have supplemented references and tied actual readers. They do not establish full-plan geometry. This recovery is a **post-audit method revision**, not evidence that the unchanged pipeline generalised successfully, and not a more-accurate VLM winner.

Use deterministic solid-symbol thresholding and morphology, directional bars and the source dimension grid. The VLMs supply no vertices. Record every measured pixel box, calibration, printed-size source, inferred support and remaining ambiguity. A conditional engineering baseline is allowed only with those assumptions exposed; do not label it a fully promoted blind extraction.

## Prospective image rules

- Retain original image sizes; no new source resize. Threshold grayscale <100 to select dark solid symbols. Open with a square of physical side 0.20 m, rounded to pixels using the printed overall dimension and independently located outer column-grid anchors (minimum 2 px).
- Initial calibration anchors, from existing classical/source measurements: NewPlan lower-left column centre approximately (1646,3406) px and upper-right (6890,1391) px for 46 by 18 m; NIST (74,502) and (527,48) px for 120 ft = 36.576 m in both directions. These are image-derived starting measurements, not CAD coordinates.
- Keep all connected components. Candidate columns require fill >=0.85, aspect <=1.5 and pixel size consistent with square structural symbols; label text must not be accepted merely because it is a component.
- Open the solid mask directionally over 1 m and require bar aspect >=3. Associate compatible directional bars uniquely to printed labels. Use printed wall lengths/thicknesses for NewPlan; pixels place centres. For NIST lengths come from calibrated symbol endpoints and wall thickness is the assignment default 0.250 m, never inferred from schematic stroke width.
- Cluster measured column coordinates within 0.30 m. NewPlan has eight dimensioned axes with spans 6/6/8/6/8/6/6 m and four rows 6 m apart. NIST has five axes per direction, 9.144 m apart. Record a global affine fit and local grid-based calibration; if the image is not perfectly to scale, retain residuals and any piecewise grid calibration as a disclosed revision, not silent snapping.

## Source interpretation and uncertainty, before extraction

- NewPlan prints C1:C30 = 800x800 mm. Columns C17/C20 have printed labels at grid intersections but no clearly filled square in the viewed source. Retain them as **label-only, grid-inferred** supports in one conditional case, and compare a visible-body-only case without them. Their presence is not cleared by the existing six wall-label flags.
- NIST Figure 2 shows 21 separate square symbols and four wall symbols, while adjacent report text describes 25 gravity columns. Use a visible-symbol baseline (21 column points + four walls) and retain the four-column discrepancy as unresolved. IDs on the found plan are analyst bookkeeping IDs, not OCR successes. No unknown column section or self-weight may be invented.
- NewPlan dimensions are grid spacings. The visible outside frame lies near the outer column faces. Main conditional slab domain: outer grid expanded by half the printed column width, [-0.4,46.4] x [-0.4,18.4] m. Also retain the grid-axis rectangle [0,46] x [0,18] m as an area/mass sensitivity. Both are explicit edge interpretations, not a newly printed slab dimension.
- For NIST use the printed square footprint, [0,36.576]^2 m. Interpret perimeter walls' outside face on that border and inset their structural centreline by half the assumed thickness; retain raw ink-centre coordinates too. Unknown column sections are point supports. Retain an ideal symmetric-wall sensitivity separately from the measured schematic placement; do not mistake drawing irregularity for verified building eccentricity.
- No openings/stairs are shown on these additional schematic plans; absence is an explicit model assumption, not a claim about a constructed building. Do not copy Plan 3 O1/O2/S1 into other plans.

## Area, gravity and mechanics sequence

1. Generate metric element records and overlay them on the original sources. Printed column grids and assumed outlines must be distinguished from measured wall centres. Require unique IDs, bar claims, support-axis containment, source/size provenance and ink-support diagnostics. Retain warnings rather than deleting inconvenient symbols.
2. Construct closed L1 nearest-finite-axis/point tributary regions, clipped to the declared slab domain, using the same Manhattan allocation convention as Plan 3. Use 0.05 m cells and a separate 0.10 m check; exact polygon union must close the domain and detect gaps/overlaps. The raster step is numerical approximation, not image rescaling.
3. Transfer the HW1 exercise assumptions explicitly: slab G=0.150*25=3.75 kN/m2 and Q=5.0 kN/m2, H=3 m, five storeys. No unspecified beams/finishes/design earthquake are added. NewPlan known vertical-member weight must use a net footprint union, avoiding overlap double counting; keep its allocation convention. NIST unknown column self-weight stays null, and gravity totals are labelled known-only rather than complete axial loads.
4. Keep the prescribed uniform floor mass intensity 8.75 kN/m2 for the lateral exercise, consistent with Plan 3; vertical-member self-weight is separate and not silently inserted into that mass. Compute CM, polar mass, shear-inclusive strong/weak wall stiffness, hand K/F and CR first. E=30 GPa, nu=0.2, Av=(5/6)Lt, intrinsic wall torsion J=0, columns omitted from lateral stiffness, same rectangular-bar approximation as the retained baseline. Joined L walls are separate labelled bars, not a detailed monolithic shell design.
5. Only after geometry/area checks, run matching explicit rigidDiaphragm/Transformation OpenSees unit loads, equilibrium and zero rotation through CR. Use the same assumed 100 kN demonstration loads and retain raw solver responses. No code-level seismic design certification is claimed.
6. Compare NewPlan/NIST conditional results with Plan 3, including edge/mass, missing-column and schematic-symmetry sensitivities. A useful engineering comparison does not erase the documented failure of the unchanged extraction or unresolved source topology.
