# Task 8 - Reference R2 and isolated-reader protocol

Date: 2026-11-11. This is an agent-authored method declaration, not a student-signed prediction. It is frozen in Git before executing Reference R2 or scoring the newly collected answers.

## Chronology and independence

The student has already supplied six NewPlan JSON replies and four NIST follow-up JSON replies from a service identified by the student as Grok 4.5. Record that model name as student-reported; the exact backend snapshot is unverified and a screenshot cannot confirm it. Do not request the same version proof again.

The V4 reference and reader inputs remain unchanged. Reference R2 is a separately retained, **post-response** method revision. The engineering agent has seen Grok replies; no claim of pre-response blindness is permissible. R2 must read only frozen source images and query metadata, never any reader-response file. Its rules below are fixed before execution and may return unresolved. Report both the original V4-reference score and the R2 sensitivity comparison. A post-response repaired reference cannot erase the original protocol failure or automatically certify geometry.

## Reference R2 rules

1. Use original unmarked source crops, threshold 180 and the existing local RapidOCR engine. For printed labels, run the same crop at 0, 90, 180 and 270 degrees, without rescaling. Strip whitespace and normalize the multiplication sign. Match the exact queried printed label followed by two 3- or 4-digit dimensions; reject nonpositive dimensions. Require OCR confidence at least 0.85 and one unique size across admissible readings. Keep every raw detection, transformation and confidence. Multiple distinct sizes remain unresolved; do not choose the one agreeing with Grok.
2. For continuity, use the frozen queried axis box on the original unmarked source. Replace the invalid fixed 8 px trim with the predeclared geometric rule `min(8, floor(min(width,height)/4))`. Evaluate raw-ink axial occupancy at each threshold 160, 180 and 200 using the existing axial occupancy fraction >0.15. Require at least 95% supported axis stations at all three thresholds. Preserve support vectors and the longest unsupported run. A low-support result remains unresolved rather than inferring a concrete gap. This is a measurement of visible symbol continuity, not proof of wall thickness, endpoints or structural topology.
3. Record exact source/crop/old-reference/code hashes, creation time and the pre-execution Git commit. Freeze R2 files before the comparison code is run. No VLM reply, historic accepted geometry or student signoff supplies an R2 answer.

## Isolated first-reader sessions

The student explicitly authorised an independent reader agent without inherited chat history. Start one fresh session per plan, matching the requested Grok handoff's separate chats. Use the same V4 common instructions, images, question text and order, one flag per turn. Do not provide this document, evaluator metadata, reference answers, geometry, Grok replies or engineering-session history to those sessions. Disable history forking; instruct them not to consult workspace files or memories. Retain actual tool IDs, input payloads, raw responses, ordering and available model identity. Unknown model snapshots remain unknown.

The isolated Codex harness and user-operated Grok web interface are different interfaces; do not call them an identical harness. Grok's six NewPlan replies are original pasted JSON; NIST confidence/reasons were supplied in later follow-ups and must remain identified as such. Preserve both initial and follow-up evidence. The new reader may use native image understanding only, not reference-generating OCR.

## Scoring and gate

Use confidence >=0.8 and equality of asked fields on resolved reference flags. An unresolved reference cannot produce a pass or a failure count. Report resolved, incorrect, low-confidence/abstained and unscorable flags separately for each model and reference revision. A tie is a tie, not evidence of superiority. No geometry may be promoted solely on ten local flag answers: require full geometry/scale/size/area checks, unchanged previously cleared flags and explicit acknowledgement of experimental limitations.

## Environment repair

The HW3 virtual environment's previous base runtime path no longer existed. Its original pyvenv.cfg was copied to pyvenv.cfg.before_runtime_20261111 inside the ignored environment. Only the base `home` and `executable` paths were retargeted to the current cached Python 3.12.14, matching the previous Python version. No package upgrade was performed. Import smoke checks succeeded for OpenCV 5.0.0, NumPy 2.5.4, SciPy 1.18.1, scikit-learn 1.9.1 and OpenSees 3.8.0. Future numerical checks still must be run; successful imports alone are not model verification.
