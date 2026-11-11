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

## Tasks 6 and 7 - Frozen-mass wall modification and interpretation

- User instruction: continue. The agent-authored design briefing and bounded parameter file were committed as e8514a7 before optimisation. No student signoff or pre-solve numerical thickness prediction is fabricated.
- Choice: increase only T9/T10 thickness, holding T9's exterior left face and T10's exterior bottom face fixed. All columns, wall main lengths/directions, voids, stair zone and prescribed floor mass remain fixed. Both strong/weak stiffnesses and shear flexibility are recomputed.
- The actual bounded least-squares trajectory converged to T9=0.4635649155 m and T10=0.6181479218 m. Their centres shift inward by 0.1067824578 m in x and 0.1840739609 m in y respectively. The ideal hand/model CR equals CM=(4.96377055,8.32608266) m to stored precision; solver eccentricity is 3.55e-15 m.
- A separate 5 mm-rounded proposal uses 0.465/0.620 m thicknesses and leaves 0.007113481 m eccentricity. It is not falsely represented as exact alignment. Both proposals pass floor, void/stair, column and new wall-overlap checks.
- Added concrete is 3.490277 m3 per storey and added dead weight is 87.256926 kN. The equivalent 8.894692 t is 5.40% of the prescribed floor mass; it is explicitly quantified but not included in the exercise's fixed mass. Practical mass/gravity/foundation/reinforcement/clearance reassessment remains necessary outside this numerical proposal.
- Actual rebuilt OpenSees Timoshenko rigid-diaphragm models and three unit loads were run before, after ideal alignment and after rounding. Both assumed 100 kN force directions are retained. Original x-load amplification is 1.305200 at T10/T11; y-load amplification is 1.060605 at T9. Peak x wall demand at T4 changes 27.454585 to 25.228452 kN; peak y demand at T7 changes 45.992592 to 40.243008 kN. These changes include stiffness redistribution; thickened walls attract additional load, so not all demands decrease.
- Corrected the brief's radius-only amplification denominator by dimensional derivation: squared torsional radius and wall stiffness are required. Force-specific signed eccentricity is used, not automatically norm(e)*F.
- Actual analytical and OpenSees eigenanalyses share the unchanged diagonal mass matrix. The engine emitted its generic fullGenLapack speed warning, but all three finite modes were obtained and independently checked. The torsion-dominant mode is mode 3 before/after, not mode 1. Its rotational mass fraction changes approximately 0.667 to 1, demonstrating decoupling rather than disappearance of torsional dynamics.
- Independent modification, geometry, force, amplification, eigenvalue/eigenvector and zero-rotation checks pass 133/133. English reports, figures, parameters, trajectory and raw solver responses are retained. Formal Task 2 experiment controls and Task 8 additional plans remain pending.

## Task 8 - Third-plan source selection, 2026-11-10

- Student requested a public third plan of manageable, comparable complexity. Selected NIST TN 2351 Figure 2 after comparing the Seo 2015 and Velarde 2025 research figures; retained source, unannotated renders, hash manifest and a reproducible rendering command.
- The selected office-building archetype has clear overall/bay dimensions and walls in both directions, but lacks individual printed IDs and full section sizes. Solid symbols, imperial units and missing labels are recorded as generalisation challenges. The source-text versus schematic column-count discrepancy remains flagged.
- Uniform-mass symmetry is a conditional zero-eccentricity check, not an already run result or a reduction claim. No thresholds were retuned, dimensions invented, reader responses generated or extraction promoted. Both additional-plan pipelines remain pending.

## Task 8 - Frozen classical portability checkpoint, 2026-11-10

- Pre-run briefing/source/code/history freeze committed as 2358ad8. Generalised source/output routing in the original four scripts without changing image rules, OCR parsing, matching or forest settings. Added null-scale and single-class probability handling instead of inventing geometry or crashing.
- NewPlan: 216 components, 61/116 raw OCR detections, two main-parser size hypotheses, 225 preliminary candidates, zero bar claims and no scale seed. NIST: zero components, 6/6 OCR detections, no size hypotheses/candidates/claims and no scale seed. Actual forests retained and never selected; NIST trained only on background and has zero importance/probability.
- Preserved invalid v1/v2 question-package drafts: v1 ID splitting was wrong; v2's shared schedule did not fit its crop. V3 uses an explicit framing gate and retains the excluded schedule as unresolved. Main extraction was not repaired. Six NewPlan questions have five alternative-reference answers; four NIST continuity references fail the unchanged 8 px trim. No actual VLM runs or winner are claimed.
- Validation initially passed 154/155, exposing an overlay-render difference. Kept that attempt; six processing PNGs and component records are exact, while 2614 differing overlay pixels fall inside ID text neighborhoods. Final validation passes 156/156 artifact checks and retains the exact-overlay mismatch as an observation. Historic Plan 3 hashes are unchanged; Task 1 still passes 71/71.
- English report, comparison figure, actual model files, frozen crop/reference hashes and answer-free V3 reader ZIPs retained. Additional-plan CM/CR, promotion and the full Task 8 comparison remain pending.

### Pre-push serialization correction

- The v3 local validation was insufficient: Git attributes normalise text to LF, while Windows-generated reference JSON and ZIP text contained CRLF. A direct HEAD-blob/reference-hash comparison failed before upload. Kept the v3 commit and files as superseded evidence.
- V4 explicitly serializes all new frozen JSON/questions as UTF-8/LF before hashing and ZIP creation. Images/questions and reference meanings are unchanged; no reader answers are added. The current packages are V4 only.
- The verifier now compares actual staged reference hashes and every distributed text/image file with its reader ZIP. All 174/174 checks pass (156 local plus 18 Git-index checks); this does not resolve outstanding reference or structural-model limitations.

## Task 8 - Isolated readers and reference R2, 2026-11-11

- Student supplied all six NewPlan and four complete NIST follow-up replies, declared Grok 4.5 with unverified backend identity, and explicitly authorised isolated reader delegation. Original abbreviated NIST replies and partial receipt chronology remain preserved.
- Committed the post-response source-only R2 protocol and isolated-reader controls as 820a363 before execution; retained R2 outputs as c585457 before scoring. R2 cannot be relabelled as pre-response blind truth. NewPlan resolves 5/6 references; NIST resolves 4/4 under fixed geometric trim and threshold sensitivities. NP-F03 remains unresolved; a direct student source-reading request is pending.
- Ran two fresh no-history native-image Codex sessions, one per additional plan, one flag per turn. Only V4 inputs and a recorded no-tools control were supplied. All ten actual answers and full delivered payloads are retained. Runtime turn metadata establishes gpt-6.1-sol; neither session used a tool. The raw unknown-version self-report is preserved rather than rewritten.
- Original V4 and post-response R2 scores are separately tabulated. Both readers agree on all asked fields, resolve the nine R2-scorable flags and break none. NP-F03 is unscorable, not a manufactured tenth success. No accuracy winner or full-plan promotion is claimed; geometry/scale and mechanics remain pending.
- Extended the installed hook to JSONL and pinned JSONL to LF. Workflow validation passes 81/81 including actual session/input/identity evidence and adversarial wrong-answer/low-confidence/duplicate-ID/no-regression checks. AGENTS.md and skills.md now cover these controls and limitations.

## Task 8 - Student source reading and human supplement R3

- Student replied T3 3500X400 after the unmarked source-crop request. Preserved the exact reply and its non-blind post-response timing, with no invented confidence or student prediction.
- Committed receipt/protocol as 235cba2 and froze R3 as c1787e4 before scoring. Only NP-F03's reference expectation/resolved state is supplemented; all earlier V4/R2 records, other reference flags and raw reader replies remain unchanged.
- Separately scored unchanged model answers against NewPlan R3 and NIST R2: both agree with all ten supplemented reference flags, zero incorrect, tie. This does not establish blind full-plan accuracy or pass geometry promotion. Full geometry/calibration and structural analysis remain pending.

## Task 8 - Conditional engineering recovery and actual solver comparison

- Froze the supplementary recovery brief/parameters as 445eef6. This is a disclosed post-audit solid-symbol method, not a rebranding of failed unchanged hatching rules. Measured NewPlan: 26 standalone square bodies, four L groups/eight bars, eight/four grid axes. Retained C25/C28 junction interpretation and C17/C20 label-only assumptions. NIST: 21 visible squares/four bars/five axes per direction; source text's 25 columns remains unresolved.
- Retained source overlays, original pixels, global/local scale diagnostics, unique label claims and conditional coordinates as 0d7c45b. A failed 2 m label-centre guard rejected long T2 text; the original attempt is preserved and its correction documented without retuning masks/sizes. NewPlan's 0.054545 m2 combined T4/T8 face protrusion past the assumed slab edge remains a warning, not clipped geometry.
- Retained 0.05 m closed areas and hand calculations as f368008, then independently refined to 0.025 m. All declared floor domains close with no overlaps/gaps. Maximum per-support change versus 0.05 m is 0.935% NewPlan and 1.090% NIST; the marginal NIST target exception is explicit. Known-column joint footprints trim gravity axes; original untrimmed allocations remain a sensitivity.
- Known vertical gravity uses footprint unions to avoid overlap double counting. NIST unknown column self-weights stay null. Both known G/Q schedules have consistent IDs and 1:2:3:4:5 accumulation. Uniform prescribed floor mass stays separate from vertical-member gravity, matching Plan 3's convention.
- Independent geometry/area/load/hand validation passes 364/364. Froze refined hand models/gates as d66f7a1 before actual OpenSees 3.8.0 rigidDiaphragm/Transformation runs. Actual matrix/CR, equilibrium, kinematics, zero rotation, push/turn, bending/section limits and eigen checks pass 140/140. The generic fullGenLapack speed warning is retained as a warning, not a failed analysis.
- NewPlan conditional CM=(23,9) m, CR=(23.003250,9.733916) m, e=0.733924 m. NIST CM=(18.288,18.288) m, CR=(18.289483,18.287516) m, e=0.001560 m, below schematic precision. These are single-floor diagnostic models, not full-building periods or surveyed-source certification.
- Source sensitivities retain grid-axis versus outer-face slab mass, C17/C20 omission, global versus piecewise calibration and NIST symmetric/independent endpoint cases. NIST's independent +/-2 px endpoint extreme box reaches e=1.523 m; it is not a statistical interval or a claim that the source building has that eccentricity.
- Generated coordinate/section-provenance CSVs, closed GeoJSON/figures, known loads, matrices, raw solver/force/mode files and an English three-plan comparison. Conditional numerical work is complete; strict unchanged-pipeline generalisation, full-source topology and model-identity/reference/harness limits are not erased.
