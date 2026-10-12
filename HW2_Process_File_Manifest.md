# HW2 Process-File Manifest

This manifest records the English process evidence retained for submission. Historical files are not deleted; superseded outputs are labelled in the reports or preserved in the checkpoint archive.

## Source and entry points

- `README.md` - repository entry point and reproduction commands.
- `AGENTS.md` - project rules and calculation sequence.
- `requirements.txt` - reproducible Python dependencies.
- `HW2_Final_Report.md` - final continuous English submission report.
- `HW2_Submission_Report_Draft.md` - retained pre-finalisation draft and process evidence.
- `HW2_FloorPlan3_Marked_Beams.png` - source plan with the two assigned beam lines.

## HW1 retained basis

- `HW1_Final_Report.md` and `HW1_Checkpoint_Report.md`.
- `Step_01*` - coordinate system, vertical-element schedule and tributary regions.
- `Step_02*` - floor loads and vertical-element axial forces.
- `Step_03*` - independent HW1 verification.
- `tributary_regions.py`, `step02_loads.py`, `verify_results.py`.

## HW2 Task 1 / Step 04 - beam geometry and tributary areas

- `hw2_beam_loads.py` - retained geometry definitions and current command entry point.
- `hw2_mixed_supports.py` - current mixed-edge polygon generator.
- `verify_hw2_mixed_supports.py` - independent analytic/export checks.
- `Step_04_Beam_Census.csv` and `HW2_Beam_Census.png`.
- `Step_04_Slab_Edge_Conditions.csv`.
- `Step_04_Closed_Regions.geojson`.
- `Step_04_Beam_Tributary_Area_Contributions.csv`.
- `Step_04_Finite_Edge_Ties.csv`.
- `Step_04_Revision_Comparison.csv`.
- `Step_04_Mixed_Support_Verification.csv`.
- `Step_04_Independent_Mixed_Verification.csv`.
- `Step_04_Beam_Census_and_Tributary_Areas.md`.
- `Step_04_Mixed_Support_Revision_Log.md`.
- `HW2_Beam_Tributary_Boundaries.png` and `HW2_Beam_Tributary_Areas.png`.
- `HW2_Pre_Mixed_Support_Revision_b867ebd.zip` - preserved pre-revision process checkpoint.

## HW2 Task 2 / Step 05 - line loads

- `Step_05_Beam_Line_Loads.csv`.
- `Step_05_Beam_Load_Profiles.csv`.
- `Step_05_Beam_Endpoint_Loads.csv`.
- `Step_05_Beam_Line_Loads_and_Worked_Example.md`.
- `HW2_D18_Worked_Line_Load.png`.
- `step05_coefficient_check.py`.
- `Step_05_Coefficient_Area_Reconciliation.csv`.
- `Step_05_Coefficient_Area_Panel_Closure.csv`.
- `Step_05_Coefficient_Area_Reconciliation.md`.

## HW2 Tasks 3, 6, 7 and 11 / Step 06 - standalone and historical iteration

- `Step_06_OpenSees_Model_Config.json`.
- `step06_opensees_core.py`, `step06_run_all.py`, `verify_step06_opensees.py`.
- Four explicit `Step_06_*_OpenSees.py` entry files.
- `Step_06_BeamA_Pure_Result.json`, `Step_06_BeamB_Pure_Result.json` and response figures.
- Historical single-line subframe result JSON files and response figures; superseded for final Task 8 comparison.
- `Step_06_OpenSees_Model_Summary.csv`, `Step_06_OpenSees_Support_Reactions.csv` and `Step_06_OpenSees_Verification.csv`.
- `Step_06_Mixed_Support_PreSolve_Screening.md`.
- `Step_06_PreAnalysis_Moment_Estimates.md` - adopted Beam A and Beam B \(qL^2/8\) screening calculations.
- `Step_06_PreSolve_Expected_Shapes.png` - illustrative computer output, not student hand work.
- `Step_06_OpenSees_Briefing_and_Iteration_Log.md`.
- `Step_06_OpenSees_Models_and_Verification.md`.
- Historical Step 06 HW1 comparison files; superseded by Task 12 grid results.

## HW2 Tasks 8, 10 and 12 - plan-grid subframes

- `step08_grid_subframes.py`.
- `verify_step08_grid_subframes.py`.
- `Step_08_BeamA_Grid_Result.json` and `Step_08_BeamB_Grid_Result.json`.
- `Step_08_BeamA_Selected_Response.csv` and `Step_08_BeamB_Selected_Response.csv`.
- `Step_08_BeamA_Grid_Response.png` and `Step_08_BeamB_Grid_Response.png`.
- `Step_08_BeamA_Whole_Grid_Deformed.png` and `Step_08_BeamB_Whole_Grid_Deformed.png`.
- `Step_08_Grid_Subframe_Summary.csv`.
- `Step_08_Grid_Subframe_Reactions.csv`.
- `Step_08_Grid_Subframe_Verification.csv`.
- `Step_08_Grid_Subframes_and_Task12.md`.
- `Step_08_Grid_Subframe_Iteration_Log.md`.
- `Step_12_HW1_Grid_Subframe_Cross_Check.csv` and comparison PNG.

## Student-supplied material

- `Task_09_Hand_Drawn_Deformation_Sketches.jpg` - one student-supplied sheet containing Beam A standalone, Beam A grid, Beam B standalone and Beam B grid deformation sketches.
- `Step_06_PreAnalysis_Moment_Estimates.md` - English calculation record used for the two simplified moment bounds.

The hand sketches and calculation record are linked in `HW2_Final_Report.md`. The final report adopts the current image-derived support schedule and wall-end idealisations while explicitly disclosing the unresolved core area and provisional P1 tie convention.

The pre-existing HW1 Git history is preserved under the repository audit rule. All new HW2 filenames, file contents, code comments, report text and commit messages are English.

## Language audit note

The submitted reports, calculations, source files, code comments, tracked filenames and all HW2 commit subjects are in English. One inherited pre-HW2 history entry, commit `2490a98`, has the Colab-generated Chinese subject whose English meaning is "Created with Colab." It is retained only to preserve the original Git audit history; it is not assignment content or a current HW2 commit message.
