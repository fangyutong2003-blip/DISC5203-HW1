# HW3 Iteration Log

## 2026-11-06 - Stage 00, authorised setup

- Student instruction, translated from Chinese: "I will find the other model myself. Give me instructions to send to it. I plan to use DP v4.1. You can proceed with the tasks; save information, iterations and Git history."
- The student highlighted the prior HW2 deductions for thin initial briefing, hard-to-inspect Git history, incomplete guidance/procedures and missing formal hooks.
- Agent action: extend AGENTS.md and skills.md; add a tracked pre-commit hook; preserve source assets and hashes; begin classical extraction with explicit intermediate images.
- Reader comparison status: pending. No DP response or winning model is claimed.
- Structural briefing status: future agent proposal; student-authored structural expectations have not yet been supplied.
- Known brief ambiguities to resolve before mechanics: stiffness-versus-flexibility CR expressions, per-storey versus five-storey mass, and the dimensional form of the torsional amplification expression.

### Stage 00 checks and revisions

- A deliberately malformed staged JSON fixture was rejected by the installed hook. The repaired staged fixture passed. See Hook_Exercise.json.
- The first hook exercise attempted to launch `sh` directly, unavailable on PATH. It was revised to `git hook run pre-commit`, using Git's own hook runner. A real commit attempt also failed while the malformed fixture was staged; it succeeded after repair.
- Existing runtime lacked cv2, sklearn and OpenSees. A dedicated .venv_hw3 environment and HW3/requirements.txt were added. Initial extraction attempts before dependency installation completed failed at the cv2 import; no detection results were claimed from those attempts.

## Stage 01 - Classical image evidence

- Actual run: stage01_classical.py produced 20 connected components on the unchanged assigned image. Binary mask, source-shape and component pixel-area closure checks passed.
- Visual overlay review: a page-border component and small text artifacts are present; the T4/T5/T6/T7/T8 core is merged. Therefore component count is not claimed as named-element recall.
- Threshold, diagonal hatching, close17/open21, an open17 alternative and a long-line-removal image are retained. Scale, labels and merge/break scores remain pending independent assessment.
- The source brief's morphology wording differs from the L09 recap. Both the chosen close17/open21 route and an open17 alternative are explicitly recorded rather than silently treating the wording as identical.
- Two dependency installer invocations overlapped and one returned a Windows file-lock error. OpenCV was importable and the classical stage completed. Full environment verification is recorded separately; no forest training or mechanics run is claimed here.

## Stage 02 - Dual OCR and provisional label supervision

- Used local RapidOCR ONNX 1.4.4 because no Tesseract executable was available. This is a text detection/recognition stage, not a VLM flag reader.
- Original reading: 52 text detections. Long-line-removed reading: 61. Raw text, boxes, confidence and input hashes are retained.
- Initial parsing allowed implausible zero dimensions and split concatenated label/size strings incorrectly. Revised to enumerate plausible splits and preserve explicit spaces. The final export contains all 21 label/size hypotheses.
- Directional bars and square-column candidates yielded 21 unique provisional label matches. Visual overlay review confirmed the core wall separation and label locations. This is agent review, not an independent human reference or a model-comparison result.
- Square-column median gives an uncorrected scale seed of 183.75 px/m. It is not promoted: measured stroke growth, directional scale checks, metric origin and labelled-size extent support are still required.

## Stage 03 - Retained forest and draft review package

- Actual preliminary experiment: 120000 weak-labelled pixels, 15 features, 60 trees, random seed 5203, half-size Plan 3. Fitting took approximately 3.61 seconds. Model and probability/mask images are retained and explicitly never selected.
- Largest importances were blur8 (0.2147), blur4 (0.1592) and ink-density9 (0.1553). The 45-degree filters did not dominate this experiment. No result was tuned to imitate the lecture; no unseen-plan accuracy is claimed.
- Five draft flags were generated from single-pass label readings and merged-component containment. Crops, hashes, questions and field scopes are saved. The package remains DRAFT until an independent reference and final gate are frozen.
- No external-model answer, winning reader, signed student prediction or final structural result has been manufactured.

## Stage 05 - Metric scale gate and archived dimension-chain audit

- Raw thin-line sampling measured a median 6 px stroke. Applying the L09 two-stroke growth of 12 px gave x=159.5 and y=159.0 px/m, failing the declared 2% dimension-chain calibration gate. This rejected route remains in Metric_Calibration.json.
- A separate extent-versus-labelled-length regression measured effective bar growth of approximately 4.61 px (x) and 4.86 px (y). The resulting median scales are x=163.194599 and y=162.568259 px/m; both pass the overall 10.20 by 19.20 m dimension-chain cross-check.
- This is a documented methodological extension. Effective morphological-bar growth and thin-line stroke width are not interchangeable on this drawing.
- First run encountered an OpenCV Hough return-shape incompatibility. Normalising the line array to N-by-4 fixed it before results were exported.
- Exported 21 labelled-size metric rectangles with pixel-derived centres and a documented exterior structural origin. Their visual overlay agrees with the main wall/column bodies; short returns are not silently added as extra labelled walls.
- All 21 printed sizes agree with the archived HW1 main-element reading at commit 5f1eafe. Maximum centre difference is 0.172509 m; old coordinates were not substituted for measured new ones. The comparison is an audit aid, not proof of independent ground truth.
- Axial raw-ink support is 100% for all rectangles, but ink may include linework. This is explicitly weaker than a hatch-specific completion check and does not close all geometry questions.
- Independent_Reference_Form.md was prepared for an actual student source reading before either VLM response is collected. It contains no invented signoff or prefilled answers. The five-flag package remains a draft until the reference and crop questions are frozen.

## Stage 06 - Complete the assigned-plan Task 1 pipeline

- Student instruction, translated: "Finish Task 1."
- The independent-reference route was implemented as a separately tuned classical pass, so progress did not require fabricating student hand signoff. It uses threshold180, unmarked local crops, fresh local OCR without line removal and raw interior-ink axial occupancy. The OCR engine and query locations are shared; the independence limit is explicitly disclosed. Five reference questions were resolved. The reference and identical-reader v1 crops/questions were frozen by hash.
- The current GPT-6 session inspected the five frozen crops in order through native image viewing and recorded real structured answers. All five passed the >0.80 confidence gate and agreed on asked fields with the alternative reference. The original JSON stayed unchanged; answers were applied to a copy with corrected-by provenance. This session had prior crop/OCR exposure, so it is not a blinded formal Task 2 comparison. Fresh isolated readers are still required for that comparison.
- The floor was reconstructed from the retained HW1 dimension-chain rectangle union: 186.615 m2 gross including five balconies, 2.000 m2 voids O1/O2, 5.365 m2 separate S1, 179.250 m2 ordinary slab. This is inherited geometric evidence, not a new foundation-model outline inference.
- Local label-scale coordinates initially produced five footprint/floor inconsistencies. A deterministic single global dimension-anchor transform (x=164.411765, y=164.114583 px/m) was then applied to every measured centre using the printed overall chains. No per-element snapping, clipping or VLM coordinate was used. The prior local calibration and before/after audit remain recorded. All 21 final labelled footprints are inside the retained floor at 1e-6 m2 area tolerance, and all have 100% axial diagonal-hatch support.
- Generated closed 0.01 m L1 tributary polygons with no overlaps or gaps above 1e-7 m2. Their union equals 179.250 m2. Max per-element 0.02-to-0.01 m area change is 0.0602 m2. Main-wall rectangles omit approximate HW1 returns; diagnostic differences and the unchanged inherited HW1 load table are retained separately.
- The initial retrospective score is 8: 16 single-label objects minus 5 labels sharing the merged core minus 3 unlabelled artifacts. Bar/label association yields 21 single-label candidates and score 21. These are association-based source audits, not unseen-plan accuracy metrics.
- Final Task 1 verification passes 71/71 checks, with zero listed final geometry warnings. The English report, executable reproduction, raw reader answers, metadata, forest artifact, source/classical outputs, score sheet and answer-free ZIP are preserved. No DP result, winner, student hand review or final CM/CR is claimed.

## 2026-11-10 - External reader answers received

- The student pasted five original JSON answers in flag order, then identified the provider as "gork", recorded as user-reported Grok. This supersedes the earlier proposed DP reader; no DP run is claimed.
- Exact website model/version, original transcript/screenshots and actual inference time have not been supplied. Unknown metadata is null rather than invented.
- All five records are preserved without correcting their contents. Confidence values are 0.95, 1.00, 1.00, 0.95 and 1.00.
- Reference scoring and a provisional comparison were generated by compare_received_readers.py. The engineering-session first reader has context exposure and a different execution environment; the report explicitly retains those limits. No formal winner or structural CR result is inferred merely from answer confidence.

### Model identity follow-up

- The student subsequently confirmed the external model as Grok 4.5. Metadata and the comparison table now use that student-reported version. The original answers remain unchanged; screenshot/transcript verification and execution-environment limitations remain separately recorded.

### Screenshot follow-up

- The student supplied an original website screenshot corroborating P3-F05, the pasted JSON answer, and the chatbot's self-description as Grok 4.5. The selector only reads Fast, so the exact backend version remains unverified.
- Original screenshot retained locally in ignored local_evidence because unrelated personal sidebar conversations are visible. A tracked English evidence description records what is and is not established; raw model answers are unchanged.

## 2026-11-10 - Task 3 analytical baseline before OpenSees

- User instruction: continue. The analytical plan and parameter file were committed first as 8d1d35c. No student-signed prediction or handwritten work is claimed.
- Both readers have identical asked-field answers. A provisional common-geometry mechanics baseline proceeds without claiming final Task 2 promotion or a model winner.
- Signed rectangles keep O1/O2 void and S1 separate. One-storey equivalent mass is 164.666794 t; five-storey sum is 823.333970 t. CM=(4.963771,8.326083) m. The assigned service G+Q intensity is an exercise mass convention, not a code seismic mass.
- Corrected dimensional inconsistency in the brief's stiffness-based CR expression by deriving weighted-position and flexibility formulas. Full force torque uses signed directional eccentricity, not automatically e*F.
- The matched rectangular-wall baseline retains strong/weak lateral bending and shear, excludes intrinsic vertical wall torsion and columns, and treats walls as cantilevers. Strong-direction-only and bending-only sensitivity cases are retained separately.
- Shear-inclusive CR=(5.563280,9.694116) m, e=1.493628 m. Independent polygon mass integrals, scalar stiffness sums, coordinate shift, unit-load no-rotation and wall-force equilibrium checks pass 54/54. No OpenSees agreement is claimed until the next actual run.
- Task 4's detailed model briefing is frozen before solver execution. No VLM confidence tiebreaker or hidden geometry correction is used.

## Tasks 4 and 5 - Actual matching solver run

- Analytical results and the detailed model briefing were committed as 3fd490a before the OpenSees run. Official ElasticTimoshenkoBeam and rigidDiaphragm documentation was checked for 3D argument order, local axes and Transformation constraints.
- OpenSees 3.8.0 ran 12 one-element Timoshenko cantilever walls, with an explicit rigid diaphragm at CM. Strong and weak rectangular-wall stiffnesses and both shear areas match the analytical assumptions; intrinsic vertical wall torsion is zero. No artificial stiff slab, penalty diaphragm, hidden fixed wall-top bending restraint or additional lateral columns were introduced.
- Three rebuilt unit-load analyses gave CR=(5.563280,9.694116) m. Relative hand/model flexibility error is 1.6015e-16; reported maximum CR difference is zero at stored floating-point precision.
- Unit x/y forces through the model-derived CR gave rotations approximately 1.80e-24 and 7.19e-25 rad. Direct 100 kN global-y loading at CM agrees with the superposed push-through-CR and signed torque runs for all master displacements and wall forces.
- Real isolated strong/weak cantilever tests and a rebuilt bending-only elasticBeamColumn model verify orientation, shear and limiting behaviour. Saved base reactions and top displacements pass force/moment equilibrium and rigid-plane kinematic checks. Tasks 4/5 verification passes 75/75.
- The 100 kN force is explicitly an assumed linear-analysis demonstration, not a supplied seismic design demand. No claim is made that numerical agreement validates the inherited image reading or completes formal Task 2 experiment control.
- Conditional structural consequences of the accepted five flag answers were added to the reader comparison. Both readers and the flag-conditioned reference produce the same mechanical geometry and CR; each conditional shift is zero. This is not a surveyed full-plan accuracy claim.
- All new calculations, raw model responses, verification records, figures and reports are in English. Existing homework steps and reader answers remain preserved.
