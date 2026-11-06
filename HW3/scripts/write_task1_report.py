"""Assemble the English Task 1 evidence report and answer-free reader package."""
import csv
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/Plan3"


def load(path):return json.loads((OUT/path).read_text(encoding="utf-8"))


def main():
    geometry=load("task1/Elements_After_Reader_A.json")
    floor=load("task1/Floor_Dimension_Record.json")
    forest=load("stage04_forest/Forest_Report.json")
    score=load("task1/Score_Sheet.json")
    verification=json.loads((ROOT/"records/Task1_Verification.json").read_text())
    rows=["# DISC 5203 HW3 - Task 1 Report","",
          "Student: Fangyutong | Student ID: 21353319 | Floor Plan 3","",
          "**Status:** Task 1 pipeline completed for the assigned plan, including one documented crop-only VLM review. Task 2 model comparison and final promotion are not complete.","",
          "## A. Classical reading, grid and closed regions","",
          "The source image is unchanged. Ink threshold is grey < 225; the 11-pixel 45-degree opening isolates hatching, followed by close17/open21. An open17 alternative is preserved because the brief and L09 recap use different wording. The aspect-ratio wall rule is 4:1. No VLM supplies coordinates.","",
          "[Raw components and parameters](outputs/Plan3/stage01/Classical_Components.json) record 20 connected objects. A retrospective label audit finds 21 element labels across 17 named objects: 16 single-label objects and one object merging T4-T8, plus 3 unlabelled artifacts. No matched main wall is broken along its axis. These are declared association-based scores, not an unseen benchmark.","",
          f"The L09 label score (single labels - shared labels - unlabelled objects) rises from {score['classical']['score']} to {score['label_supervised']['score']} after bar/label association.","",
          "![Original component overlay](outputs/Plan3/stage01/07_Component_Overlay.png)","",
          "[Measured column grid](outputs/Plan3/task1/Column_Grid.json) clusters only axes within 0.15 m; no individual centre is snapped.","",
          "### Floor, balconies and exclusions","",
          "The floor is reconstructed by a deterministic union of the archived HW1 dimension-chain rectangles, not by tracing all ink. The three body rectangles and five projections P10-P14 retain their dimensions. P10 placement and short returns remain image-derived assumptions. This is a reused, documented source reading rather than a claim of fully automatic outline detection.","",
          "| Quantity | Area (m2) |","|---|---:|",
          f"| Gross outline including five balconies | {floor['gross_area_m2']:.6f} |",
          f"| O1/O2 voids | {floor['void_area_m2']:.6f} |",
          f"| Separate stair/core S1 | {floor['separate_stair_area_m2']:.6f} |",
          f"| Ordinary flat slab | {floor['ordinary_flat_area_m2']:.6f} |",
          f"| Net horizontal area including separate S1 | {floor['net_horizontal_area_including_stair_m2']:.6f} |","",
          "See [dimension records and assumptions](outputs/Plan3/task1/Floor_Dimension_Record.json) and [floor polygons](outputs/Plan3/task1/Floor_Zones.geojson). S1 is not a zero-load void; it is kept separate from ordinary slab allocation.","",
          "L1 midpoint-distance allocation to the new measured column centres and finite main-wall axes produces 21 closed, non-overlapping regions. The 0.01 m polygon union equals 179.250000 m2, with no gaps or overlaps above 1e-7 m2. The largest element-area change from a 0.02 m grid is 0.0602 m2.","",
          "![Closed regions and floor exclusions](outputs/Plan3/task1/Floor_and_Closed_Regions.png)","",
          "[Closed region GeoJSON](outputs/Plan3/task1/Closed_Tributary_Regions.geojson) and [area table with differences from HW1](outputs/Plan3/task1/Candidate_Tributary_Areas.csv) are saved. The new geometry omits historic approximate returns, so its per-element diagnostic areas need not equal the accepted HW1 areas. [Inherited HW1 loads](outputs/Plan3/task1/Inherited_HW1_Loads.csv) remain unchanged. The JSON check sum_axial_kN is explicitly the five-storey ordinary-slab G+Q contribution only; stair and element self-weight are separate in the inherited table.","",
          "## B. Labels, scale and element record","",
          "Local RapidOCR reads the original and long-line-removed images separately: 52 and 61 text detections. The raw strings, boxes, confidence and source hashes are preserved. Parsing was revised after concatenated IDs and dimensions generated implausible splits; the final result contains 21 label/size hypotheses. Directional openings split the merged core into bars. Unique assignment and nominal thickness classes prevent a 250 mm label from claiming a 400 mm bar.","",
          "[Dual OCR evidence](outputs/Plan3/stage02/Dual_OCR.json) and [bar associations](outputs/Plan3/stage03/Bar_Label_Matches.json) retain the actual outputs.","",
          "### Scale rejection and revision","",
          "Thin-line sampling measured 6 px, so the L09 two-stroke growth route uses g=12 px. Its label-median scales (159.5 and 159.0 px/m) fail the 2% overall dimension-chain check and are retained as rejected. A separate effective bar-growth fit gives label-median scales x=163.194599 and y=162.568259 px/m. Although these pass the scale check, they produce five small footprint/floor inconsistencies.","",
          f"The final coordinate transform is therefore anchored globally to the printed 1.00+8.20+1.00 m width and 19.20 m height: x={geometry['scale_px_per_m']['x']:.6f}, y={geometry['scale_px_per_m']['y']:.6f} px/m. All centres use this same affine transform; no per-element snapping, clipping or VLM coordinate is used. All 21 labelled rectangles are inside the retained outline at the 1e-6 m2 footprint-area tolerance.","",
          "[Local calibration](outputs/Plan3/stage05/Metric_Calibration.json), [final global anchor](outputs/Plan3/task1/Global_Dimension_Anchor.json), [before/after footprint audit](outputs/Plan3/task1/Calibration_Revision_Audit.json) and [final geometry audit](outputs/Plan3/task1/Element_Geometry_Audit.json) record the revisions. Every main bar has at least 85% axial support in the original diagonal-hatch image (100% here). This does not prove the dimensions or eliminate source-reading uncertainty.","",
          "The origin is the bottom-left exterior datum of the main structural footprint; x points right and y up. The bottom balcony reaches y=-1.2 m. Coordinates are image-derived, not CAD.","",
          "### Final Task 1 element schedule","",
          "| Label | Class | Centre x (m) | Centre y (m) | Printed size (mm) |",
          "|---|---|---:|---:|---|"]
    rows += [f"| {e['labels'][0]} | {e['class']} | {e['centre_m'][0]:.4f} | {e['centre_m'][1]:.4f} | {'x'.join(map(str,e['size_mm']))} |" for e in geometry["elements"]]
    rows += ["","[Original classical JSON](outputs/Plan3/task1/Elements_Classical.json) follows the required source/scale/elements/floor/checks structure. [Reader-A copy](outputs/Plan3/task1/Elements_After_Reader_A.json) adds field-specific provenance while preserving original geometry and all flag evidence. Unknown wall continuity is kept null where it was not queried.","",
             "## C. Retained forest - never selected","",
             "The actual run trains 60 trees on 120000 weak-labelled pixels with 15 features and seed 5203, at half image resolution. Labels come from the classical mask. The model, probability image and thresholded mask are retained; none is promoted. This is a training-plan experiment, not a generalisation score.","",
             "| Feature | Importance |","|---|---:|"]
    rows += [f"| {k} | {v:.6f} |" for k,v in forest["feature_importance"].items()]
    rows += ["","Blur and ink density dominate this actual run; diagonal features do not dominate. The difference from the lecture is reported, not tuned away. See [forest report](outputs/Plan3/stage04_forest/Forest_Report.json), [retained model](outputs/Plan3/stage04_forest/Forest_Never_Selected.joblib) and [probability image](outputs/Plan3/stage04_forest/Forest_Probability.png).","",
             "## D. Crop-only VLM review and preserved originals","",
             "A second classical reference pass uses threshold180 on unmarked source crops, fresh local OCR without line removal, and interior raw-ink axial occupancy for continuity. It resolves five reference questions before the recorded Task 1 answer file. It shares the OCR engine and query locations with the main pipeline, so it is an alternative defensible reading, not statistically independent ground truth or student hand signoff. Its raw readings and decisions are retained in [Reference.json](outputs/Plan3/independent_reference/Reference.json).","",
             "[Frozen input package](outputs/Plan3/reader_package_v1/Questions.md) contains five crops, questions in fixed order, common instructions, hashes and a confidence threshold of 0.80. Only queried fields are scored and applied. The reference is excluded from the answer-free reader ZIP.","",
             "The GPT-6 Codex session actually inspected the five frozen crops using native image viewing and supplied [structured answers](outputs/Plan3/reader_A_task1/Raw_Answers.json). Five answers passed the threshold and agreed with the alternative reference. The application rule writes a copy, changes no centre, and records corrected-by provenance. See [application log](outputs/Plan3/reader_A_task1/Application_Log.json).","",
             "**Exposure limit:** this engineering session had previously seen the draft crops and OCR/historical audit. This is a real Task 1 reading, not a blinded Task 2 comparison. [Run metadata](outputs/Plan3/reader_A_task1/Run_Metadata.json) discloses this. For formal Task 2, collect both readers in isolated sessions with the identical answer-free input package. DP has not been run or promoted. No student review or external API request is fabricated.","",
             "## Verification and iteration evidence","",
             f"Task 1 verification: {verification['passed']}/{verification['total']} checks passed; final listed geometry warnings: {len(verification['known_geometry_warnings'])}. These check artifact integrity, declared assumptions, closure and preservation; they do not establish an unknown-plan result or a Task 2 winner.","",
             "See [verification details](records/Task1_Verification.json), [iteration log](records/Iteration_Log.md), [readable Git history](records/Git_History.md), [project guidance](../AGENTS.md), [reusable procedures](../skills.md) and the tracked pre-commit hook. Historic steps are retained.","",
             "## Reproduction","","Run from the repository root with HW3/requirements.txt installed:","","```text",
             "python HW3/scripts/stage01_classical.py","python HW3/scripts/stage02_ocr.py",
             "python HW3/scripts/stage03_bars.py","python HW3/scripts/stage04_forest.py",
             "python HW3/scripts/prepare_review_flags.py","python HW3/scripts/stage05_metric_geometry.py",
             "python HW3/scripts/check_metric_reference.py","python HW3/scripts/stage06_independent_reference.py",
             "python HW3/scripts/stage07_floor_and_record.py","python HW3/scripts/apply_task1_reader.py",
             "python HW3/scripts/verify_task1.py","python HW3/scripts/write_task1_report.py","```","",
             "Raw VLM answers are retained observations. The reproduction scripts validate and reapply those answers; they do not silently call or simulate a fresh model inference."]
    (ROOT/"HW3_Task_01_Report.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    package=OUT/"reader_package_v1"
    with zipfile.ZipFile(ROOT/"HW3_Reader_Package_V1.zip","w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(package.iterdir()):
            if p.is_file():z.write(p,p.name)
    # Verify delivered Markdown links without requiring a renderer.
    import re
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)",(ROOT/"HW3_Task_01_Report.md").read_text()):
        if not target.startswith(("https:","http:")) and not (ROOT/target).exists():
            raise FileNotFoundError(target)
    with zipfile.ZipFile(ROOT/"HW3_Reader_Package_V1.zip") as z:
        assert z.testzip() is None
        assert not any("Reference" in n or "Raw_Answers" in n for n in z.namelist())
    print("Saved Task 1 English report and answer-free reader ZIP")


if __name__=="__main__":main()
