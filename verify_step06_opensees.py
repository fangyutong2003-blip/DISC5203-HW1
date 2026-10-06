"""Independent verification checks for the HW2 Step 06 OpenSees models."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import openseespy.opensees as ops


ROOT = Path(__file__).resolve().parent
RESULTS = [
    ROOT / "Step_06_BeamA_Pure_Result.json",
    ROOT / "Step_06_BeamA_Subframe_Result.json",
    ROOT / "Step_06_BeamB_Pure_Result.json",
    ROOT / "Step_06_BeamB_Subframe_Result.json",
]
OUTPUT = ROOT / "Step_06_OpenSees_Verification.csv"


def uniform_reference(fixed: bool) -> tuple[float, float]:
    length = 4.0
    load = 10.0
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.node(1, 0.0, 0.0)
    ops.node(2, length / 2.0, 0.0)
    ops.node(3, length, 0.0)
    if fixed:
        ops.fix(1, 1, 1, 1)
        ops.fix(3, 1, 1, 1)
    else:
        ops.fix(1, 1, 1, 0)
        ops.fix(3, 0, 1, 0)
    ops.geomTransf("Linear", 1)
    for tag, i, j in ((1, 1, 2), (2, 2, 3)):
        ops.element("elasticBeamColumn", tag, i, j, 0.15, 30.0e6, 0.002, 1)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.eleLoad("-ele", 1, 2, "-type", "-beamUniform", -load)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    if ops.analyze(1) != 0:
        raise RuntimeError("OpenSees reference model failed")
    first = [float(value) for value in ops.eleResponse(1, "localForce")]
    support_internal_moment = -first[2]
    midspan_internal_moment = first[5]
    ops.wipe()
    return support_internal_moment, midspan_internal_moment


def add_check(rows: list[dict], check_id: str, description: str, expected, actual, tolerance) -> None:
    if isinstance(expected, str):
        passed = expected == actual
    else:
        passed = math.isclose(float(expected), float(actual), rel_tol=0.0, abs_tol=float(tolerance))
    rows.append({
        "check_id": check_id,
        "description": description,
        "expected": expected,
        "actual": actual,
        "tolerance": tolerance,
        "status": "PASS" if passed else "FAIL",
    })


def main() -> None:
    rows: list[dict] = []
    add_check(rows, "O01", "OpenSees major version", "3", ops.version().split(".")[0], "exact")
    simple_support, simple_mid = uniform_reference(False)
    add_check(rows, "O02", "Simple beam support moment, 4 m at 10 kN/m (kN m)", 0.0, simple_support, 1.0e-6)
    add_check(rows, "O03", "Simple beam midspan moment qL2/8 (kN m)", 20.0, simple_mid, 1.0e-6)
    fixed_support, fixed_mid = uniform_reference(True)
    add_check(rows, "O04", "Fixed beam support moment -qL2/12 (kN m)", -13.3333333333, fixed_support, 1.0e-6)
    add_check(rows, "O05", "Fixed beam midspan moment qL2/24 (kN m)", 6.6666666667, fixed_mid, 1.0e-6)

    next_id = 6
    for path in RESULTS:
        result = json.loads(path.read_text(encoding="utf-8"))
        label = f"{result['beam']} {result['model']}"
        add_check(rows, f"O{next_id:02d}", f"{label} vertical equilibrium (kN)", 0.0, result["equilibrium_error_kN"], 1.0e-6)
        next_id += 1
        add_check(rows, f"O{next_id:02d}", f"{label} element end-moment reconstruction (kN m)", 0.0, result["max_element_end_moment_error_kNm"], 1.0e-9)
        next_id += 1
        add_check(rows, f"O{next_id:02d}", f"{label} pre-solve order gate", "PASS", result["hand_bound_order_check"], "exact")
        next_id += 1

    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    failures = [row for row in rows if row["status"] != "PASS"]
    if failures:
        raise SystemExit(f"Step 06 verification failed: {len(failures)} checks")
    print(f"Step 06 verification passed: {len(rows)}/{len(rows)} checks")


if __name__ == "__main__":
    main()
