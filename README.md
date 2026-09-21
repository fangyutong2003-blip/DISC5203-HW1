# DISC 5203 HW1 - AI-Assisted Structural Analysis

This repository contains the Week 4 checkpoint work for Floor Plan 3.

**Student:** Fangyutong  
**Student ID:** 21353319  
**Email:** yfangbu@connect.ust.hk

## Start here

Open [HW1_Checkpoint_Report.md](HW1_Checkpoint_Report.md) for the checkpoint submission overview.

Detailed engineering records are retained as separate steps:

1. [Step 01 - Geometry and tributary areas](Step_01_Geometry_and_Tributary_Areas.md)
2. [Step 02 - Vertical loads and axial forces](Step_02_Vertical_Load_and_Axial_Force_Calculation.md)
3. [Step 03 - Independent verification](Step_03_Verification_and_Checkpoint.md)

## Repository structure

| File group | Purpose |
|---|---|
| `FloorPlan3*.png` | Source plan and reviewed geometry diagrams |
| `Step_01*.md/csv` | Geometry, element locations, and tributary areas |
| `Step_02*.md/csv/png` | Load calculations, schedules, and comparison chart |
| `Step_03*.md/csv` | Independent verification and checkpoint evidence |
| `*.py` | Reproducible geometry, load, and verification scripts |
| `AGENTS.md` | Project guidance for the AI agent |
| `skills.md` | Reusable procedures used in this workflow |

## Reproduce the calculations

Run the scripts from the repository root in this order:

```powershell
python tributary_regions.py
python step02_loads.py
python verify_results.py
```

`verify_results.py` exits with an error if any Step 03 check fails.

## Checkpoint result

- Vertical elements: 21
- Ordinary flat-slab area: 179.250 m2
- Five-storey base service load: 11107.844 kN
- Five-storey base ULS load: 15687.895 kN
- Independent verification: 23/23 checks passed

All detailed assumptions and limitations are stated in the step reports and checkpoint report.

