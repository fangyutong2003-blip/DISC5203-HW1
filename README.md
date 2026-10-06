# DISC 5203 HW1 - AI-Assisted Structural Analysis

This repository contains the final Homework 1 submission for Floor Plan 3, together with the complete intermediate audit trail.

**Student:** Fangyutong  
**Student ID:** 21353319  
**Email:** yfangbu@connect.ust.hk

## Start here

Open [HW1_Final_Report.md](HW1_Final_Report.md) for the complete continuous submission report.

The checkpoint and detailed engineering records are retained as separate files:

1. [Week 4 checkpoint report](HW1_Checkpoint_Report.md)
2. [Step 01 - Geometry and tributary areas](Step_01_Geometry_and_Tributary_Areas.md)
3. [Step 02 - Vertical loads and axial forces](Step_02_Vertical_Load_and_Axial_Force_Calculation.md)
4. [Step 03 - Independent verification](Step_03_Verification_and_Checkpoint.md)

## Repository structure

| File group | Purpose |
|---|---|
| `HW1_Final_Report.md` | Complete continuous final report |
| `FloorPlan3*.png` | Source plan and reviewed geometry diagrams |
| `Step_01*.md/csv` | Geometry, element locations, and tributary areas |
| `Step_02*.md/csv/png` | Load calculations, schedules, and comparison chart |
| `Step_03*.md/csv` | Independent verification and checkpoint evidence |
| `Step_04*.md/csv/png` | HW2 beam census and tributary-area records |
| `Step_05*.md/csv/png` | HW2 beam line-load records and worked example |
| `*.py` | Reproducible geometry, load, and verification scripts |
| `load_combinations.json` | Provisional reporting factors and confirmation status |
| `requirements.txt` | Python package requirements |
| `AGENTS.md` | Project guidance for the AI agent |
| `skills.md` | Reusable procedures used in this workflow |

## Reproduce the calculations

Use Python 3.10 or newer. From a fresh clone, create an environment and install the two required packages:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead.

Run the HW1 scripts from the repository root in this order:

```powershell
python tributary_regions.py
python step02_loads.py
python verify_results.py
```

The first command now uses the validated rectilinear L1 method by default, deducts O1/O2 and S1, and generates both `Step_01B_Vertical_Element_Coordinates.csv` and `Step_01C_Tributary_Areas.csv`. The deprecated `--straight` flag remains accepted for compatibility. The non-submission Euclidean diagnostic is available only through `python tributary_regions.py --euclidean-diagnostic` and does not overwrite the validated Step 01 CSV files.

`verify_results.py` exits with an error if any Step 03 check fails. To reproduce the completed HW2 Tasks 1 and 2 after HW1 verification, run:

```powershell
python hw2_beam_loads.py
```

All plotting scripts use a cross-platform font fallback. `load_combinations.json` records the current 1.35G+1.50Q and G+0.30Q factors as provisional because the required course design standard has not yet been confirmed.

## Final result

- Vertical elements: 21
- Ordinary flat-slab area: 179.250 m2
- Five-storey base service load: 11107.844 kN
- Five-storey base ULS load: 15687.895 kN
- Independent verification: 23/23 checks passed

All detailed assumptions, limitations, calculations, and verification evidence are stated in the final report and retained step records.
