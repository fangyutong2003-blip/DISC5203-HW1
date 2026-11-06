# HW3 - Audited extraction and rigid-diaphragm analysis

Student: Fangyutong, 21353319. Assigned drawing: Floor Plan 3.

## Current stage

Task 1A has an initial classical run: 20 connected components, including merged walls and artifacts. Labels, scale and element-level scores remain pending. No reader has been promoted; no final CM/CR has been calculated. DP v4.1 is the student's proposed second reader; exact service model ID and image capability must be recorded from the actual session.

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
