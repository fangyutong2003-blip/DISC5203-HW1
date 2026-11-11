# Task 8 - Isolated readers and workflow review R2

Student: Fangyutong, 21353319. Date: 2026-11-11.

**Outcome:** actual isolated Codex readings and user-pasted Grok replies are retained for all ten questions. Both readers agree on all asked fields. Nine questions have a resolved source-based reference under R2; both readers resolve those nine with no incorrect answers. NewPlan NP-F03 remains unscorable. There is no accuracy winner and no full-plan extraction promotion. Task 8 remains incomplete.

## Student instructions and prospective controls

The student requested continued work with a complete workflow and explicitly authorised an independent image-reading agent without inherited chat history. The actual engineering brief and student instruction are separate; no numerical prediction is attributed to the student.

Before executing the reference revision or scoring, commit `820a363` froze [the R2/isolation protocol](records/Task_08_Reference_R2_Protocol.md) and [the Grok identity declaration](records/Task_08_Grok_Model_Declaration.md). Commit `c585457` retained the calculated R2 references before running the comparison. Earlier V1-V4 inputs, failed masks, degenerate forest, user-pasted original/follow-up replies and original V4 references were preserved.

## Actual reader runs

| Property | Isolated Codex reader | Grok reader |
|---|---|---|
| Identity | `gpt-6.1-sol`, from runtime turn_context metadata | Grok 4.5, student-reported; exact backend unverified |
| Collection | Two fresh native-image sessions, one per plan; no inherited chat history | Student-operated web sessions; replies pasted by student |
| Inputs | Frozen V4 common instructions, exact images/questions/order, one image per turn | Same V4 handoff requested; full website transcript unavailable |
| Additional control | Explicit no-tools/no-workspace/no-memories instruction | Web interface and system prompt not controlled here |
| Answers | Six NewPlan plus four NIST actual completed-agent responses | Six original NewPlan JSON replies; four NIST abbreviated originals plus later complete JSON follow-ups |
| Reference exposure | No reference files, geometry or Grok answers supplied; runtime logs show no reader tool calls | No evidence of reference-file transfer; cannot independently certify full session context |

The model initially self-reported that its version was not exposed. That exact preface remains in the raw response. A separate extraction of runtime model metadata establishes the routing identifier `gpt-6.1-sol`; this is not a claim to certify the backend weights snapshot. Only model/turn/effort metadata and tool-call names were extracted from runtime logs; private reasoning was not copied into the coursework.

The Codex and Grok interfaces differ. Common inputs are identical; the harness is **not** identical. This is not a randomized, fully blinded cross-service benchmark. Unknown Grok backend identity remains disclosed; no further unsupported version claim or screenshot is fabricated.

- NewPlan: [raw actual input/output transcript](outputs/NewPlan/reader_codex_isolated_v4/Raw_Tool_Transcript.json), [parsed answers](outputs/NewPlan/reader_codex_isolated_v4/Parsed_Answers.json), [runtime model evidence](outputs/NewPlan/reader_codex_isolated_v4/Model_Runtime_Evidence.json), [run metadata](outputs/NewPlan/reader_codex_isolated_v4/Run_Metadata.json).
- NIST: [raw actual input/output transcript](outputs/NIST/reader_codex_isolated_v4/Raw_Tool_Transcript.json), [parsed answers](outputs/NIST/reader_codex_isolated_v4/Parsed_Answers.json), [runtime model evidence](outputs/NIST/reader_codex_isolated_v4/Model_Runtime_Evidence.json), [run metadata](outputs/NIST/reader_codex_isolated_v4/Run_Metadata.json).
- Grok: [complete receipt chronology](records/Task_08_Grok_Complete_Receipt_2026-11-11.md), [NewPlan original pasted JSONL](outputs/NewPlan/reader_grok_received_v4/Raw_User_Messages.jsonl) and [NIST follow-up receipt](records/Task_08_NIST_Followup_Receipt_2026-11-11.json). Earlier partial receipts remain historical evidence.

## Reference chronology and results

V4 was frozen before the student supplied answers. Its fixed reference route resolved five NewPlan questions and no NIST questions. Those limitations remain in the original files. R2 is explicitly a **post-response** source-only revision: the engineering agent had already seen Grok replies. Its method was committed before running it, and its program never reads response files. It is reported as a sensitivity audit, not a retroactively blind pre-response reference.

For labels, R2 applies threshold 180 OCR at four fixed rotations with confidence >=0.85 and unique exact-label/size agreement. For continuity, it uses a predetermined quarter-thickness trim and raw axial occupancy at thresholds 160/180/200. All four NIST wall symbols show robust visible continuity. That result does not supply wall thickness, dimensions or complete topology.

NewPlan NP-F03 remains unresolved: the OCR reads the size text but fails to establish the full printed T3 identifier reliably. Neither Grok's reply nor Codex's matching reply is substituted for an independent source reference. [An unmarked crop and direct human-reading request](outputs/NewPlan/human_reference_request/Request.json) are retained; the student's own source reading is pending. No human review is backdated or invented.

| Plan | Reference | Codex resolved / incorrect / unscorable | Grok resolved / incorrect / unscorable |
|---|---|---|---|
| NewPlan | Original V4, pre-response | 5 / 0 / 1 | 5 / 0 / 1 |
| NIST | Original V4, pre-response | 0 / 0 / 4 | 0 / 0 / 4 |
| NewPlan | R2, post-response | 5 / 0 / 1 | 5 / 0 / 1 |
| NIST | R2, post-response | 4 / 0 / 0 | 4 / 0 / 0 |

No low-confidence or abstained answer occurred in these actual records. Self-reported 0.99 versus 0.95 confidence is not an accuracy tiebreaker. Do not report ten-of-ten verified accuracy or full-plan extraction accuracy from this table.

References: [NewPlan R2](outputs/NewPlan/independent_reference_r2/Reference.json), [NIST R2](outputs/NIST/independent_reference_r2/Reference.json). Their manifests preserve source, code, protocol and original-reference hashes. [The comparison JSON](outputs/Task08/reader_comparison/Comparison.json) retains both revision scores, per-flag classifications, raw-response hashes and local no-regression results; [the table](outputs/Task08/reader_comparison/Comparison.md) is generated from the same actual data.

## Gate, verification and next engineering work

Both readers preserve the other's cleared flags on the scorable subset. Neither resolves more than the other, so no superior model is selected. The full geometry gate still fails: the unchanged NewPlan pipeline has zero accepted bar claims and null scale; the NIST pipeline has no detected structural components or labelled-size claims. Local continuity/size answers cannot create the missing complete element set.

[Workflow validation](records/Task_08_Workflow_Validation.json) passes **81/81** checks of actual image/question ordering, source hashes, raw-to-parsed equality, runtime model evidence, no-tool isolation, source/reference integrity and promotion state. Adversarial checks confirm that a wrong high-confidence answer, loss of a previously cleared flag, low confidence and duplicated IDs do not pass the gate. These are evidence and gate checks, not structural validation.

The real installed pre-commit hook has been extended to validate JSONL as well as JSON, Python syntax and English text. JSONL is pinned to LF for portable hashes. The [actual staged-fixture hook exercise](records/Task_08_Actual_Hook_Exercise.json) retains both the rejection of a damaged JSONL fixture and acceptance after repair. Earlier hook exercises remain preserved.

The local environment was repaired by retargeting the stale venv base path to the current cached Python of the same version. The old configuration remains backed up inside the ignored environment; no package upgrade is claimed. The numerical model still requires its relevant checks when it is eventually run on new geometry.

Next: obtain the direct T3 source reading; independently establish complete geometry, both-axis calibration, printed-size association, NIST missing-size assumptions and closed-area conservation. Preserve the unchanged-pipeline failure and label any recovery as a revision rather than a successful unchanged extraction. Only an adopted geometry that passes those checks may feed tributary/gravity calculations, hand CM/K/CR and the matched OpenSees model. No new-plan CM/CR result is asserted by this workflow report.

## Reproduce the comparison

The exact native model runs are retained measurements; scripts do not fabricate them. With the retained files:

```powershell
python HW3/scripts/task08_reference_r2.py
python HW3/scripts/task08_compare_readers.py
python HW3/scripts/verify_task08_workflow.py
```

The reference script verifies existing frozen R2 files instead of replacing them. `task08_export_isolated_evidence.py` is an evidence-ingestion utility requiring the actual local runtime logs; the resulting minimal evidence excerpts are committed, so scoring does not require access to unrelated machine logs. Future responses or human references must be added as a new receipt/revision, preserving these raw measurements.
