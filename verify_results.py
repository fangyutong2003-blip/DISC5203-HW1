"""Independent verification for HW1 Steps 01 and 02.

The script reads the delivered CSV files, recomputes the principal quantities,
and writes an auditable check table plus a Markdown checkpoint report.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent

AREA_FILE = ROOT / "Step_01C_Tributary_Areas.csv"
COORD_FILE = ROOT / "Step_01B_Vertical_Element_Coordinates.csv"
SUMMARY_FILE = ROOT / "Step_02_Element_Load_Summary.csv"
LEVEL_FILE = ROOT / "Step_02_Axial_Loads_by_Level.csv"
RESULT_FILE = ROOT / "Step_03_Verification_Results.csv"
REPORT_FILE = ROOT / "Step_03_Verification_and_Checkpoint.md"
COMBINATION_FILE = ROOT / "load_combinations.json"

STOREYS = 5
STOREY_HEIGHT_M = 3.0
SLAB_THICKNESS_M = 0.150
CONCRETE_DENSITY_KN_M3 = 25.0
LIVE_LOAD_KN_M2 = 5.0
DEAD_LOAD_KN_M2 = SLAB_THICKNESS_M * CONCRETE_DENSITY_KN_M3
GROSS_AREA_M2 = 186.615
VOID_AREA_M2 = 2.000
S1_AREA_M2 = 5.365
FLAT_SLAB_AREA_M2 = GROSS_AREA_M2 - VOID_AREA_M2 - S1_AREA_M2
S1_BORDER_LENGTHS_M = {"T6": 2.10, "T7": 3.40, "T8": 2.10}
COMBINATIONS = json.loads(COMBINATION_FILE.read_text(encoding="utf-8"))
GAMMA_G = float(COMBINATIONS["uls"]["gamma_G"])
GAMMA_Q = float(COMBINATIONS["uls"]["gamma_Q"])
G_PLUS_Q_FACTOR = float(COMBINATIONS["g_plus_0_30q"]["q_factor"])


@dataclass
class Check:
    check_id: str
    description: str
    expected: str
    actual: str
    tolerance: str
    status: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_section_area_m2(section: str) -> float:
    width_mm, depth_mm = (float(value) for value in section.lower().split("x"))
    return width_mm * depth_mm / 1_000_000.0


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def close_check(
    checks: list[Check],
    check_id: str,
    description: str,
    expected: float,
    actual: float,
    tolerance: float = 0.001,
) -> None:
    passed = math.isclose(expected, actual, rel_tol=0.0, abs_tol=tolerance)
    checks.append(
        Check(
            check_id,
            description,
            fmt(expected, 6),
            fmt(actual, 6),
            fmt(tolerance, 6),
            "PASS" if passed else "FAIL",
        )
    )


def exact_check(
    checks: list[Check], check_id: str, description: str, expected: object, actual: object
) -> None:
    checks.append(
        Check(
            check_id,
            description,
            str(expected),
            str(actual),
            "exact",
            "PASS" if expected == actual else "FAIL",
        )
    )


def git_history() -> list[str]:
    try:
        output = subprocess.check_output(
            [
                "git",
                "-c",
                f"safe.directory={ROOT.as_posix()}",
                "log",
                "-6",
                "--pretty=format:%h %s",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        history = []
        for line in output.splitlines():
            if not line.strip():
                continue
            commit_hash, _, subject = line.partition(" ")
            if subject and not subject.isascii():
                subject = "[non-English commit subject omitted from report]"
            history.append(f"{commit_hash} {subject}".rstrip())
        return history
    except (OSError, subprocess.CalledProcessError):
        return ["Git history was unavailable when this report was generated."]


def main() -> None:
    area_rows = read_csv(AREA_FILE)
    coordinate_rows = read_csv(COORD_FILE)
    summary_rows = read_csv(SUMMARY_FILE)
    level_rows = read_csv(LEVEL_FILE)

    areas = {row["element_id"]: float(row["tributary_area_m2"]) for row in area_rows}
    summaries = {row["element_id"]: row for row in summary_rows}
    main_sections = {
        row["element_id"]: row["section_mm"]
        for row in coordinate_rows
        if row["axis_segment"] in {"centre", "main"}
    }
    checks: list[Check] = []

    area_ids = set(areas)
    summary_ids = set(summaries)
    coordinate_ids = set(main_sections)
    level_ids = {row["element_id"] for row in level_rows}

    exact_check(checks, "V01", "Number of vertical elements", 21, len(area_rows))
    exact_check(checks, "V02", "Number of by-level result rows", 21 * STOREYS, len(level_rows))
    exact_check(
        checks,
        "V03",
        "Element IDs agree across area, coordinate, summary, and level files",
        True,
        area_ids == summary_ids == coordinate_ids == level_ids,
    )

    area_sum = sum(areas.values())
    close_check(checks, "V04", "Tributary areas close to ordinary flat-slab area (m2)", FLAT_SLAB_AREA_M2, area_sum, 0.001)
    close_check(
        checks,
        "V05",
        "Gross floor area closes after adding O1/O2 and S1 (m2)",
        GROSS_AREA_M2,
        area_sum + VOID_AREA_M2 + S1_AREA_M2,
        0.001,
    )

    ordinary_dead = area_sum * DEAD_LOAD_KN_M2
    ordinary_live = area_sum * LIVE_LOAD_KN_M2
    s1_dead = S1_AREA_M2 * DEAD_LOAD_KN_M2
    s1_live = S1_AREA_M2 * LIVE_LOAD_KN_M2
    close_check(checks, "V06", "Ordinary slab dead load per floor (kN)", 672.1875, ordinary_dead)
    close_check(checks, "V07", "Ordinary slab live load per floor (kN)", 896.2500, ordinary_live)
    close_check(checks, "V08", "S1 equivalent dead load per floor (kN)", 20.11875, s1_dead)
    close_check(checks, "V09", "S1 equivalent live load per floor (kN)", 26.82500, s1_live)

    self_weights: dict[str, float] = {}
    for element_id, section in main_sections.items():
        self_weights[element_id] = (
            parse_section_area_m2(section) * STOREY_HEIGHT_M * CONCRETE_DENSITY_KN_M3
        )
    member_self_weight = sum(self_weights.values())
    close_check(checks, "V10", "Vertical-member self-weight per floor (kN)", 606.1875, member_self_weight)

    s1_total_border = sum(S1_BORDER_LENGTHS_M.values())
    expected: dict[str, dict[str, float]] = {}
    for element_id, area in areas.items():
        share = S1_BORDER_LENGTHS_M.get(element_id, 0.0) / s1_total_border
        g_floor = area * DEAD_LOAD_KN_M2 + self_weights[element_id] + share * s1_dead
        q_floor = area * LIVE_LOAD_KN_M2 + share * s1_live
        base_g = STOREYS * g_floor
        base_q = STOREYS * q_floor
        expected[element_id] = {
            "area": area,
            "self": self_weights[element_id],
            "share": share,
            "g_floor": g_floor,
            "q_floor": q_floor,
            "base_g": base_g,
            "base_q": base_q,
            "service": base_g + base_q,
            "uls": GAMMA_G * base_g + GAMMA_Q * base_q,
            "g_plus_0_3q": base_g + G_PLUS_Q_FACTOR * base_q,
        }

    total_g_floor = sum(item["g_floor"] for item in expected.values())
    total_q_floor = sum(item["q_floor"] for item in expected.values())
    close_check(checks, "V11", "Total permanent load per floor (kN)", 1298.49375, total_g_floor)
    close_check(checks, "V12", "Total variable load per floor (kN)", 923.07500, total_q_floor)
    close_check(checks, "V13", "Base permanent load for five storeys (kN)", 6492.46875, STOREYS * total_g_floor)
    close_check(checks, "V14", "Base variable load for five storeys (kN)", 4615.37500, STOREYS * total_q_floor)
    close_check(checks, "V15", "Base service load G+Q (kN)", 11107.84375, STOREYS * (total_g_floor + total_q_floor))
    close_check(
        checks,
        "V16",
        "Base ULS load 1.35G+1.50Q (kN)",
        15687.89531,
        GAMMA_G * STOREYS * total_g_floor + GAMMA_Q * STOREYS * total_q_floor,
        0.002,
    )
    close_check(
        checks,
        "V17",
        "Base provisional G+0.30Q reporting combination (kN)",
        7877.08125,
        STOREYS * total_g_floor + G_PLUS_Q_FACTOR * STOREYS * total_q_floor,
        0.002,
    )

    summary_fields = {
        "tributary_area_m2": "area",
        "element_self_weight_per_floor_kN": "self",
        "total_G_per_floor_kN": "g_floor",
        "total_Q_per_floor_kN": "q_floor",
        "base_G_5_storeys_kN": "base_g",
        "base_Q_5_storeys_kN": "base_q",
        "base_G_plus_Q_kN": "service",
        "base_ULS_1_35G_1_5Q_kN": "uls",
        "base_G_plus_0_3Q_kN": "g_plus_0_3q",
    }
    max_summary_delta = 0.0
    for element_id, row in summaries.items():
        for csv_field, expected_field in summary_fields.items():
            max_summary_delta = max(
                max_summary_delta,
                abs(float(row[csv_field]) - expected[element_id][expected_field]),
            )
    close_check(checks, "V18", "Maximum absolute difference in Step 02 summary (kN or m2)", 0.0, max_summary_delta, 0.00011)

    max_level_delta = 0.0
    accumulation_ok = True
    for row in level_rows:
        element_id = row["element_id"]
        multiplier = int(row["floors_supported"])
        accumulation_ok = accumulation_ok and 1 <= multiplier <= STOREYS
        expected_level = {
            "G_kN": multiplier * expected[element_id]["g_floor"],
            "Q_kN": multiplier * expected[element_id]["q_floor"],
            "G_plus_Q_kN": multiplier * (expected[element_id]["g_floor"] + expected[element_id]["q_floor"]),
            "ULS_1_35G_1_5Q_kN": multiplier
            * (GAMMA_G * expected[element_id]["g_floor"] + GAMMA_Q * expected[element_id]["q_floor"]),
            "G_plus_0_3Q_kN": multiplier
            * (expected[element_id]["g_floor"] + G_PLUS_Q_FACTOR * expected[element_id]["q_floor"]),
        }
        for field, value in expected_level.items():
            max_level_delta = max(max_level_delta, abs(float(row[field]) - value))
    counts_by_element = {
        element_id: sorted(
            int(row["floors_supported"])
            for row in level_rows
            if row["element_id"] == element_id
        )
        for element_id in level_ids
    }
    accumulation_ok = accumulation_ok and all(
        values == [1, 2, 3, 4, 5] for values in counts_by_element.values()
    )
    exact_check(checks, "V19", "Every element contains the 1:2:3:4:5 storey accumulation sequence", True, accumulation_ok)
    close_check(checks, "V20", "Maximum absolute difference in by-level results (kN)", 0.0, max_level_delta, 0.00011)

    nonnegative = all(
        expected[element_id][field] >= 0.0
        for element_id in expected
        for field in ("area", "self", "g_floor", "q_floor", "base_g", "base_q", "service", "uls", "g_plus_0_3q")
    )
    exact_check(checks, "V21", "All recomputed areas and loads are nonnegative", True, nonnegative)

    for element_id, check_id in (("C1", "V22"), ("T7", "V23")):
        close_check(
            checks,
            check_id,
            f"Representative {element_id} base ULS agrees with Step 02 (kN)",
            expected[element_id]["uls"],
            float(summaries[element_id]["base_ULS_1_35G_1_5Q_kN"]),
            0.00011,
        )

    with RESULT_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["check_id", "description", "expected", "actual", "tolerance", "status"])
        for check in checks:
            writer.writerow(
                [check.check_id, check.description, check.expected, check.actual, check.tolerance, check.status]
            )

    pass_count = sum(check.status == "PASS" for check in checks)
    fail_count = len(checks) - pass_count
    c1 = expected["C1"]
    t7 = expected["T7"]
    history = git_history()
    report = f"""# Step 03 - Verification and Checkpoint

## Purpose

This checkpoint independently recalculates the Step 01 geometry totals and the Step 02 vertical-load results from the delivered CSV inputs. It does not overwrite or replace any earlier step.

## Verification status

- Checks passed: **{pass_count}/{len(checks)}**
- Checks failed: **{fail_count}**
- Overall status: **{'PASS' if fail_count == 0 else 'FAIL'}**

| ID | Independent check | Expected | Actual | Tolerance | Status |
|---|---|---:|---:|---:|:---:|
"""
    for check in checks:
        report += (
            f"| {check.check_id} | {check.description} | {check.expected} | "
            f"{check.actual} | {check.tolerance} | **{check.status}** |\n"
        )

    report += f"""

## Independent calculation basis

| Item | Value |
|---|---:|
| Number of storeys | {STOREYS} |
| Storey height | {STOREY_HEIGHT_M:.2f} m |
| Concrete density | {CONCRETE_DENSITY_KN_M3:.2f} kN/m3 |
| Slab thickness | {SLAB_THICKNESS_M:.3f} m |
| Slab dead load | {DEAD_LOAD_KN_M2:.3f} kN/m2 |
| Live load | {LIVE_LOAD_KN_M2:.3f} kN/m2 |
| Gross floor area | {GROSS_AREA_M2:.3f} m2 |
| O1/O2 void area | {VOID_AREA_M2:.3f} m2 |
| S1 plan area | {S1_AREA_M2:.3f} m2 |
| Ordinary flat-slab area | {FLAT_SLAB_AREA_M2:.3f} m2 |

The ordinary slab area is distributed to C1-C9 and T1-T12 by the Step 01 tributary-area file. S1 is added separately and distributed to T6, T7, and T8 in proportion to bordering lengths 2.10:3.40:2.10. Column and wall self-weights use the main labelled section dimensions, a 3.0 m storey height, and 25 kN/m3 concrete density.

The 1.35G+1.50Q and G+0.30Q factors are read from `load_combinations.json`. They reproduce the original submission but remain provisional pending confirmation of the course design standard. G+0.30Q is labelled only by its equation and is not classified as seismic mass or quasi-permanent load.

## Representative manual checks

### C1

- Tributary slab dead load = {c1['area']:.4f} x {DEAD_LOAD_KN_M2:.3f} = {c1['area'] * DEAD_LOAD_KN_M2:.4f} kN/floor.
- Column self-weight = 0.400 x 0.400 x 3.0 x 25 = {c1['self']:.4f} kN/floor.
- G = {c1['g_floor']:.4f} kN/floor and Q = {c1['q_floor']:.4f} kN/floor.
- Base provisional ULS = {GAMMA_G:.2f} x ({STOREYS} x {c1['g_floor']:.4f}) + {GAMMA_Q:.2f} x ({STOREYS} x {c1['q_floor']:.4f}) = {c1['uls']:.4f} kN.

### T7

- S1 allocation ratio = 3.40 / (2.10 + 3.40 + 2.10) = {t7['share']:.6f}.
- Tributary slab dead load = {t7['area']:.4f} x {DEAD_LOAD_KN_M2:.3f} = {t7['area'] * DEAD_LOAD_KN_M2:.4f} kN/floor.
- Wall self-weight = 0.250 x 3.400 x 3.0 x 25 = {t7['self']:.4f} kN/floor.
- Allocated S1 dead/live loads = {t7['share'] * s1_dead:.4f}/{t7['share'] * s1_live:.4f} kN/floor.
- G = {t7['g_floor']:.4f} kN/floor and Q = {t7['q_floor']:.4f} kN/floor.
- Base ULS = {t7['uls']:.4f} kN.

## Numerical sensitivity and interpretation

The Step 01 partition uses a 0.01 m calculation grid. The recorded 0.02 m rerun changed any single tributary area by no more than approximately 0.073 m2, about 0.041% of the 179.250 m2 ordinary flat-slab area. This is a numerical discretisation check, not a substitute for engineering review of support axes and corner-boundary assumptions.

## Checkpoint evidence

- Step 01 geometry, coordinate, and tributary-area records remain in the repository.
- Step 02 load assumptions, element summaries, by-level axial-load results, and the base ULS chart remain in the repository.
- `verify_results.py` reproduces this report and `Step_03_Verification_Results.csv`.
- The verification uses independent equations and does not copy Step 02 totals into the expected values.

Recent Git history when this checkpoint was generated:

"""
    report += "\n".join(f"- `{line}`" for line in history)
    report += """

## Remaining limitations before final submission

- All plan coordinates and tributary regions are image-derived and should be checked against any original CAD or dimension schedule if available.
- The S1 treatment is a provisional equivalent horizontal-area model. A stair-specific load path should replace it if the coursework requires flight and landing analysis.
- Short wall returns are excluded from member self-weight to avoid overlap and uncertain image dimensions.
- Finishes, partitions, facade, beam self-weight, and live-load reduction are not included because no project values have been provided.
- The load-combination factors require confirmation against the standard or lecture reference specified by the instructor.
- Support-fixity assumptions still require confirmation before lateral-load or frame analysis.

## Reproduction

Run:

```powershell
python verify_results.py
```

The command regenerates the Step 03 CSV and Markdown files without changing Step 01 or Step 02 records.
"""
    REPORT_FILE.write_text(report, encoding="utf-8")

    if fail_count:
        raise SystemExit(f"Verification failed: {fail_count} of {len(checks)} checks failed.")
    print(f"Verification passed: {pass_count}/{len(checks)} checks.")
    print(f"Wrote {RESULT_FILE.name}")
    print(f"Wrote {REPORT_FILE.name}")


if __name__ == "__main__":
    main()
