# Task 8 - Actual two-reader comparison

Actual additional-plan reader comparison; no full-plan geometry promotion

| Plan | Reference | Reader | Resolved | Incorrect | Abstained/low confidence | Unscorable reference |
|---|---|---|---:|---:|---:|---:|
| NewPlan | V4_original_pre_response | Codex_gpt_6_1_sol_isolated | 5 | 0 | 0 | 1 |
| NewPlan | V4_original_pre_response | Grok_4_5_student_reported | 5 | 0 | 0 | 1 |
| NewPlan | R2_post_response_sensitivity | Codex_gpt_6_1_sol_isolated | 5 | 0 | 0 | 1 |
| NewPlan | R2_post_response_sensitivity | Grok_4_5_student_reported | 5 | 0 | 0 | 1 |
| NIST | V4_original_pre_response | Codex_gpt_6_1_sol_isolated | 0 | 0 | 0 | 4 |
| NIST | V4_original_pre_response | Grok_4_5_student_reported | 0 | 0 | 0 | 4 |
| NIST | R2_post_response_sensitivity | Codex_gpt_6_1_sol_isolated | 4 | 0 | 0 | 0 |
| NIST | R2_post_response_sensitivity | Grok_4_5_student_reported | 4 | 0 | 0 | 0 |

No accuracy winner on scorable flags. Unresolved flags remain unscorable; no model promoted.

Same V4 crops/questions/order/common instructions; separate interfaces and additional Codex no-tools control. Not an identical harness or randomized blinded cross-service trial.

V4 reference frozen before user replies. R2 protocol frozen before computation/scoring but after Grok replies; report it as sensitivity, not a replacement pre-response truth.

The actual isolated-reader model is supported by retained runtime model metadata, not by its unknown self-report. Grok identity remains student-reported; no further screenshot proof is fabricated or required from the student.

NewPlan NP-F03 is not marked incorrect or correct against an unresolved reference, even when both models agree. A direct student source reading has been requested and is still pending.

Both local no-regression checks pass on the scorable subset. Full-plan promotion fails because no complete geometry and scale pass the geometry gate. Neither a tie nor high confidence creates a winner.

Additional-plan full geometry, tributary/gravity audit, CM/CR and matched OpenSees remain pending.
