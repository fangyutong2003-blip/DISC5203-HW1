# Project Guidance for AI Agents

## Scope

This repository supports DISC 5203 HW1, HW2 and HW3. HW3 extends the retained image-derived geometry to audited extraction, two VLM readers and rigid-diaphragm lateral analysis.

## Project rules

- Keep all reports, code comments, filenames, tables, and Git commit messages in English.
- Preserve previous step files and Git history. Add a new step or revision rather than deleting audit evidence.
- Treat plan coordinates as image-derived unless original CAD coordinates are supplied.
- State all assumptions, units, exclusions, and numerical tolerances explicitly.
- Do not present an open direction line as a completed tributary boundary. Regions must close and pass area conservation.
- Keep O1/O2 as voids and S1 separate from the ordinary flat slab unless new source evidence changes the interpretation.
- Do not add unspecified structural loads without identifying them as assumptions.
- Verify generated calculations independently before reporting completion.

## Calculation sequence

1. Read and review the source drawing.
2. Establish the coordinate system, slab outline, openings, and special zones.
3. Identify support points and finite wall-axis segments.
4. Generate closed tributary regions and verify area conservation.
5. Calculate per-floor dead and live loads.
6. Add vertical-element self-weight and accumulate loads by storey.
7. Check totals, combinations, IDs, and representative elements independently.
8. Save intermediate outputs and commit each meaningful stage to Git.

## Required checks

- Tributary regions collectively equal the adopted ordinary slab area.
- Every vertical element appears consistently in geometry, area, and load files.
- Floor accumulation follows 1:2:3:4:5 for the five-storey building.
- The sum of element loads equals independently calculated whole-floor loads.
- Figures and Markdown links resolve from the repository root.

## HW3 sequence and evidence

1. Preserve source images and hashes in HW3/sources; run threshold, morphology, connected components and shape rules before VLM review.
2. Read text twice, associate one printed label with one compatible bar, and record scale in both axes, provenance and unresolved flags.
3. Train and retain a random forest with feature importance; never promote its extraction.
4. Freeze an independent reference by a separately documented route before scoring readers. Historic HW1 geometry is a review aid, not automatically ground truth.
5. Give two genuinely different image-capable models identical crops, questions and ordering. Save raw responses and actual model identifiers. Never invent a model run or backdate human review.
6. Promote only after reference scoring and a no-regression gate; retain both raw extractions.
7. Calculate CM, shear-inclusive wall stiffness and the hand 3-by-3 matrix before the matching OpenSees run. Resolve dimensional inconsistencies in the assignment by derivation and document them.
8. Use explicit rigidDiaphragm and Transformation constraints; test unit loads, symmetry, equilibrium, load decomposition and zero rotation through CR.
9. Keep floor mass fixed while modifying walls; compare eccentricity, force shares and periods. Repeat unchanged procedures on the two additional plans.
10. Commit meaningful stages with English messages. Use .githooks/pre-commit and preserve readable Git history and actual validation logs.

Store student instructions separately from agent-authored briefing proposals. A proposal is not a signed student prediction. Incomplete tasks remain labelled pending; do not promote them merely to produce a final report.

## Reader experiment revisions and controls

- Preserve frozen V4 source/crop/question/reference bytes. A later source-only reference is a named revision; disclose whether model replies were already visible when it was designed. Never describe post-response R2 as a pre-response blind reference.
- Independently unresolved flags are unscorable, even if two models agree. Do not count them as resolved or broken against a fabricated answer. A tie and high self-reported confidence do not establish a winner.
- User-authorised isolated readers receive no inherited chat history, evaluator files, geometry or other-reader replies. Retain actual delivered inputs, raw outputs and available runtime model metadata. Record interface and isolation-control differences rather than claiming an identical harness.
- Retain initial abbreviated replies and requested follow-ups separately. Record Grok 4.5 as student-reported when its backend version is unverified; do not repeatedly demand a screenshot that cannot establish it.
- Validate LF-stable JSON/JSONL, actual Git object hashes and ZIP input bytes. Exercise the installed hook with a staged malformed fixture and preserve the actual rejection/repair log.
- Flag-level no-regression is necessary but insufficient: complete geometry, both-axis scale, dimensions, closed tributary regions and conservation must pass before full-plan promotion and downstream structural analysis.

