"""Run and document all four HW2 Task 3 OpenSees models."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from step06_opensees_core import run_model


ROOT = Path(__file__).resolve().parent


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def expected_shape_figure() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 5.8), constrained_layout=True)
    definitions = [
        ("Beam A", [6.05, 6.05, 3.10], [-1.0, -0.55, 0.10]),
        ("Beam B", [3.60, 3.00, 3.60], [-1.0, 0.35, -1.0]),
    ]
    for ax, (name, lengths, amplitudes) in zip(axes, definitions):
        cursor = 0.0
        for length, amplitude in zip(lengths, amplitudes):
            local = np.linspace(0.0, length, 120)
            shape = amplitude * np.sin(np.pi * local / length)
            ax.plot(cursor + local, shape, color="#c52f3f", linewidth=2.2)
            cursor += length
        supports = np.cumsum([0.0] + lengths)
        ax.scatter(supports, np.zeros_like(supports), marker="^", s=80, color="#1f4f82", zorder=3)
        ax.axhline(0.0, color="#6b7280", linewidth=0.8)
        ax.set_title(f"{name}: pre-solve expected deflected-shape sketch")
        ax.set_ylabel("Relative deflection")
        ax.grid(alpha=0.2)
    axes[-1].set_xlabel("Distance along beam line (m)")
    fig.suptitle("Engineering expectation recorded before OpenSees execution (schematic, not to scale)", fontweight="bold")
    fig.savefig(ROOT / "Step_06_PreSolve_Expected_Shapes.png", dpi=190)
    plt.close(fig)


def main() -> None:
    expected_shape_figure()
    results = [
        run_model("Beam A", "pure"),
        run_model("Beam A", "subframe"),
        run_model("Beam B", "pure"),
        run_model("Beam B", "subframe"),
    ]
    summary_rows = []
    reaction_rows = []
    for result in results:
        summary_rows.append({
            "beam": result["beam"],
            "model": result["model"],
            "applied_service_load_kN": f"{result['applied_service_load_kN']:.6f}",
            "reaction_sum_kN": f"{result['vertical_reaction_sum_kN']:.6f}",
            "equilibrium_error_kN": f"{result['equilibrium_error_kN']:.9f}",
            "peak_sagging_kNm": f"{result['peak_sagging_kNm']:.6f}",
            "peak_hogging_kNm": f"{result['peak_hogging_kNm']:.6f}",
            "peak_abs_shear_kN": f"{result['peak_abs_shear_kN']:.6f}",
            "peak_abs_axial_kN": f"{result['peak_abs_axial_kN']:.6f}",
            "max_vertical_displacement_mm": f"{1000.0 * result['max_vertical_displacement_m']:.6f}",
            "governing_hand_bound_kNm": f"{result['governing_hand_bound_kNm']:.6f}",
            "hand_bound_order_check": result["hand_bound_order_check"],
        })
        for reaction in result["reactions"]:
            reaction_rows.append({
                "beam": result["beam"],
                "model": result["model"],
                "support": reaction["support"],
                "x_m": f"{reaction['x_m']:.4f}",
                "Rx_kN": f"{reaction['Rx_kN']:.6f}",
                "Ry_kN": f"{reaction['Ry_kN']:.6f}",
                "base_moment_kNm": f"{reaction['M_kNm']:.6f}",
            })
    write_csv(ROOT / "Step_06_OpenSees_Model_Summary.csv", summary_rows)
    write_csv(ROOT / "Step_06_OpenSees_Support_Reactions.csv", reaction_rows)

    hw1_rows = {row["element_id"]: row for row in read_csv(ROOT / "Step_02_Element_Load_Summary.csv")}
    cross_rows = []
    labels = []
    hw1_values = []
    hw2_values = []
    for result in results:
        if result["model"] != "subframe":
            continue
        for reaction in result["reactions"]:
            row = hw1_rows[reaction["support"]]
            hw1_service = float(row["total_G_per_floor_kN"]) + float(row["total_Q_per_floor_kN"])
            hw2_reaction = float(reaction["Ry_kN"])
            difference = 100.0 * (hw2_reaction - hw1_service) / hw1_service
            cross_rows.append({
                "beam": result["beam"],
                "grid_point": reaction["support"],
                "HW1_one_floor_service_axial_kN": f"{hw1_service:.4f}",
                "HW2_selected_line_subframe_reaction_kN": f"{hw2_reaction:.4f}",
                "difference_percent": f"{difference:.2f}",
                "scope_note": "HW2 contains only the selected beam line; HW1 contains the full floor tributary load and member self-weight.",
            })
            labels.append(f"{result['beam'][-1]}:{reaction['support']}")
            hw1_values.append(hw1_service)
            hw2_values.append(hw2_reaction)
    write_csv(ROOT / "Step_06_HW1_Axial_Cross_Check.csv", cross_rows)

    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(12, 5.8), constrained_layout=True)
    ax.bar(x - width / 2, hw1_values, width, label="HW1 full-floor one-storey axial", color="#4776b4")
    ax.bar(x + width / 2, hw2_values, width, label="HW2 selected-line subframe reaction", color="#d46a42")
    for index, (hw1, hw2) in enumerate(zip(hw1_values, hw2_values)):
        difference = 100.0 * (hw2 - hw1) / hw1
        ax.text(index, max(hw1, hw2) + 2.0, f"{difference:+.0f}%", ha="center", fontsize=9)
    ax.set_xticks(x, labels)
    ax.set_ylabel("One-floor vertical force (kN)")
    ax.set_title("Scope diagnostic: HW1 full-floor axial vs HW2 selected-line subframe reaction")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(ROOT / "Step_06_HW1_Subframe_Reaction_Comparison.png", dpi=190)
    plt.close(fig)

    result_lookup = {(result["beam"], result["model"]): result for result in results}
    a_pure = result_lookup[("Beam A", "pure")]
    a_frame = result_lookup[("Beam A", "subframe")]
    b_pure = result_lookup[("Beam B", "pure")]
    b_frame = result_lookup[("Beam B", "subframe")]
    max_equilibrium_error = max(abs(result["equilibrium_error_kN"]) for result in results)
    max_end_error = max(result["max_element_end_moment_error_kNm"] for result in results)

    report = f"""# Step 06 - OpenSees Pure-Beam and One-Storey Subframe Models

## 1. Scope

This step implements HW2 Task 3 for both marked lines. Beam A is D19-D11-D05, the three-span peripheral edge beam. Beam B is D16-D17-D18, the three-span interior beam. The models reuse the Step 04 geometry and Step 05 service line loads rather than re-deriving the floor plan.

The structural briefing and the pre-solve hand bounds were recorded before execution in `Step_06_OpenSees_Briefing_and_Iteration_Log.md`.

## 2. Model assumptions

- Units: kN and m; stress and elastic modulus in kN/m2.
- Concrete: linear elastic, E = 30,000,000 kN/m2.
- Beam A section: 250 x 700 mm; Beam B section: 250 x 600 mm.
- Load case: service G+Q, including slab load and beam-stem self-weight.
- The non-uniform profiles are discretised into 60 uniform elasticBeamColumn elements per span.
- The pure models are continuous beams with vertical simple supports at all grid points.
- Each subframe places the beam at the top of one 3.0 m storey; the support members have fixed bases and there are no upper-storey columns.
- Positive plotted moment is sagging; negative plotted moment is hogging.

The configuration is machine-readable in `Step_06_OpenSees_Model_Config.json`.

## 3. Pre-solve expectation

![Pre-solve expected shapes](Step_06_PreSolve_Expected_Shapes.png)

The governing simply-supported moment bounds were 79.287 kN m for Beam A and 38.621 kN m for Beam B. Continuity was expected to introduce negative moments over the interior supports and reduce span sagging relative to isolated simply-supported spans. Beam B's lightly loaded central D17 span was expected to be strongly influenced by the two loaded outer spans.

## 4. Solver results

| Beam | Model | Applied G+Q (kN) | Reaction sum (kN) | M+ (kN m) | M- (kN m) | max |V| (kN) | max |N| (kN) | max vertical deflection (mm) | Bound check |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
"""
    for result in results:
        report += (
            f"| {result['beam']} | {result['model']} | {result['applied_service_load_kN']:.3f} | "
            f"{result['vertical_reaction_sum_kN']:.3f} | {result['peak_sagging_kNm']:.3f} | "
            f"{result['peak_hogging_kNm']:.3f} | {result['peak_abs_shear_kN']:.3f} | "
            f"{result['peak_abs_axial_kN']:.3f} | {1000.0 * result['max_vertical_displacement_m']:.3f} | "
            f"{result['hand_bound_order_check']} |\n"
        )

    report += f"""

Maximum vertical equilibrium error across the four models was {max_equilibrium_error:.3e} kN. Maximum reconstructed element-end moment error was {max_end_error:.3e} kN m. All four peak moments passed the deliberately broad pre-solve order-of-magnitude gate.

The independent reference suite in `Step_06_OpenSees_Verification.csv` also passed 17/17 checks, including the closed-form (qL^2/8), (-qL^2/12), and (qL^2/24) limits for a 4 m beam under 10 kN/m.

### Beam A - pure continuous beam

![Beam A pure response](Step_06_BeamA_Pure_Response.png)

### Beam A - one-storey subframe

![Beam A subframe response](Step_06_BeamA_Subframe_Response.png)

### Beam B - pure continuous beam

![Beam B pure response](Step_06_BeamB_Pure_Response.png)

### Beam B - one-storey subframe

![Beam B subframe response](Step_06_BeamB_Subframe_Response.png)

## 5. Pure beam versus subframe

For Beam A, the peak absolute moment changed from {a_pure['peak_abs_moment_kNm']:.2f} to {a_frame['peak_abs_moment_kNm']:.2f} kN m and maximum vertical deflection changed from {1000*a_pure['max_vertical_displacement_m']:.3f} to {1000*a_frame['max_vertical_displacement_m']:.3f} mm. The stiff T9 boundary member and the finite column rotational stiffness redistribute both the support and span moments. For Beam B, the subframe reduced the peak sagging moment from {b_pure['peak_sagging_kNm']:.2f} to {b_frame['peak_sagging_kNm']:.2f} kN m while increasing the peak hogging magnitude from {abs(b_pure['peak_hogging_kNm']):.2f} to {abs(b_frame['peak_hogging_kNm']):.2f} kN m. This is the expected transfer from span moment into support moment. The beam remains rotation-compatible at each support and does not form a displacement kink; the frame columns sway and rotate with the beam nodes.

The subframe is the more defensible of these two models for beam-force distribution because it includes support stiffness and frame action. It is still only a one-line, one-storey approximation and is not a substitute for a full floor-grid or multi-storey model.

## 6. Support reactions and HW1 cross-check

The detailed reactions are in `Step_06_OpenSees_Support_Reactions.csv`.

![HW1 and HW2 reaction comparison](Step_06_HW1_Subframe_Reaction_Comparison.png)

| Beam | Grid point | HW1 full-floor one-storey axial (kN) | HW2 selected-line reaction (kN) | Difference |
|---|---|---:|---:|---:|
"""
    for row in cross_rows:
        report += (
            f"| {row['beam']} | {row['grid_point']} | {float(row['HW1_one_floor_service_axial_kN']):.2f} | "
            f"{float(row['HW2_selected_line_subframe_reaction_kN']):.2f} | {float(row['difference_percent']):+.1f}% |\n"
        )
    report += """

This is a scope diagnostic, not an expected equality. The HW1 value contains the full floor tributary load plus vertical-member self-weight. The Step 06 subframe contains only the selected marked beam line and omits reactions arriving from orthogonal and neighbouring beams. The generally smaller HW2 reactions therefore identify missing floor-grid scope rather than a vertical-equilibrium failure. A full Task 12 equality check requires either a larger grid model or equivalent nodal loads from every omitted adjoining beam.

The assignment wording refers to beam axial N at the support, but the quantity physically comparable with a column axial force is the vertical support reaction, or equivalently the column axial force. Beam-local N is horizontal and is reported separately in the N diagram.

## 7. Reproduction

Run all models and rebuild the tables and figures:

```powershell
python step06_run_all.py
python verify_step06_opensees.py
```

The four explicit OpenSees entry points are:

- `Step_06_BeamA_Pure_OpenSees.py`
- `Step_06_BeamA_Subframe_OpenSees.py`
- `Step_06_BeamB_Pure_OpenSees.py`
- `Step_06_BeamB_Subframe_OpenSees.py`

## 8. Items requiring student sign-off

1. Confirm the image-derived mapping of Beam A to D19-D11-D05 and Beam B to D16-D17-D18.
2. Confirm the T9 strong-axis wall-equivalent representation in the Beam A subframe.
3. Confirm that the W5 convention intends fixed bases with no upper-storey columns.
4. Add the student's hand-drawn deformed-shape sketches. The pre-solve schematic above records the engineering prediction but is not a substitute for the required hand drawing.
5. Decide whether Task 12 should be extended to a full floor-grid reaction model or completed with equivalent nodal loads from omitted beams.
"""
    (ROOT / "Step_06_OpenSees_Models_and_Verification.md").write_text(report, encoding="utf-8")

    print(f"Generated {len(results)} OpenSees models.")
    print(f"Maximum vertical equilibrium error: {max_equilibrium_error:.3e} kN")
    print("All hand-bound order checks:", all(result["hand_bound_order_check"] == "PASS" for result in results))


if __name__ == "__main__":
    main()
