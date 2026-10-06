# Step 06 - OpenSees Pure-Beam and One-Storey Subframe Models

## 1. Scope

This step is a preliminary single-line model for each marked beam, not the complete HW2 Task 3 subframe. It lacks the perpendicular bay and the full Task 12 load-path comparison. Beam A is D19-D11-D05; Beam B is D16-D17-D18. The models use the revised Step 04 mixed-edge allocation and actual Step 05 service-load profiles. All C/S labels remain assumptions; unresolved core area remains unallocated.

The old briefing is retained as historical evidence in `Step_06_OpenSees_Briefing_and_Iteration_Log.md`; its old load values are superseded. Current screening scales are recorded before this rerun in `Step_06_Mixed_Support_PreSolve_Screening.md`. No claim is made that the historical schematic was independently drawn before the first-ever solver execution.

## 2. Model assumptions

- Units: kN and m; stress and elastic modulus in kN/m2.
- Concrete: linear elastic, E = 30,000,000 kN/m2.
- Beam A section: 250 x 700 mm; Beam B section: 250 x 600 mm.
- Load case: service G+Q, including slab load and beam-stem self-weight.
- Actual non-uniform profiles are read directly from Step_05_Beam_Load_Profiles.csv into 0.01 m elasticBeamColumn intervals. Asymmetry is preserved; no symmetric fitting or force rescaling is used.
- The pure models are continuous beams with vertical simple supports at all grid points.
- Each subframe places the beam at the top of one 3.0 m storey; the support members have fixed bases and there are no upper-storey columns.
- Positive plotted moment is sagging; negative plotted moment is hogging.

The configuration is machine-readable in `Step_06_OpenSees_Model_Config.json`.

## 3. Pre-solve expectation

![Pre-solve expected shapes](Step_06_PreSolve_Expected_Shapes.png)

The governing simply-supported midspan screening scales are 58.470 kN m for Beam A and 46.470 kN m for Beam B. These are not rigorous maximum-moment bounds for asymmetric loading. Continuity can introduce negative moments over interior supports. The schematic is an illustrative guide, not a student hand drawing.

## 4. Solver results

| Beam | Model | Applied G+Q (kN) | Reaction sum (kN) | M+ (kN m) | M- (kN m) | max abs(V) (kN) | max abs(N) (kN) | max vertical deflection (mm) | Screen check |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| Beam A | pure | 151.268 | 151.268 | 35.629 | -50.301 | 40.433 | 0.000 | 0.491 | PASS |
| Beam A | subframe | 151.268 | 151.268 | 24.056 | -40.016 | 33.934 | 3.890 | 0.316 | PASS |
| Beam B | pure | 183.071 | 183.071 | 37.046 | -22.291 | 43.990 | 0.000 | 0.323 | PASS |
| Beam B | subframe | 183.071 | 183.071 | 28.073 | -25.297 | 41.208 | 7.332 | 0.253 | PASS |


Maximum vertical equilibrium error across the four models was 3.965e-05 kN. The fine mesh uses an absolute equilibrium gate of 1e-4 kN (0.1 N) and relative gate of 1e-6; the former 60-element mesh used 1e-6 kN. This relaxed absolute gate acknowledges numerical conditioning, not missing physical load. Maximum reconstructed element-end moment error was 7.283e-14 kN m. All four peak moments passed the deliberately broad screening gate.

Run `verify_step06_opensees.py` separately to produce `Step_06_OpenSees_Verification.csv`. It includes closed-form (qL^2/8), (-qL^2/12), and (qL^2/24) references for a 4 m beam at 10 kN/m, plus profile provenance, load totals and solver equilibrium checks. Model self-consistency is not independent validation of the assumed support conditions.

### Beam A - pure continuous beam

![Beam A pure response](Step_06_BeamA_Pure_Response.png)

### Beam A - one-storey subframe

![Beam A subframe response](Step_06_BeamA_Subframe_Response.png)

### Beam B - pure continuous beam

![Beam B pure response](Step_06_BeamB_Pure_Response.png)

### Beam B - one-storey subframe

![Beam B subframe response](Step_06_BeamB_Subframe_Response.png)

## 5. Pure beam versus subframe

For Beam A, the peak absolute moment changed from 50.30 to 40.02 kN m and maximum vertical deflection changed from 0.491 to 0.316 mm. The stiff T9 boundary member and the finite column rotational stiffness redistribute both the support and span moments. For Beam B, the subframe reduced the peak sagging moment from 37.05 to 28.07 kN m while increasing the peak hogging magnitude from 22.29 to 25.30 kN m. This is the expected transfer from span moment into support moment. The beam remains rotation-compatible at each support and does not form a displacement kink; the frame columns sway and rotate with the beam nodes.

The subframe is the more defensible of these two models for beam-force distribution because it includes support stiffness and frame action. It is still only a one-line, one-storey approximation and is not a substitute for a full floor-grid or multi-storey model.

## 6. Support reactions and HW1 cross-check

The detailed reactions are in `Step_06_OpenSees_Support_Reactions.csv`.

![HW1 and HW2 reaction comparison](Step_06_HW1_Subframe_Reaction_Comparison.png)

| Beam | Grid point | HW1 full-floor one-storey axial (kN) | HW2 selected-line reaction (kN) | Difference |
|---|---|---:|---:|---:|
| Beam A | T9 | 111.58 | 31.39 | -71.9% |
| Beam A | C6 | 93.35 | 66.78 | -28.5% |
| Beam A | C3 | 80.69 | 48.70 | -39.6% |
| Beam A | C2 | 35.01 | 4.40 | -87.4% |
| Beam B | C6 | 93.35 | 41.21 | -55.9% |
| Beam B | C7 | 106.46 | 47.90 | -55.0% |
| Beam B | C8 | 91.00 | 52.78 | -42.0% |
| Beam B | C9 | 76.63 | 41.18 | -46.3% |


This is a scope diagnostic, not an expected equality. The HW1 value contains the full floor tributary load plus vertical-member self-weight. The Step 06 subframe contains only the selected marked beam line and omits reactions arriving from orthogonal and neighbouring beams. The generally smaller HW2 reactions therefore identify missing floor-grid scope rather than a vertical-equilibrium failure. A full Task 12 equality check requires either a larger grid model or equivalent nodal loads from every omitted adjoining beam.

The assignment wording refers to beam axial N at the support, but the quantity physically comparable with a column axial force is the vertical support reaction, or equivalently the column axial force. Beam-local N is horizontal and is reported separately in the N diagram.

## 7. Reproduction

Run all models and rebuild the tables and figures:

```powershell
python step06_run_all.py
python verify_step06_opensees.py
```

The four explicit OpenSees entry points are:

- `Step_06_BeamA_Pure_OpenSees.py`
- `Step_06_BeamA_Subframe_OpenSees.py`
- `Step_06_BeamB_Pure_OpenSees.py`
- `Step_06_BeamB_Subframe_OpenSees.py`

## 8. Items requiring student sign-off

1. Confirm the image-derived mapping of Beam A to D19-D11-D05 and Beam B to D16-D17-D18.
2. Confirm the T9 strong-axis wall-equivalent representation in the Beam A subframe.
3. Confirm that the W5 convention intends fixed bases with no upper-storey columns.
4. Add the student's hand-drawn deformed-shape sketches. The illustrative schematic is not a substitute for the required hand drawing.
5. Decide whether Task 12 should be extended to a full floor-grid reaction model or completed with equivalent nodal loads from omitted beams.
