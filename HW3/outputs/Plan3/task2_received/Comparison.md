# Task 2 - Provisional comparison of received answers

Provisional scoring of received records; Task 2 evidence not yet complete

| Reader | Resolved | Broken | Mean confidence | Printed-size error (mm) |
|---|---:|---:|---:|---:|
| GPT-6 contextual Task 1 reader | 5/5 | 0 | 0.984 | 0 |
| Grok 4.5 (student-confirmed) | 5/5 | 0 | 0.980 | 0 |

Tie on the five asked-field answers; no accuracy winner is established. Self-reported confidence is not a tiebreaker.

The student confirmed Grok 4.5 and supplied a screenshot on 2026-11-10. The screenshot corroborates P3-F05 and the chatbot's self-description; the UI selector shows Fast rather than an exact backend version. The full five-question website transcript remains unavailable. The five pasted JSON objects are preserved as received, without correcting them. The two original execution environments differ. Reader A had prior draft/answer-related engineering context. These limitations prevent presenting the table as a fully controlled experiment. See [screenshot evidence description](../../../records/Grok_Screenshot_Evidence.md).

All queried fields are identical, so these five corrections alone introduce no geometry difference between the readers. No winner or promotion has been manufactured.

## Per-flag Grok outcomes

| Flag | Resolved | Broken | Size error (mm) |
|---|---|---|---:|
| P3-F01 | True | False | N/A |
| P3-F02 | True | False | 0 |
| P3-F03 | True | False | 0 |
| P3-F04 | True | False | N/A |
| P3-F05 | True | False | 0 |

Raw records: [Grok answers](../reader_B_grok/Raw_Answers.json), [Grok metadata](../reader_B_grok/Run_Metadata.json), [Reader A answers](../reader_A_task1/Raw_Answers.json).

## Conditional structural consequences

Conditional on the shared unqueried classical geometry and accepted answers; not error relative to an independently surveyed full plan.

Each record applies the accepted queried fields to a copy of the same classical geometry. Weighted wall-stiffness CR is computed separately for each copy using the Task 3 rectangular, shear-inclusive wall convention. Thus this calculation measures the consequence of the flagged fields, not full-plan extraction truth.

| Record | CR x (m) | CR y (m) | Shift from conditional reference (m) |
|---|---:|---:|---:|
| flag_conditioned_reference | 5.563280 | 9.694116 | 0.000000 |
| GPT-6 contextual | 5.563280 | 9.694116 | 0.000000 |
| Grok 4.5 student-reported | 5.563280 | 9.694116 | 0.000000 |
