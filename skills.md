# Reusable Project Procedures

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

