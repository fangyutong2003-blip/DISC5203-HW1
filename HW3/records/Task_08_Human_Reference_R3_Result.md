# Task 8 - Human reference receipt and R3 outcome

Date: 2026-11-11. The student personally read the unmarked source crop and replied **T3 3500X400**. The [raw receipt](../outputs/NewPlan/human_reference_request/Student_Reading_2026-11-11.json) preserves the exact reply; only the multiplication separator is normalized for comparison. No human confidence or pre-solve prediction is invented.

Receipt/protocol were committed as `235cba2`; the resulting [NewPlan R3 reference](../outputs/NewPlan/independent_reference_r3/Reference.json) was frozen as `c1787e4` before scoring. R3 supplements only NP-F03. All other R2 flags, original V4/R2 references and scores, actual reader replies and images remain unchanged.

With NewPlan R3 and unchanged NIST R2, both isolated gpt-6.1-sol and student-reported Grok 4.5 resolve **10/10 queried flags**, with zero incorrect and zero unscorable flags. This is agreement with the supplemented reference, not ten-of-ten full-plan accuracy or a blind pre-response benchmark. The human review and NIST R2 audit occurred after model replies. Interfaces differ, and Grok backend identity remains student-reported.

The [separate R3 comparison](../outputs/Task08/reader_comparison_r3/Comparison.md) retains the tie and local no-regression results. No model is declared more accurate and no complete geometry is promoted. The original failure to produce accepted geometry/scale is not repaired merely by matching ten answers.

The next engineering stage is full image-derived geometry recovery: coordinate origins, two-axis calibration, all support IDs/positions, printed-size association, explicit NIST missing-size assumptions and closed tributary-region area conservation. Preserve the unchanged-pipeline failure and record any supplementary recovery as a new revision. CM/CR and OpenSees require an adopted geometry that passes those separate gates.
