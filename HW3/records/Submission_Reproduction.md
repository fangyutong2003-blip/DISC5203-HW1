# Reproduction and Git-free inspection

Prepared: 2026-11-12. Tested environment: Windows x64, Python 3.12.14; observed versions are in Submission_Runtime_Versions.json. Other operating systems and a fresh dependency installation have not been claimed as tested.

## Read without Git

Open HW3_Final_Report.md at the repository/package root. All figures, raw outputs, model code and intermediate records are included. The delivered package also supplies Git_Evidence/History_English.md and per-commit text patches, so process grading does not require a Git installation. Repository.bundle is an additional full-history copy, not the only process evidence.

## Environment

From the repository root, use Python 3.12 and install HW3/requirements.txt in an isolated environment. Direct dependencies include SciPy and joblib. On Windows, an example is:

```powershell
py -3.12 -m venv .venv_reproduce
.venv_reproduce/Scripts/python.exe -m pip install -r HW3/requirements.txt
.venv_reproduce/Scripts/python.exe HW3/scripts/restore_legacy_frozen_bytes.py --restore
.venv_reproduce/Scripts/python.exe HW3/scripts/submission_verify.py
```

On another platform use its Python 3.12 virtual-environment interpreter and available OpenSeesPy backend. The retained forest pickle is version-sensitive; compare the observed package versions before loading it. No API key is needed to inspect or validate the retained actual reader answers. Scripts do not fabricate a new VLM run.

## Preserve frozen evidence when replaying

The numerical validators independently inspect retained exported results. They are not a claim to rerun a model inference. To replay calculations, work in a separate copy so the original frozen evidence remains untouched:

```text
python HW3/scripts/task03_centres.py
python HW3/scripts/task04_opensees.py
python HW3/scripts/task06_modify.py
python HW3/scripts/task08_geometry_recovery.py
python HW3/scripts/task08_areas_and_hand.py
python HW3/scripts/task08_areas_and_hand.py --refined
python HW3/scripts/verify_task08_engineering.py
python HW3/scripts/task08_opensees.py
python HW3/scripts/verify_task08_opensees.py
python HW3/scripts/task08_source_sensitivity.py
```

The original image-stage commands and their failures remain in the retained task reports. Rebuilding classical/forest stages can change creation times/training times and thus artifact hashes; this must not be confused with a fresh blinded reference or an identical raw model run. Main-plan stage07 can read the three byte-exact historical snapshots in HW3/sources/legacy_snapshots/5f1eafe without Git; it parses the old Python literals rather than executing the old plotting code.

## Legacy byte hashes

37 legacy Plan3 text artifacts were frozen as CRLF before Git LF normalization. The bootstrap uses paired full-file hashes to reconstruct only that exact EOL change. It refuses real content changes and never changes a reference expectation. The later V4/R2/R3 records already use explicit LF. The working-byte submission snapshot preserves original bytes; Git clones should run the bootstrap before frozen-hash validators. See Legacy_Line_Ending_Portability.md.

## Validation scope

The final package check runs the retained-data validators in an extracted copy using the available tested interpreter, with Git calls unavailable to the check process. This is an extraction/portability and numerical-result audit, not a clean-machine dependency-install test or proof that all rubric conditions were met. Source interpretation, harness differences and known-only NIST gravity remain explicitly conditional.
