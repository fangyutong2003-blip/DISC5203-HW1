# Step 04 - Mixed-Support Revision Audit

## Request and scope

Correct the prior all-45-degree HW2 allocation where different slab-edge conditions require the coursework 60/30-degree convention. This revision changes HW2 Steps 04-06 only; HW1 numerical results and earlier Git history are preserved. The previous checkpoint is archived in HW2_Pre_Mixed_Support_Revision_b867ebd.zip.

## Implemented changes

1. Export a per-panel edge-condition schedule. C denotes an assumed continuous/restrained slab edge; S denotes an assumed simply supported slab edge. Beam end releases are a separate modelling decision.
2. Retain 45 degrees for C/C and S/S. Use 60 degrees from C and 30 degrees from S at mixed perpendicular corners. The P3/D16/D11 corner is the clean worked example; P3/D16/D12 stays at 45 degrees.
3. Replace raster ownership with closed polygon clipping. An adopted weighted finite-L1 extension handles partial and L-shaped boundaries; it is not a stiffness or general yield-line solution.
4. Export exact polygons, dashed boundaries, coloured areas, and a before/after comparison with a same-geometry matched-edge comparator.
5. Correct the finite cantilever-root extents, including P12. Report the 1.707500 m2 core remainder as unresolved instead of forcing it into a wall reaction.
6. Explicitly audit 2.584167 m2 of positive-area P1 ties between W_T3 and D06. The provisional list-order allocation is not a physically unique result.
7. Compute strip-average line loads from polygons and integrate the simply-supported midspan influence function exactly for each constant-load interval, splitting at midspan when needed. Keep any endpoint forces separate. No endpoint forces are produced by the current adopted allocation.
8. Feed actual, potentially asymmetric profiles directly into all four OpenSees models. Remove active symmetric reconstruction and total-force renormalisation. Store input SHA256 fingerprints for stale-result detection.
9. Retain the historical briefing but flag superseded values and illustrative sketch provenance. Clarify that the single-line subframe omits the perpendicular bay and is not a finished Task 3/12 submission.

## Verification

- 52 generation checks: panel coverage, overlaps, floor-accounting and profile integration.
- 147 separate verification checks: analytic square limits, mixed-corner geometry, exported P3 boundaries, independent point ownership, exclusions, areas, beam IDs and load integration.
- 33 OpenSees checks: simple/fixed closed-form benchmarks, profile fingerprints, independently summed applied loads, reaction equilibrium, local-force reconstruction and broad moment-scale screening.
- HW1 verification rerun: 23/23 passed; original checkpoint text retained.
- Polygon tolerance: 1e-8 m2; load-integration tolerance: 1e-7 kN. Fine-mesh solver equilibrium tolerance: 1e-4 kN absolute and 1e-6 relative; this is explicitly looser than the old coarse-mesh absolute tolerance. Maximum observed vertical imbalance: 3.965e-5 kN.

Passing these tests establishes numerical consistency of the adopted model, not the correctness of unverified support conditions or its completeness as a submission.

## Review still required

- Confirm each assumed C/S condition from lecture conventions or connection details, especially full-edge restraint at partial cantilever roots.
- Confirm physical-to-idealised support segmentation, especially the core boundary W_CORE_R and the P1 finite-edge tie region. Grey wall/column footprints are visual references, not additional active support lines.
- Resolve the unallocated core area before claiming complete load-path closure.
- Complete the required subframe extent, coefficient-route reconciliation and student hand sketches separately if still required by the assignment.

## Reproduction

```text
python -m pip install -r requirements.txt
python hw2_beam_loads.py
python verify_hw2_mixed_supports.py
python step06_run_all.py
python verify_step06_opensees.py
```

HW1-derived coordinate inputs must exist; README documents how to regenerate them. The old ZIP is needed only for the historical comparison. All text and Git records are in English.
