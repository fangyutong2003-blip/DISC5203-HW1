# Step 03 - Verification and Checkpoint

## Purpose

This checkpoint independently recalculates the Step 01 geometry totals and the Step 02 vertical-load results from the delivered CSV inputs. It does not overwrite or replace any earlier step.

## Verification status

- Checks passed: **23/23**
- Checks failed: **0**
- Overall status: **PASS**

| ID | Independent check | Expected | Actual | Tolerance | Status |
|---|---|---:|---:|---:|:---:|
| V01 | Number of vertical elements | 21 | 21 | exact | **PASS** |
| V02 | Number of by-level result rows | 105 | 105 | exact | **PASS** |
| V03 | Element IDs agree across area, coordinate, summary, and level files | True | True | exact | **PASS** |
| V04 | Tributary areas close to ordinary flat-slab area (m2) | 179.250000 | 179.250000 | 0.001000 | **PASS** |
| V05 | Gross floor area closes after adding O1/O2 and S1 (m2) | 186.615000 | 186.615000 | 0.001000 | **PASS** |
| V06 | Ordinary slab dead load per floor (kN) | 672.187500 | 672.187500 | 0.001000 | **PASS** |
| V07 | Ordinary slab live load per floor (kN) | 896.250000 | 896.250000 | 0.001000 | **PASS** |
| V08 | S1 equivalent dead load per floor (kN) | 20.118750 | 20.118750 | 0.001000 | **PASS** |
| V09 | S1 equivalent live load per floor (kN) | 26.825000 | 26.825000 | 0.001000 | **PASS** |
| V10 | Vertical-member self-weight per floor (kN) | 606.187500 | 606.187500 | 0.001000 | **PASS** |
| V11 | Total permanent load per floor (kN) | 1298.493750 | 1298.493750 | 0.001000 | **PASS** |
| V12 | Total variable load per floor (kN) | 923.075000 | 923.075000 | 0.001000 | **PASS** |
| V13 | Base permanent load for five storeys (kN) | 6492.468750 | 6492.468750 | 0.001000 | **PASS** |
| V14 | Base variable load for five storeys (kN) | 4615.375000 | 4615.375000 | 0.001000 | **PASS** |
| V15 | Base service load G+Q (kN) | 11107.843750 | 11107.843750 | 0.001000 | **PASS** |
| V16 | Base ULS load 1.35G+1.50Q (kN) | 15687.895310 | 15687.895312 | 0.002000 | **PASS** |
| V17 | Base provisional G+0.30Q reporting combination (kN) | 7877.081250 | 7877.081250 | 0.002000 | **PASS** |
| V18 | Maximum absolute difference in Step 02 summary (kN or m2) | 0.000000 | 0.000050 | 0.000110 | **PASS** |
| V19 | Every element contains the 1:2:3:4:5 storey accumulation sequence | True | True | exact | **PASS** |
| V20 | Maximum absolute difference in by-level results (kN) | 0.000000 | 0.000050 | 0.000110 | **PASS** |
| V21 | All recomputed areas and loads are nonnegative | True | True | exact | **PASS** |
| V22 | Representative C1 base ULS agrees with Step 02 (kN) | 539.361656 | 539.361700 | 0.000110 | **PASS** |
| V23 | Representative T7 base ULS agrees with Step 02 (kN) | 1130.020609 | 1130.020600 | 0.000110 | **PASS** |


## Independent calculation basis

| Item | Value |
|---|---:|
| Number of storeys | 5 |
| Storey height | 3.00 m |
| Concrete density | 25.00 kN/m3 |
| Slab thickness | 0.150 m |
| Slab dead load | 3.750 kN/m2 |
| Live load | 5.000 kN/m2 |
| Gross floor area | 186.615 m2 |
| O1/O2 void area | 2.000 m2 |
| S1 plan area | 5.365 m2 |
| Ordinary flat-slab area | 179.250 m2 |

The ordinary slab area is distributed to C1-C9 and T1-T12 by the Step 01 tributary-area file. S1 is added separately and distributed to T6, T7, and T8 in proportion to bordering lengths 2.10:3.40:2.10. Column and wall self-weights use the main labelled section dimensions, a 3.0 m storey height, and 25 kN/m3 concrete density.

The 1.35G+1.50Q and G+0.30Q factors are read from `load_combinations.json`. They reproduce the original submission but remain provisional pending confirmation of the course design standard. G+0.30Q is labelled only by its equation and is not classified as seismic mass or quasi-permanent load.

## Representative manual checks

### C1

- Tributary slab dead load = 7.2973 x 3.750 = 27.3649 kN/floor.
- Column self-weight = 0.400 x 0.400 x 3.0 x 25 = 12.0000 kN/floor.
- G = 39.3649 kN/floor and Q = 36.4865 kN/floor.
- Base provisional ULS = 1.35 x (5 x 39.3649) + 1.50 x (5 x 36.4865) = 539.3617 kN.

### T7

- S1 allocation ratio = 3.40 / (2.10 + 3.40 + 2.10) = 0.447368.
- Tributary slab dead load = 8.7395 x 3.750 = 32.7731 kN/floor.
- Wall self-weight = 0.250 x 3.400 x 3.0 x 25 = 63.7500 kN/floor.
- Allocated S1 dead/live loads = 9.0005/12.0007 kN/floor.
- G = 105.5236 kN/floor and Q = 55.6982 kN/floor.
- Base ULS = 1130.0206 kN.

## Numerical sensitivity and interpretation

The Step 01 partition uses a 0.01 m calculation grid. The recorded 0.02 m rerun changed any single tributary area by no more than approximately 0.073 m2, about 0.041% of the 179.250 m2 ordinary flat-slab area. This is a numerical discretisation check, not a substitute for engineering review of support axes and corner-boundary assumptions.

## Checkpoint evidence

- Step 01 geometry, coordinate, and tributary-area records remain in the repository.
- Step 02 load assumptions, element summaries, by-level axial-load results, and the base ULS chart remain in the repository.
- `verify_results.py` reproduces this report and `Step_03_Verification_Results.csv`.
- The verification uses independent equations and does not copy Step 02 totals into the expected values.

Recent Git history when this checkpoint was generated:

- `20909ae Revise HW2 mixed-edge tributary regions and propagate actual load profiles`
- `b867ebd Add HW2 OpenSees beam and subframe models`
- `2aa77dc Repair reproducible HW1 workflow and cross-platform setup`
- `dbd0516 Merge remote-tracking branch 'origin/master'`
- `5164a40 Add HW2 beam tributary areas and line-load schedules`
- `2490a98 [non-English commit subject omitted from report]`

## Remaining limitations before final submission

- All plan coordinates and tributary regions are image-derived and should be checked against any original CAD or dimension schedule if available.
- The S1 treatment is a provisional equivalent horizontal-area model. A stair-specific load path should replace it if the coursework requires flight and landing analysis.
- Short wall returns are excluded from member self-weight to avoid overlap and uncertain image dimensions.
- Finishes, partitions, facade, beam self-weight, and live-load reduction are not included because no project values have been provided.
- The load-combination factors require confirmation against the standard or lecture reference specified by the instructor.
- Support-fixity assumptions still require confirmation before lateral-load or frame analysis.

## Reproduction

Run:

```powershell
python verify_results.py
```

The command regenerates the Step 03 CSV and Markdown files without changing Step 01 or Step 02 records.
