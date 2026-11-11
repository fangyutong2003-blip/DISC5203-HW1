# HW3 - Audited extraction and rigid-diaphragm analysis

Start with [the Task 1 report](HW3_Task_01_Report.md). The assigned-plan Task 1 pipeline is complete; the chronology below and earlier artifacts remain as process evidence. The formal Task 2 comparison is still pending.

The provisional common-geometry baseline now has [Task 3 analytical centres](HW3_Task_03_Analytical_Report.md) and [Tasks 4/5 OpenSees verification](HW3_Task_04_05_OpenSees_Report.md). Analytical checks pass 54/54; model/decomposition checks pass 75/75. The declared model includes both rectangular-wall bending axes and shear; strong-direction-only sensitivity is separately tabulated. No Task 2 winner is claimed.

The [Tasks 6/7 report](HW3_Task_06_07_Modification_Report.md) records the inward T9/T10 thickening proposal, exact/rounded eccentricity, force redistribution, concrete cost and actual modal checks. Verification passes 133/133 under the frozen-mass assumption. For Task 8, NewPlan is retained and [NIST Figure 2 is selected as the third plan](records/Task_08_Found_Plan_Selection.md); processing and comparison of both additional plans remain pending.

Student: Fangyutong, 21353319. Assigned drawing: Floor Plan 3.

The retained [2026-11-10 additional-plan portability checkpoint](HW3_Task_08_Additional_Plans_Report.md) documents fixed-rule classical, dual OCR, bar matching and never-selected forests on NewPlan/NIST, including failures before actual reader intake. Current reader packages remain **V4**, with six NewPlan and four NIST questions; earlier drafts are superseded. UTF-8/LF serialization and actual Git bytes were verified. The subsequent reader evidence and current limitations are recorded below.

The [Task 8 workflow review R2](HW3_Task_08_Workflow_Review_R2.md) now retains actual isolated `gpt-6.1-sol` readings and the student-pasted Grok 4.5 replies. Both resolve nine R2-scorable flags with zero incorrect answers; NP-F03 remains unscorable. Original pre-response V4 scores and the post-response R2 revision are both retained. There is no winner or full-plan promotion; source-based geometry and mechanics remain pending.

## Retained early-stage chronology (superseded)

Task 1A has an initial classical run: 20 connected components, including merged walls and artifacts. Labels, scale and element-level scores remain pending. No reader has been promoted; no final CM/CR has been calculated. DP v4.1 is the student's proposed second reader; exact service model ID and image capability must be recorded from the actual session.

Task 1B now has two raw OCR readings and 21 unique provisional label/bar matches. A preliminary 60-tree weakly supervised forest is retained but never selected. Five draft review flags are prepared; the independent reference, final scale and flag freeze remain pending.

![Provisional one-label-per-bar matches](outputs/Plan3/stage03/Provisional_Label_Matches.png)

## Reproduce current evidence

Install HW3/requirements.txt in a virtual environment, then run from the repository root:

```text
python HW3/scripts/stage01_classical.py
python HW3/scripts/stage02_ocr.py
python HW3/scripts/stage03_bars.py
python HW3/scripts/stage04_forest.py
python HW3/scripts/prepare_review_flags.py
python HW3/scripts/stage05_metric_geometry.py
python HW3/scripts/check_metric_reference.py
python HW3/scripts/verify_extraction_stage.py
```

## Current metric calibration

See [metric calibration review](outputs/Plan3/stage05/Metric_Geometry_Review.md) and [labelled-size overlay](outputs/Plan3/stage05/Labelled_Size_Rectangles.png). The two-stroke growth route failed the dimension-chain gate and is retained; a separately measured effective-bar-growth route passes. These are unpromoted candidates while floor extraction and independent reference review remain open.

The student can fill the [independent reference form](records/Independent_Reference_Form.md) directly from the source crops before viewing either model's answers.

![Initial connected components, not final elements](outputs/Plan3/stage01/07_Component_Overlay.png)

## Evidence locations

- sources/: course brief and original drawing assets.
- records/: source hashes, iteration log and readable Git history.
- prompts/: identical instructions for both image readers.
- scripts/: extraction and deterministic validation.
- outputs/: actual extraction outputs; future OCR, flags, reference and forest artifacts.

## Hook installation

Run `git config core.hooksPath .githooks`. If the default Python lacks dependencies, set HW3_PYTHON to a suitable Python executable. The hook reads staged text rather than unstaged copies. It rejects non-English text, malformed JSON and conflict markers, and validates staged Python syntax. Full engineering verification is a separate documented gate once the calculation stages exist.

Do not call preparation records completed engineering results. Raw external-model responses are collected by the student and retained verbatim.
