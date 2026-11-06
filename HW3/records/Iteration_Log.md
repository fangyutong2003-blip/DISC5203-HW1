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
