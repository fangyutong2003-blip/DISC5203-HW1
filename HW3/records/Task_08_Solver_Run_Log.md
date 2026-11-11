# Task 8 actual solver execution record

Date: 2026-11-11. Command run after the hand/area validation and its Git checkpoint:

```text
.venv_hw3/Scripts/python.exe HW3/scripts/task08_opensees.py
```

Observed process exit code: 0. Captured combined console output:

```text
NewPlan actual OpenSees 3.8.0 CR [23.003249578423944, 9.73391633417397] e 0.7339235282556967
NIST actual OpenSees 3.8.0 CR [18.289482780892882, 18.287515830984745] e 0.0015598265325444222
WARNING - the 'fullGenLapack' eigen solver is VERY SLOW. Consider using the default eigen solver.
```

The warning concerns the small dense eigensolver's performance. Finite positive eigenvalues and saved responses independently passed all 140 solver checks. Raw numerical unit loads, reactions, displacements, force decompositions and modes are in the two engineering_r1_refined/OpenSees_Result.json files; the console text is not a substitute for those records.

These are conditional single-floor exercise models. The log does not certify source topology, missing column sections, full-building modes or the original unchanged extraction pipeline.
