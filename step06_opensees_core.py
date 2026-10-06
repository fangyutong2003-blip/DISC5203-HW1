"""Shared OpenSeesPy model builder for HW2 Task 3.

The module builds either a continuous standalone beam or a one-storey frame
using the frozen service-load profiles from Step 05. Units are kN and m.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openseespy.opensees as ops


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "Step_06_OpenSees_Model_Config.json"
LOAD_PATH = ROOT / "Step_05_Beam_Line_Loads.csv"
E_CONCRETE = 30.0e6  # kN/m2


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _normalised_trapezoid_ratio(length: float, ramp: float) -> float:
    x = np.linspace(0.0, length, 20001)
    ordinate = np.minimum(np.minimum(x / ramp, (length - x) / ramp), 1.0)
    q_average = float(np.trapezoid(ordinate, x) / length)
    influence = 0.5 * np.minimum(x, length - x)
    midspan_moment = float(np.trapezoid(ordinate * influence, x))
    q_moment = 8.0 * midspan_moment / length**2
    return q_moment / q_average


def _profile_function(
    profile_type: str,
    length: float,
    q_average: float,
    q_moment: float,
) -> tuple[Callable[[float], float], dict[str, float | str]]:
    """Return the slab-load profile that matches total load and hand moment."""

    if q_average <= 0.0:
        return (lambda _x: 0.0), {"profile": "zero"}

    ratio = q_moment / q_average
    if profile_type == "symmetric_triangle":
        peak = 2.0 * q_average

        def triangle(x: float) -> float:
            return peak * (2.0 * x / length if x <= length / 2.0 else 2.0 * (length - x) / length)

        return triangle, {"profile": profile_type, "peak_slab_kN_m": peak, "target_ratio": ratio}

    if profile_type == "symmetric_trapezoid":
        low = max(length * 1.0e-6, 1.0e-8)
        high = length / 2.0
        target = min(max(ratio, 1.0), 4.0 / 3.0)
        for _ in range(60):
            mid = 0.5 * (low + high)
            if _normalised_trapezoid_ratio(length, mid) < target:
                low = mid
            else:
                high = mid
        ramp = 0.5 * (low + high)
        peak = q_average / (1.0 - ramp / length)

        def trapezoid(x: float) -> float:
            return peak * min(x / ramp, (length - x) / ramp, 1.0)

        return trapezoid, {
            "profile": profile_type,
            "ramp_m": ramp,
            "peak_slab_kN_m": peak,
            "target_ratio": ratio,
        }

    if profile_type == "centred_patch":
        loaded_fraction = min(max(2.0 - ratio, 0.05), 1.0)
        loaded_length = loaded_fraction * length
        intensity = q_average / loaded_fraction
        start = 0.5 * (length - loaded_length)
        end = start + loaded_length

        def patch(x: float) -> float:
            return intensity if start <= x <= end else 0.0

        return patch, {
            "profile": profile_type,
            "loaded_length_m": loaded_length,
            "peak_slab_kN_m": intensity,
            "target_ratio": ratio,
        }

    return (lambda _x: q_average), {
        "profile": "uniform",
        "peak_slab_kN_m": q_average,
        "target_ratio": ratio,
    }


def _model_data(beam_name: str) -> tuple[dict, list[dict], list[dict]]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    line = config["beam_lines"][beam_name]
    rows = {row["beam_id"]: row for row in _read_csv(LOAD_PATH)}
    span_rows = [rows[beam_id] for beam_id in line["segments"]]
    profiles = []
    for row, profile_type in zip(span_rows, line["profile_types"]):
        stem = float(row["beam_stem_dead_udl_kN_m"])
        q_average = float(row["service_udl_total_load_equiv_kN_m"]) - stem
        q_moment = float(row["service_udl_midspan_moment_equiv_kN_m"]) - stem
        profile, metadata = _profile_function(profile_type, float(row["span_m"]), q_average, q_moment)
        profiles.append({"function": profile, "metadata": metadata, "stem": stem})
    return config, span_rows, profiles


def run_model(beam_name: str, model_kind: str, save_outputs: bool = True) -> dict:
    if model_kind not in {"pure", "subframe"}:
        raise ValueError("model_kind must be 'pure' or 'subframe'")

    config, span_rows, profiles = _model_data(beam_name)
    line = config["beam_lines"][beam_name]
    divisions = int(config["analysis"]["elements_per_span"])
    beam_y = 0.0 if model_kind == "pure" else float(config["storey_height_m"])

    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.geomTransf("Linear", 1)

    next_node = 1
    next_element = 1
    beam_nodes: list[int] = []
    support_nodes: list[int] = []
    beam_elements: list[dict] = []
    all_edges: list[tuple[int, int, str]] = []
    support_x = [0.0]
    cursor = 0.0

    ops.node(next_node, cursor, beam_y)
    beam_nodes.append(next_node)
    support_nodes.append(next_node)
    next_node += 1

    for span_index, (row, profile_data) in enumerate(zip(span_rows, profiles)):
        length = float(row["span_m"])
        depth = float(row["depth_mm"]) / 1000.0
        width = 0.250
        area = width * depth
        inertia = width * depth**3 / 12.0
        dx = length / divisions
        start_node = beam_nodes[-1]
        raw_slab = [profile_data["function"]((j + 0.5) * dx) for j in range(divisions)]
        target_slab_load = (
            float(row["service_udl_total_load_equiv_kN_m"]) - profile_data["stem"]
        ) * length
        sampled_slab_load = sum(raw_slab) * dx
        scale = target_slab_load / sampled_slab_load if sampled_slab_load else 1.0
        for j in range(divisions):
            local_end = (j + 1) * dx
            node_tag = next_node
            next_node += 1
            ops.node(node_tag, cursor + local_end, beam_y)
            beam_nodes.append(node_tag)
            element_tag = next_element
            next_element += 1
            ops.element("elasticBeamColumn", element_tag, start_node, node_tag, area, E_CONCRETE, inertia, 1)
            total_down = profile_data["stem"] + raw_slab[j] * scale
            beam_elements.append({
                "tag": element_tag,
                "i": start_node,
                "j": node_tag,
                "x0": cursor + j * dx,
                "length": dx,
                "q_down": total_down,
                "span_id": row["beam_id"],
            })
            all_edges.append((start_node, node_tag, "beam"))
            start_node = node_tag
        cursor += length
        support_x.append(cursor)
        support_nodes.append(beam_nodes[-1])

    base_nodes: list[int] = []
    column_elements: list[int] = []
    if model_kind == "pure":
        for index, node in enumerate(support_nodes):
            ops.fix(node, 1 if index == 0 else 0, 1, 0)
        reaction_nodes = support_nodes
    else:
        for index, (top_node, x, section) in enumerate(zip(support_nodes, support_x, line["support_sections_m"])):
            base_tag = 10001 + index
            ops.node(base_tag, x, 0.0)
            ops.fix(base_tag, 1, 1, 1)
            base_nodes.append(base_tag)
            width, depth = (float(section[0]), float(section[1]))
            area = width * depth
            inertia = width * depth**3 / 12.0
            element_tag = 5001 + index
            ops.element("elasticBeamColumn", element_tag, base_tag, top_node, area, E_CONCRETE, inertia, 1)
            column_elements.append(element_tag)
            all_edges.append((base_tag, top_node, "column"))
        reaction_nodes = base_nodes

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for element in beam_elements:
        ops.eleLoad("-ele", element["tag"], "-type", "-beamUniform", -element["q_down"])

    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-12, 20)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    analysis_code = ops.analyze(1)
    if analysis_code != 0:
        raise RuntimeError(f"OpenSees analysis failed for {beam_name} {model_kind}: code {analysis_code}")
    ops.reactions()

    reactions = []
    for label, node, x in zip(line["support_labels"], reaction_nodes, support_x):
        rx, ry, rm = (float(value) for value in ops.nodeReaction(node))
        reactions.append({"support": label, "x_m": x, "Rx_kN": rx, "Ry_kN": ry, "M_kNm": rm})

    response_x: list[float] = []
    response_n: list[float] = []
    response_v: list[float] = []
    response_m: list[float] = []
    max_end_moment_error = 0.0
    for element in beam_elements:
        local_force = [float(value) for value in ops.eleResponse(element["tag"], "localForce")]
        pi, vi, mi, _pj, _vj, mj = local_force
        length = element["length"]
        wy = -element["q_down"]
        for local_x in np.linspace(0.0, length, 5):
            response_x.append(element["x0"] + float(local_x))
            response_n.append(-pi)
            response_v.append(vi + wy * float(local_x))
            response_m.append(-mi + vi * float(local_x) + 0.5 * wy * float(local_x) ** 2)
        calculated_end = -mi + vi * length + 0.5 * wy * length**2
        max_end_moment_error = max(max_end_moment_error, abs(calculated_end - mj))

    node_coordinates = {node: tuple(float(v) for v in ops.nodeCoord(node)) for node in set(beam_nodes + base_nodes)}
    node_displacements = {node: tuple(float(v) for v in ops.nodeDisp(node)) for node in node_coordinates}
    applied_load = sum(element["q_down"] * element["length"] for element in beam_elements)
    reaction_sum = sum(item["Ry_kN"] for item in reactions)
    max_vertical_displacement = max(abs(node_displacements[node][1]) for node in beam_nodes)

    simple_bounds = []
    for row in span_rows:
        simple_bounds.append(
            float(row["service_udl_midspan_moment_equiv_kN_m"]) * float(row["span_m"]) ** 2 / 8.0
        )
    hand_bound = max(simple_bounds)
    peak_abs_moment = max(abs(value) for value in response_m)
    bound_pass = 0.20 * hand_bound <= peak_abs_moment <= 1.50 * hand_bound

    slug = beam_name.replace(" ", "")
    label = "Pure" if model_kind == "pure" else "Subframe"
    figure_name = f"Step_06_{slug}_{label}_Response.png"
    result_name = f"Step_06_{slug}_{label}_Result.json"

    result = {
        "beam": beam_name,
        "model": model_kind,
        "segments": line["segments"],
        "span_lengths_m": [float(row["span_m"]) for row in span_rows],
        "simple_span_bounds_kNm": simple_bounds,
        "governing_hand_bound_kNm": hand_bound,
        "peak_sagging_kNm": max(response_m),
        "peak_hogging_kNm": min(response_m),
        "peak_abs_moment_kNm": peak_abs_moment,
        "peak_abs_shear_kN": max(abs(value) for value in response_v),
        "peak_abs_axial_kN": max(abs(value) for value in response_n),
        "max_vertical_displacement_m": max_vertical_displacement,
        "applied_service_load_kN": applied_load,
        "vertical_reaction_sum_kN": reaction_sum,
        "equilibrium_error_kN": reaction_sum - applied_load,
        "max_element_end_moment_error_kNm": max_end_moment_error,
        "hand_bound_order_check": "PASS" if bound_pass else "FAIL",
        "reactions": reactions,
        "profile_metadata": [item["metadata"] for item in profiles],
        "assumptions": [
            "Linear-elastic gross concrete sections with E = 30 GPa.",
            "Service G+Q loading; no load factors are applied in Step 06.",
            "Non-uniform slab profiles are discretised into 60 uniform sub-elements per span.",
            "The subframe contains one storey below the beam with fixed bases and no upper-storey columns.",
        ],
        "figure": figure_name,
    }

    if save_outputs:
        _plot_response(
            ROOT / figure_name,
            beam_name,
            model_kind,
            all_edges,
            node_coordinates,
            node_displacements,
            np.asarray(response_x),
            np.asarray(response_n),
            np.asarray(response_v),
            np.asarray(response_m),
            support_x,
            result,
        )
        (ROOT / result_name).write_text(json.dumps(result, indent=2), encoding="utf-8")

    ops.wipe()
    return result


def _plot_response(
    path: Path,
    beam_name: str,
    model_kind: str,
    edges: list[tuple[int, int, str]],
    coordinates: dict[int, tuple[float, float]],
    displacements: dict[int, tuple[float, float, float]],
    x: np.ndarray,
    axial: np.ndarray,
    shear: np.ndarray,
    moment: np.ndarray,
    support_x: list[float],
    result: dict,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), constrained_layout=True)
    ax = axes[0, 0]
    max_disp = max(max(abs(v[0]), abs(v[1])) for v in displacements.values())
    total_length = max(support_x)
    scale = 0.08 * total_length / max_disp if max_disp > 0.0 else 1.0
    for i, j, member_type in edges:
        xi, yi = coordinates[i]
        xj, yj = coordinates[j]
        ax.plot([xi, xj], [yi, yj], "--", color="#9ca3af", linewidth=1.0)
        uxi, uyi, _ = displacements[i]
        uxj, uyj, _ = displacements[j]
        colour = "#c52f3f" if member_type == "beam" else "#2563a6"
        ax.plot([xi + scale * uxi, xj + scale * uxj], [yi + scale * uyi, yj + scale * uyj], color=colour, linewidth=1.8)
    ax.set_title(f"Deformed shape (scale x{scale:.0f})")
    ax.set_xlabel("Model x (m)")
    ax.set_ylabel("Model y (m)")
    ax.grid(alpha=0.25)
    ax.set_aspect("equal", adjustable="datalim")

    diagrams = [
        (axes[0, 1], axial, "Axial force N (kN)", "#7c3aed"),
        (axes[1, 0], shear, "Shear V (kN)", "#0f766e"),
        (axes[1, 1], moment, "Bending moment M (kN m)", "#c2410c"),
    ]
    for diagram_ax, values, title, colour in diagrams:
        diagram_ax.axhline(0.0, color="#374151", linewidth=0.8)
        diagram_ax.plot(x, values, color=colour, linewidth=1.6)
        diagram_ax.fill_between(x, 0.0, values, color=colour, alpha=0.16)
        for support in support_x:
            diagram_ax.axvline(support, color="#9ca3af", linestyle=":", linewidth=0.8)
        diagram_ax.set_title(title)
        diagram_ax.set_xlabel("Distance along beam line (m)")
        diagram_ax.grid(alpha=0.2)

    fig.suptitle(
        f"{beam_name} - {model_kind.capitalize()} OpenSees Model | "
        f"M+={result['peak_sagging_kNm']:.1f}, M-={result['peak_hogging_kNm']:.1f} kN m",
        fontsize=14,
        fontweight="bold",
    )
    fig.savefig(path, dpi=190)
    plt.close(fig)
