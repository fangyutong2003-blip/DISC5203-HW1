# Step 04 - Revised Mixed Slab-Edge Conditions

Revision of checkpoint b867ebd. The original Step 04-06 outputs and code are preserved in [the pre-revision archive](HW2_Pre_Mixed_Support_Revision_b867ebd.zip). HW1 geometry is unchanged.

## Method and source

HW2.md, hint 04 (L04): matched 45/45; mixed 60 from fixed and 30 from simple.

C = continuous/rotationally restrained idealisation; S = supported with simple rotation idealisation. These labels describe the slab edge, not the end releases of the supporting beam. Complexity alone does not select an angle. The exact edge connection cannot be read reliably from this plan; every C/S entry below is an explicit modelling assumption.

For adjacent perpendicular edges use score = finite L1 distance / weight, with w(S)=1 and w(C)=sqrt(3). If the horizontal edge is C and the vertical edge S, equal scores give y=sqrt(3)x: 60 degrees from C and 30 from S. Equal weights give 45 degrees. Opposite unequal edges meet at a shifted straight division, not a 60-degree intersection of parallel edges. This weighted-distance construction is an adopted extension to finite edges and L-shaped panels; it is not a general yield-line or elastic plate solution.

The rule comes from the supplied assignment. [HKConcrete 2013 Table 6.7](https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/CoP_SUC2013e.pdf) distinguishes continuous/discontinuous edges, but its coefficients are not identical to the geometric weighting used here. No code compliance or stiffness-based support classification is claimed.

## Edge schedule

| Panel | Support | Condition | Basis |
|---|---|---|---|
| P1 | D01 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P1 | W_T1 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P1 | D02 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P1 | W_T2 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P1 | W_T3 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P1 | D06 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P1 | D09 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P1 | W_T4 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P1 | D03 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P1 | D07 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P2 | D04 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P2 | W_T3 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P2 | D05 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P2 | D06 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P2 | D08 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P3 | D08 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P3 | D11 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P3 | D12 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P3 | D16 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P4 | D12 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P4 | W_CORE_R | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P5 | W_T4 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P5 | D10 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P5 | D13 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P5 | W_T7 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P5 | D14 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P5 | D15 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P5 | D18 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P6 | W_T8 | C | Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified. |
| P6 | D17 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P7 | D16 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P7 | D19 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P7 | D20 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P7 | D23 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P8 | D20 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P8 | D21 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P9 | D18 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P9 | D21 | C | Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified. |
| P9 | D22 | S | Slab terminates or meets an opening: supported but rotationally simple assumed. |
| P9 | D25 | C | Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity. |
| P10 | D01 | cantilever root | overhang footprint clipped to finite root segment |
| P10 | W_T1 | cantilever root | overhang footprint clipped to finite root segment |
| P11 | D04 | cantilever root | overhang footprint clipped to finite root segment |
| P12 | D03 | cantilever root | overhang footprint clipped to finite root segment |
| P12 | D07 | cantilever root | overhang footprint clipped to finite root segment |
| P13 | D10 | cantilever root | overhang footprint clipped to finite root segment |
| P14 | D23 | cantilever root | overhang footprint clipped to finite root segment |
| P14 | D24 | cantilever root | overhang footprint clipped to finite root segment |
| P14 | D25 | cantilever root | overhang footprint clipped to finite root segment |

P4/P6/P8 retain their previous one-way equal reaction split; 30/60 corner rules are not applied to them. Cantilevers route all load to their actual root extent. Treating an entire cantilever-root edge as C is a sensitivity assumption, not proof of full fixity over that edge.

## Closed boundaries and areas

![Dashed boundaries](HW2_Beam_Tributary_Boundaries.png)

![Areas](HW2_Beam_Tributary_Areas.png)

Closed polygons are exported in [GeoJSON](Step_04_Closed_Regions.geojson) in local metres, not geographic coordinates. Hatched grey strips show wall axes/widths; orange cross-hatching identifies a geometry gap inherited from the panel reconstruction.

## Revised beam schedule

| Beam | Previous area (m2) | Revised area (m2) | Angle-only change vs exact matched model (m2) |
|---|---:|---:|---:|
| D01 | 6.0049 | 6.1898 | +0.1673 |
| D02 | 2.7052 | 0.8117 | -1.8908 |
| D03 | 8.7583 | 8.2148 | +0.0067 |
| D04 | 4.9717 | 5.4740 | +0.5077 |
| D05 | 2.3992 | 1.3871 | -1.0154 |
| D06 | 8.7323 | 6.6822 | +0.0000 |
| D07 | 4.4440 | 4.9797 | +0.0000 |
| D08 | 6.4238 | 7.7934 | +1.3759 |
| D09 | 0.6049 | 0.6050 | -0.0000 |
| D10 | 4.7921 | 5.6825 | +0.8988 |
| D11 | 7.6476 | 4.9647 | -2.6853 |
| D12 | 10.9761 | 11.9265 | +0.9490 |
| D13 | 1.1248 | 0.4566 | -0.6684 |
| D14 | 0.6662 | 0.6613 | +0.0000 |
| D15 | 7.6522 | 4.9647 | -2.6853 |
| D16 | 6.4915 | 8.2163 | +1.7363 |
| D17 | 1.2160 | 1.2112 | +0.0000 |
| D18 | 6.4812 | 8.2163 | +1.7363 |
| D19 | 7.6513 | 4.9647 | -2.6853 |
| D20 | 16.7187 | 17.6740 | +0.9490 |
| D21 | 16.7174 | 17.6740 | +0.9490 |
| D22 | 7.6518 | 4.9647 | -2.6853 |
| D23 | 6.3483 | 7.2282 | +0.8682 |
| D24 | 3.6000 | 3.6000 | +0.0000 |
| D25 | 6.3538 | 7.2282 | +0.8682 |

The full census remains in [Step 04 census](Step_04_Beam_Census.csv). The matched comparator uses the same exact geometry, so the last column isolates the angle change from polygon integration and cantilever-root corrections.

## Conservation and limitations

- Beams: 151.771260 m2.
- Direct wall/support allocation: 25.771240 m2.
- Explicit unresolved geometry: 1.707500 m2.
- Total: 179.250000 m2 (HW1 ordinary slab).
- 52 checks passed; polygon closure/overlap tolerance 1e-8 m2; profile integration tolerance 1e-7 m2.
- The unresolved region has not been assigned an invented wall reaction. The previous residual filler is removed. Complete load-path closure is still pending core geometry clarification.
- Grey physical walls/columns come from the HW1 coordinate schedule for visual reference. Black support axes retain the earlier HW2 idealised segmentation, which is not identical to every physical wall extent. W_CORE_R (magenta dashed) is an unverified assumed core support, not a verified physical wall. The 30/60-degree update does not validate that earlier geometry.
- Finite-segment L1 scores also create 2.584167 m2 of positive-area ties. These are provisionally assigned by support-list order, not mechanical evidence. [Tie audit](Step_04_Finite_Edge_Ties.csv) identifies the affected supports. This is a distinct uncertainty within allocated area, not additional unallocated floor area. It explains some changes versus the old raster tie handling, including D06; use the rectangular P3 corner tests as the clean 30/60 example.
- Finite-edge cells projecting beyond a beam endpoint are exported as endpoint forces, not as artificially enormous line-load ordinates.
- P12 now uses the actual y=13.8 to 18.1 extent across D07/D03; the previous 4.0/0.3 m root split was inconsistent with that footprint.

Reproduce: `python hw2_beam_loads.py`. Verification: `python verify_hw2_mixed_supports.py`.
