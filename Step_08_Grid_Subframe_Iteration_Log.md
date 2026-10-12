# Step 08 - Plan-Grid Subframe Human/Agent Iteration Log

## Human instructions recorded in English

1. Correct the previous beam tributary construction because complex support conditions may require 60/30-degree divisions rather than universal 45-degree divisions.
2. Continue the assignment after the student completes the required hand drawings separately.
3. Upload all process files and keep every submitted file, report, code comment, filename and Git commit message in English.

## Iteration decisions

### Revision 1 - Mixed slab-edge allocation

The earlier all-matched 45-degree allocation was rejected. The revised generator retains 45 degrees for matched conditions and uses 60 degrees from an assumed continuous edge and 30 degrees from an assumed simple edge. Every edge classification is exported for human review. The previous checkpoint was archived rather than deleted.

### Revision 2 - Closed polygons and actual load profiles

Open direction lines and a forced residual support were rejected. Exact closed polygons, unresolved area and finite-edge ties are exported explicitly. Step 05 now stores actual strip-average profiles; Step 06 reads those profiles directly instead of fitting symmetric triangles/trapezia.

### Revision 3 - Subframe scope correction

The first subframe contained only the selected beam line and columns below it. It did not satisfy the stated requirement for a perpendicular bay. Those files remain historical evidence but are superseded for Tasks 8, 10 and 12.

The revised model is a 3D elastic one-floor plan grid. Beam A includes one bay east of the peripheral line. Beam B includes the south bay and the available supported branches north of the interior line. Actual Step 05 profiles are applied to every included floor beam. Vertical members extend to fixed bases and include self-weight.

### Revision 4 - Response sign and independent checks

The first 3D response extraction displayed the member-end bending sign opposite to the report convention. The plotted convention was corrected so positive is sagging and negative is hogging. A separate verifier checks source-profile fingerprints, represented beam loads, support self-weight, total applied load, vertical equilibrium, perpendicular member presence, selected-line coverage, internal span moment continuity, reaction sources and HW1 cross-check sources. The final grid verification passes 42/42 checks.

### Revision 5 - Independent coefficient route

HKConcrete 2013 Table 6.7 was added as an independent line-load scale check for clean rectangular panels only. Irregular and core panels are excluded rather than forced into an inapplicable table case. The coefficient route closes to 99.13%-100.01%; the polygon area route closes to 100%.

## Human gates still open

- Confirm every image-derived C/S slab-edge classification.
- Confirm the discrete wall-end representations at T3, T4 and T7.
- Resolve or expressly accept the unallocated core area and P1 finite-edge tie convention.
- Provide two dated handwritten moment calculations and four hand-drawn deformation sketches.
- Review the large Task 12 differences and approve the stated scope explanation.

The generated computations are reproducible, but these human gates prevent the current report from being labelled final.
