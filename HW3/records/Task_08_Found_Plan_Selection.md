# Task 8 - Found-plan source selection

Recorded: 2026-11-10. Student: Fangyutong, 21353319.

Status: source selected for the third plan; extraction, reader evaluation and structural calculation are pending. This is an agent-authored source recommendation, not a student-signed prediction or completed generalisation experiment.

## Selected public source

Elsibaie, S., et al. (2025), *Estimating the Costs and Performance of Enhanced Building Design: A Case Study of Functional Recovery for New Buildings*, NIST Technical Note 2351, Figure 2, printed page 9 (PDF page 17).

- [Persistent source](https://doi.org/10.6028/NIST.TN.2351)
- [Original PDF](https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2351.pdf)
- [Retained PDF](../sources/third_plan_candidates/NIST_TN2351_2025.pdf)
- [Full source page](../sources/third_plan_candidates/NIST_Page_09.png)
- [Unannotated plan render](../sources/third_plan_candidates/NIST_Figure_02_Plan.png)

The building is a research archetype of a reinforced-concrete shear-wall office building, not an identified constructed property. Its square plan has four bays per direction: overall 120 ft = 36.576 m and bay spacing 30 ft = 9.144 m. Four perimeter walls provide two wall directions. Figure 2 provides generic component descriptions rather than individual element IDs or a complete section schedule. The adjacent text describes 25 gravity columns, whereas the schematic shows 21 separate square column symbols with four perimeter mid-grid positions occupied by walls; this discrepancy must remain flagged.

Republished courtesy of the National Institute of Standards and Technology. [NIST publication reuse policy](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications). Retain the source attribution; this is not a blanket CC0 claim for every third-party contribution.

## Why this plan

The student's request was a third plan of roughly comparable, manageable complexity. The course NewPlan has a rectangular grid and a larger wall set. This found plan is somewhat simpler, but remains a wall-and-column floor plan with explicit scale and both wall directions. Compared with assigned Plan 3, it changes the drawing convention (solid symbols instead of hatching), units, outline and label availability. These changes can expose genuine limits of the frozen extraction rules. Task 8 explicitly permits missing size strings as a relevant difference.

Its regular symmetry provides a useful limiting check: equal opposing wall properties and uniform mass should produce CM = CR to numerical tolerance. This is a conditional prediction, not an already computed result. An unchanged symmetric case must not be advertised as an eccentricity-reduction design achievement.

## Missing information and fixed-procedure gate

1. Freeze this source and hashes before any extraction. Apply the existing rules and record failures before proposing revisions; do not tune thresholds to make the new solid symbols look like the training drawing.
2. There are no printed individual C/T IDs. Any IDs assigned for bookkeeping must be marked analyst-generated. No invented labels may count as OCR or VLM successes.
3. Do not infer a precise wall thickness or column section from schematic symbol widths. The assignment's default wall thickness of 250 mm and storey height of 3 m may be used only as disclosed exercise assumptions. Use the course material properties; do not silently import the paper's full-building model.
4. Wall lengths and locations require independently documented image measurements with both-axis calibration and a declared tolerance. A guessed nominal length cannot be presented as a printed size. Column-section-dependent self-weight remains pending unless a defensible source or explicit assumption is supplied.
5. Missing size strings cannot pass a printed-size agreement gate. Retain these unresolved flags and distinguish visual continuity questions from unsupported section dimensions. Any structural sensitivity calculation using assumptions remains provisional rather than a promoted extraction.
6. Prepare one frozen crop/question/order package for the two actual readers, retain raw responses and identifiers, freeze an independent reference by the established route, and run the unchanged no-regression gate. No new VLM run has occurred at this selection stage.
7. Subsequent CM, stiffness, CR and OpenSees checks must distinguish source facts, image measurements and exercise assumptions. Task 8 stays pending until both additional plans are processed and compared.

## Other candidates reviewed

- Seo, Hu and Davaajamts (2015), [Sustainability 7, 14287-14308](https://doi.org/10.3390/su71014287), Figure 1(a): clearer section information, but the walls act along one principal direction and the original system relies on frames. Not selected for the present wall-based comparison.
- Velarde et al. (2025), [Buildings 15, 1783](https://doi.org/10.3390/buildings15111783), Figure 2: a regular grid, but that figure does not provide a complete wall layout; configurations require additional 3D interpretation. Not selected.

Downloaded comparison material is retained locally as search evidence; only the selected NIST source and its renders are part of this source-selection commit. No rejected candidate is used as calculation input.

## Reproduce the view

From the repository root, with Poppler available:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File HW3/scripts/render_found_plan.ps1
```

The execution policy override applies only to that process and does not change the saved system policy. The figure is a PDF rendering crop; no walls, labels or dimensions were added. Original and rendered file hashes are in [the source manifest](../sources/third_plan_candidates/NIST_Source_Manifest.json).
