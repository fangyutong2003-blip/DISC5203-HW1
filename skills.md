# Reusable Project Procedures

## HW3 image extraction and two-reader comparison

1. Hash sources; threshold at 225; preserve morphology parameters, binary images and connected components.
2. Read OCR before and after long-line removal; record raw boxes. Split bars and match each label once within thickness class; retain all uncertain completions as flags.
3. Fit the weakly supervised forest with a fixed seed, retain its artifact and feature importance, and mark it never selected.
4. Freeze an independent reference with a documented separate reading route.
5. Freeze identical flag IDs, crop hashes, questions, order and JSON format for both readers. Save each original answer with exact model/version and collection time.
6. Score resolved and broken flags against the reference. Abstention is unresolved. A self-reported confidence is not a calibrated probability.
7. Apply validated answers to copies through deterministic geometry rules. Recheck after application and reject regressions; readers never supply vertex coordinates.

### Isolated readers and post-response reference audits

- After explicit student authorisation for delegation, start a history-free session per plan. Deliver only the exact frozen common instructions, ordered question and image, one flag per turn. Retain actual payloads and completed-model outputs. Derive model identity from available runtime metadata without inventing an unavailable weights snapshot; retain unknown self-reports unedited.
- Do not call different web/native interfaces the same harness. Preserve interface limitations and original versus follow-up replies. A student-reported Grok version remains student-reported.
- Freeze the prospective reference method in Git before running it. If responses were already visible, disclose the new reference as post-response sensitivity. Keep original-reference scores and reference bytes. The source-only reference program must never load reader-answer files.
- Unresolved reference questions are unscorable, not automatically correct or broken. Score asked fields with confidence >=0.8; high confidence is not an accuracy tie-break. Adversarially check wrong answers, duplicate IDs, abstention and loss of another reader's cleared flag.
- Require complete geometry, both-axis calibration, dimensions and area conservation separately from the local flag gate. Retain failures and label any recovery method as a revision; do not silently retune the frozen extraction.
- Write hashed JSON/JSONL and prompts as UTF-8/LF before packing. Validate actual Git index/object bytes. Preserve a real installed-hook damaged-fixture rejection and repaired-fixture acceptance log.

## Briefing to rigid-diaphragm model

1. Save the student's actual instruction and an explicitly agent-authored detailed briefing proposal before solving.
2. State origin, units, wall lengths/orientations, mass area, openings, H, E, nu, shear areas, supports, diaphragm constraints and design load.
3. Derive the hand stiffness and CM first, with a prediction and dimensional checks.
4. Build matching Timoshenko walls, correct local axes, fixed bases and an explicit rigid diaphragm.
5. Recover flexibility using three unit loads; compare CR by hand and model; verify reciprocal flexibility, equilibrium and zero rotation through CR.
6. Test bending-only versus shear-inclusive limits and independent simple/fixed beam limits where applicable. A pure beam and a finite-stiffness subframe are not automatically zero/infinite continuity limits.
7. Quantify before/after wall modifications with mass fixed. Record actual runs and unresolved differences.

## HW2 mixed-support load transfer (retained)

Matched orthogonal supports use 45-degree divisions. Under the adopted course convention a continuous/simple corner uses 60 degrees from the continuous edge and 30 degrees from the simple edge. Preserve actual non-uniform profiles, distinguish force-equivalent from moment-equivalent UDL, and reconcile area and applied force independently.

## Image-to-geometry review

1. Read dimension chains before estimating pixel coordinates.
2. Define one origin and record every point in metres.
3. Separate source dimensions from image-derived assumptions.
4. Plot coordinates over the source image and inspect openings, recesses, projections, and wall returns.
5. Record unresolved geometry instead of silently interpolating it.

## Tributary-area construction

1. Represent columns by centre points and walls by finite support-axis segments.
2. Construct midpoint divisions between adjacent supports.
3. Extend 45-degree divisions from orthogonal wall corners to the appropriate midpoint boundaries.
4. Clip the partition to the slab domain and remove confirmed openings or separately modelled zones.
5. Require closed, non-overlapping regions.
6. Reconcile the sum of all tributary areas to the adopted slab area.
7. Repeat with a coarser grid to estimate discretisation sensitivity.

## Vertical-load calculation

1. Calculate slab dead load from thickness and concrete unit weight.
2. Multiply dead and live area loads by each tributary area.
3. Add column or wall self-weight using the labelled section and storey height.
4. Add separately modelled zones using an explicit allocation rule.
5. Accumulate characteristic loads downward through the supported floors.
6. Report each load combination with its equation and units.

## Deterministic verification

1. Read the delivered CSV files rather than internal script variables.
2. Recompute expected values independently.
3. Compare expected and actual values using stated tolerances.
4. Check IDs, row counts, area closure, load closure, accumulation, and nonnegative values.
5. Include representative manual checks.
6. Fail the verification command when any required check fails.

## Git checkpoint procedure

1. Inspect `git status` and exclude temporary inspection artifacts.
2. Review `git diff` before staging.
3. Run the deterministic verification.
4. Commit one meaningful stage with an English message.
5. Confirm the submission copy is synchronized and clean.

