"""Build the HW2 one-floor space-frame strips for Beams A and B.

The floor beams form a plan grid at z=3 m. Vertical members extend to fixed
bases at z=0. Actual Step 05 strip-average service loads are applied to every
included beam. The old single-line subframes remain archived process evidence.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openseespy.opensees as ops

from hw2_beam_loads import BEAM_MAP, SEGMENTS

ROOT = Path(__file__).resolve().parent
E = 30.0e6
NU = 0.20
G = E / (2.0 * (1.0 + NU))
STOREY = 3.0
PROFILE_GROUP = 5  # 5 x 0.01 m source strips per analysis element

MODEL_DEFINITIONS = {
    "Beam A": {
        "selected": ["D19", "D11", "D05"],
        "members": ["D19", "D11", "D05", "D20", "D12", "D06", "D23", "D16", "D08", "D04"],
        "supports": [
            ("T9", 0.0, 0.0, 0.25, 2.00, 1.0),
            ("C6", 0.0, 6.05, 0.40, 0.40, 1.0),
            ("C3", 0.0, 12.10, 0.40, 0.40, 1.0),
            ("C2", 0.0, 15.20, 0.40, 0.40, 1.0),
            ("T10", 3.60, 0.0, 0.25, 2.00, 1.0),
            ("C7", 3.60, 6.05, 0.45, 0.45, 1.0),
            ("C4", 3.60, 12.10, 0.40, 0.40, 1.0),
            ("T3-A", 2.45, 15.20, 0.25, 1.00, 0.5),
            ("T3-B", 3.60, 15.20, 0.25, 1.00, 0.5),
        ],
        "selected_supports": ["T9", "C6", "C3", "C2"],
        "assumption": "One bay east of the peripheral Beam A line. D04 terminates at T3; T3 is represented by two half-wall vertical supports, so no fictitious D04 extension is added.",
    },
    "Beam B": {
        "selected": ["D16", "D17", "D18"],
        "members": ["D23", "D24", "D25", "D19", "D20", "D21", "D22", "D16", "D17", "D18", "D11", "D12", "D14", "D15", "D08", "D09", "D13", "D10"],
        "supports": [
            ("T9", 0.0, 0.0, 0.25, 2.00, 1.0),
            ("T10", 3.60, 0.0, 0.25, 2.00, 1.0),
            ("T11", 6.60, 0.0, 0.25, 2.00, 1.0),
            ("T12", 10.20, 0.0, 0.25, 2.00, 1.0),
            ("C6", 0.0, 6.05, 0.40, 0.40, 1.0),
            ("C7", 3.60, 6.05, 0.45, 0.45, 1.0),
            ("C8", 6.60, 6.05, 0.40, 0.40, 1.0),
            ("C9", 10.20, 6.05, 0.40, 0.40, 1.0),
            ("C3", 0.0, 12.10, 0.40, 0.40, 1.0),
            ("C4", 3.60, 12.10, 0.40, 0.40, 1.0),
            ("C5", 10.20, 12.10, 0.40, 0.40, 1.0),
            ("T4-W", 4.70, 12.10, 0.25, 1.525, 0.5),
            ("T4-E", 7.75, 12.10, 0.25, 1.525, 0.5),
            ("T7-S", 6.60, 7.20, 0.25, 1.70, 0.5),
            ("T7-N", 6.60, 10.60, 0.25, 1.70, 0.5),
        ],
        "selected_supports": ["C6", "C7", "C8", "C9"],
        "assumption": "One bay south and the available supported branches north of Beam B. Core walls T4/T7 are split into half-wall vertical supports at actual beam termination points; no fictitious beam is drawn through the openings.",
    },
}


def read_csv(name):
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def key(x, y, z=STOREY):
    return (round(float(x), 8), round(float(y), 8), round(float(z), 8))


def section_properties(width, depth):
    area = width * depth
    iy = width * depth**3 / 12.0  # vertical bending when local z is global Z
    iz = depth * width**3 / 12.0
    a = max(width, depth)
    b = min(width, depth)
    ratio = b / a
    torsion = a * b**3 * (1.0 / 3.0 - 0.21 * ratio * (1.0 - ratio**4 / 12.0))
    return area, iy, iz, torsion


def grouped_profile(beam_id, profile_rows):
    rows = [r for r in profile_rows if r["beam_id"] == beam_id]
    grouped = []
    for start in range(0, len(rows), PROFILE_GROUP):
        chunk = rows[start:start + PROFILE_GROUP]
        s0 = float(chunk[0]["s0_m"])
        s1 = float(chunk[-1]["s1_m"])
        force = sum((float(r["s1_m"]) - float(r["s0_m"])) * float(r["service_kN_m"]) for r in chunk)
        grouped.append((s0, s1, force / (s1 - s0)))
    return grouped


def build_model(name):
    definition = MODEL_DEFINITIONS[name]
    profile_rows = read_csv("Step_05_Beam_Load_Profiles.csv")
    endpoint_rows = read_csv("Step_05_Beam_Endpoint_Loads.csv")
    hw1 = {r["element_id"]: r for r in read_csv("Step_02_Element_Load_Summary.csv")}

    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)  # horizontal members: local z is vertical
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)  # vertical members

    nodes = {}
    coordinates = {}
    next_node = 1
    def node_at(x, y, z=STOREY):
        nonlocal next_node
        k = key(x, y, z)
        if k not in nodes:
            nodes[k] = next_node
            coordinates[next_node] = k
            ops.node(next_node, *k)
            next_node += 1
        return nodes[k]

    beam_elements = []
    selected_elements = []
    nodal_loads = defaultdict(float)
    next_element = 1
    represented_force = defaultdict(float)
    for beam_id in definition["members"]:
        beam = BEAM_MAP[beam_id]
        seg = SEGMENTS[beam_id]
        length = seg.length
        ux = (seg.x2 - seg.x1) / length
        uy = (seg.y2 - seg.y1) / length
        width = float(beam["width_mm"]) / 1000.0
        depth = float(beam["depth_mm"]) / 1000.0
        area, iy, iz, torsion = section_properties(width, depth)
        for s0, s1, q in grouped_profile(beam_id, profile_rows):
            x0, y0 = seg.x1 + ux*s0, seg.y1 + uy*s0
            x1, y1 = seg.x1 + ux*s1, seg.y1 + uy*s1
            ni, nj = node_at(x0, y0), node_at(x1, y1)
            tag = next_element
            next_element += 1
            ops.element("elasticBeamColumn", tag, ni, nj, area, E, G, torsion, iy, iz, 1)
            interval = s1 - s0
            nodal_loads[ni] -= q * interval / 2.0
            nodal_loads[nj] -= q * interval / 2.0
            represented_force[beam_id] += q * interval
            item = dict(tag=tag, beam_id=beam_id, ni=ni, nj=nj, s0=s0, s1=s1, q=q)
            beam_elements.append(item)
            if beam_id in definition["selected"]:
                selected_elements.append(item)
        for endpoint in endpoint_rows:
            if endpoint["beam_id"] != beam_id:
                continue
            station = float(endpoint["s_m"])
            target = node_at(seg.x1 + ux*station, seg.y1 + uy*station)
            force = float(endpoint["service_kN"])
            nodal_loads[target] -= force
            represented_force[beam_id] += force

    support_data = []
    for label, x, y, width, depth, weight_factor in definition["supports"]:
        top = node_at(x, y)
        base = node_at(x, y, 0.0)
        ops.fix(base, 1, 1, 1, 1, 1, 1)
        area, iy, iz, torsion = section_properties(width, depth)
        tag = next_element
        next_element += 1
        ops.element("elasticBeamColumn", tag, base, top, area, E, G, torsion, iy, iz, 2)
        self_weight = area * STOREY * 25.0
        nodal_loads[top] -= self_weight
        support_data.append(dict(label=label, top=top, base=base, tag=tag, x=x, y=y,
                                 self_weight=self_weight, weight_factor=weight_factor))

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    for node, fz in nodal_loads.items():
        ops.load(node, 0.0, 0.0, fz, 0.0, 0.0, 0.0)

    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1e-10, 30)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    code = ops.analyze(1)
    if code != 0:
        raise RuntimeError(f"{name} grid subframe failed with code {code}")
    ops.reactions()

    reactions = []
    for support in support_data:
        values = [float(v) for v in ops.nodeReaction(support["base"])]
        reactions.append(dict(support=support["label"], x_m=support["x"], y_m=support["y"],
                              Rx_kN=values[0], Ry_kN=values[1], Rz_kN=values[2],
                              Mx_kNm=values[3], My_kNm=values[4], Mz_kNm=values[5],
                              vertical_member_self_weight_kN=support["self_weight"]))

    station_offset = {}
    cursor = 0.0
    for beam_id in definition["selected"]:
        station_offset[beam_id] = cursor
        cursor += SEGMENTS[beam_id].length
    response = []
    for element in selected_elements:
        force = [float(v) for v in ops.eleResponse(element["tag"], "localForce")]
        ni, nj = element["ni"], element["nj"]
        for end, node, station, axial, shear, moment in (
            ("i", ni, element["s0"], -force[0], force[2], force[4]),
            ("j", nj, element["s1"], force[6], -force[8], -force[10]),
        ):
            disp = [float(v) for v in ops.nodeDisp(node)]
            response.append(dict(beam_id=element["beam_id"], end=end,
                                 station_m=station_offset[element["beam_id"]] + station,
                                 local_station_m=station, axial_kN=axial,
                                 vertical_shear_kN=shear, bending_moment_kNm=moment,
                                 vertical_displacement_m=disp[2]))
    response.sort(key=lambda r: (r["station_m"], 0 if r["end"] == "i" else 1))

    displacements = {node: tuple(float(v) for v in ops.nodeDisp(node)) for node in coordinates}
    applied = -sum(nodal_loads.values())
    reaction_sum = sum(r["Rz_kN"] for r in reactions)
    source_expected = sum(represented_force.values())
    support_self_weight = sum(r["vertical_member_self_weight_kN"] for r in reactions)
    result = {
        "beam": name,
        "model": "one-floor plan-grid subframe",
        "included_members": definition["members"],
        "selected_members": definition["selected"],
        "support_assumption": definition["assumption"],
        "profile_source_sha256": hashlib.sha256((ROOT/"Step_05_Beam_Load_Profiles.csv").read_bytes()).hexdigest(),
        "represented_beam_service_load_kN": source_expected,
        "vertical_member_self_weight_kN": support_self_weight,
        "applied_vertical_load_kN": applied,
        "vertical_reaction_sum_kN": reaction_sum,
        "equilibrium_error_kN": reaction_sum-applied,
        "peak_sagging_kNm": max(r["bending_moment_kNm"] for r in response),
        "peak_hogging_kNm": min(r["bending_moment_kNm"] for r in response),
        "peak_abs_shear_kN": max(abs(r["vertical_shear_kN"]) for r in response),
        "peak_abs_axial_kN": max(abs(r["axial_kN"]) for r in response),
        "max_vertical_displacement_m": max(abs(r["vertical_displacement_m"]) for r in response),
        "max_floor_grid_vertical_displacement_m": max(abs(displacements[n][2]) for n,c in coordinates.items() if math.isclose(c[2],STOREY)),
        "reactions": reactions,
        "assumptions": [
            "3D elastic space frame; floor beams at z=3 m and vertical members fixed at z=0.",
            "Gross uncracked sections, E=30 GPa, nu=0.20, service G+Q beam loads.",
            "Every included beam uses the actual Step 05 profile grouped from 0.01 m into 0.05 m intervals without force rescaling.",
            "Vertical-member self-weight is applied at each support top; slab load assigned directly to walls and the unresolved core area are excluded.",
            "Wall supports are discrete line-end idealisations; diaphragm action, slab stiffness, cracking and upper storeys are omitted.",
        ],
    }
    slug = name.replace(" ", "")
    (ROOT/f"Step_08_{slug}_Grid_Result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_rows(ROOT/f"Step_08_{slug}_Selected_Response.csv", response)
    plot_result(name, definition, coordinates, displacements, beam_elements, support_data, response, reactions, result)
    ops.wipe()
    return result, hw1


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot_result(name, definition, coordinates, displacements, elements, support_data, response, reactions, result):
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    plan = axes[0, 0]
    for item in elements:
        a, b = coordinates[item["ni"]], coordinates[item["nj"]]
        selected = item["beam_id"] in definition["selected"]
        plan.plot([a[0], b[0]], [a[1], b[1]], color="#c52f3f" if selected else "#536a82",
                  linewidth=2.6 if selected else 1.0)
    for r in reactions:
        plan.scatter(r["x_m"], r["y_m"], marker="s", s=24, color="#1b3a57")
        plan.text(r["x_m"], r["y_m"], r["support"], fontsize=6)
    plan.set(title="Plan grid and vertical supports", xlabel="x (m)", ylabel="y (m)")
    plan.set_aspect("equal"); plan.grid(alpha=.2)

    x = np.asarray([r["station_m"] for r in response])
    curves = [
        (axes[0,1], np.asarray([1000*r["vertical_displacement_m"] for r in response]), "Selected-beam vertical displacement", "mm", "#c52f3f"),
        (axes[0,2], np.asarray([r["axial_kN"] for r in response]), "Selected-beam axial N", "kN", "#7c3aed"),
        (axes[1,0], np.asarray([r["vertical_shear_kN"] for r in response]), "Selected-beam vertical shear V", "kN", "#0f766e"),
        (axes[1,1], np.asarray([r["bending_moment_kNm"] for r in response]), "Selected-beam bending moment M", "kN m", "#c2410c"),
    ]
    for ax, y, title, unit, colour in curves:
        ax.axhline(0,color="#444",linewidth=.7)
        ax.plot(x,y,color=colour,linewidth=1.3)
        ax.fill_between(x,0,y,color=colour,alpha=.15)
        ax.set(title=title,xlabel="Distance along selected beam (m)",ylabel=unit)
        ax.grid(alpha=.2)
    ax=axes[1,2]
    labels=[r["support"] for r in reactions]
    values=[r["Rz_kN"] for r in reactions]
    ax.bar(np.arange(len(labels)),values,color="#4776b4")
    ax.set_xticks(np.arange(len(labels)),labels,rotation=75,fontsize=7)
    ax.set(title="Vertical base reactions",ylabel="kN");ax.grid(axis="y",alpha=.2)
    fig.suptitle(f"{name} | One-floor plan-grid subframe | M+={result['peak_sagging_kNm']:.1f}, M-={result['peak_hogging_kNm']:.1f} kN m",fontweight="bold")
    fig.savefig(ROOT/f"Step_08_{name.replace(' ','')}_Grid_Response.png",dpi=190)
    plt.close(fig)

    fig=plt.figure(figsize=(12,8),layout="constrained")
    ax=fig.add_subplot(111,projection="3d")
    max_disp=max(abs(v[2]) for v in displacements.values())
    scale=1.2/max_disp if max_disp else 1.0
    for item in elements:
        a,b=coordinates[item["ni"]],coordinates[item["nj"]]
        da,db=displacements[item["ni"]],displacements[item["nj"]]
        ax.plot([a[0],b[0]],[a[1],b[1]],[a[2],b[2]],linestyle="--",color="#a3aab3",linewidth=.5)
        selected=item["beam_id"] in definition["selected"]
        ax.plot([a[0]+scale*da[0],b[0]+scale*db[0]],
                [a[1]+scale*da[1],b[1]+scale*db[1]],
                [a[2]+scale*da[2],b[2]+scale*db[2]],
                color="#c52f3f" if selected else "#2563a6",linewidth=2.2 if selected else 1.0)
    for support in support_data:
        a,b=coordinates[support["base"]],coordinates[support["top"]]
        da,db=displacements[support["base"]],displacements[support["top"]]
        ax.plot([a[0],b[0]],[a[1],b[1]],[a[2],b[2]],linestyle="--",color="#a3aab3",linewidth=.5)
        ax.plot([a[0]+scale*da[0],b[0]+scale*db[0]],
                [a[1]+scale*da[1],b[1]+scale*db[1]],
                [a[2]+scale*da[2],b[2]+scale*db[2]],color="#1f4f82",linewidth=1.2)
    ax.set(xlabel="x (m)",ylabel="y (m)",zlabel="z / scaled vertical deformation (m)")
    ax.set_title(f"{name} one-floor grid | whole-subframe deformed shape (scale x{scale:.0f})")
    ax.view_init(elev=24,azim=-58)
    fig.savefig(ROOT/f"Step_08_{name.replace(' ','')}_Whole_Grid_Deformed.png",dpi=190)
    plt.close(fig)


def main():
    results=[]
    hw1=None
    for name in ("Beam A", "Beam B"):
        result, hw1=build_model(name)
        results.append(result)
    summary=[]; reactions=[]; cross=[]
    for result in results:
        summary.append({k:result[k] for k in ("beam","model","represented_beam_service_load_kN","vertical_member_self_weight_kN","applied_vertical_load_kN","vertical_reaction_sum_kN","equilibrium_error_kN","peak_sagging_kNm","peak_hogging_kNm","peak_abs_shear_kN","peak_abs_axial_kN","max_vertical_displacement_m")})
        selected=set(MODEL_DEFINITIONS[result["beam"]]["selected_supports"])
        for reaction in result["reactions"]:
            reactions.append(dict(beam=result["beam"],**reaction))
            if reaction["support"] not in selected:
                continue
            row=hw1[reaction["support"]]
            hw1_service=float(row["total_G_per_floor_kN"])+float(row["total_Q_per_floor_kN"])
            grid=float(reaction["Rz_kN"])
            cross.append(dict(beam=result["beam"],grid_point=reaction["support"],
                              HW1_one_floor_G_plus_Q_kN=hw1_service,
                              grid_subframe_base_reaction_kN=grid,
                              difference_percent=100*(grid-hw1_service)/hw1_service,
                              interpretation="Not expected to match exactly: local grid excludes direct wall loads, unresolved core area, slab stiffness and upper storeys."))
    write_rows(ROOT/"Step_08_Grid_Subframe_Summary.csv",summary)
    write_rows(ROOT/"Step_08_Grid_Subframe_Reactions.csv",reactions)
    write_rows(ROOT/"Step_12_HW1_Grid_Subframe_Cross_Check.csv",cross)
    cross_check_figure(cross)
    report(results,cross)
    maximum=max(abs(r["equilibrium_error_kN"]) for r in results)
    print(f"Built {len(results)} plan-grid subframes; maximum equilibrium error {maximum:.3e} kN")


def report(results,cross):
    old={}
    for name in ("BeamA","BeamB"):
        old[(name,"pure")]=json.loads((ROOT/f"Step_06_{name}_Pure_Result.json").read_text())
    text=["# Tasks 8, 10 and 12 - One-Floor Plan-Grid Subframes", "",
          "## Scope", "",
          "This revision replaces the earlier single-line subframe for final comparisons. The pure-beam models remain the Task 7 references. The grid models add perpendicular floor beams and their vertical supports so that the marked beam can redistribute load into neighbouring members.", "",
          "The models are local strips, not a full-building finite-element model. They use image-derived axes and explicit wall-end idealisations. Direct slab load assigned to walls and 1.707500 m2 of unresolved core area are excluded. Therefore the Task 12 comparison is an explained consistency check, not forced equality.", ""]
    for result in results:
        pure=old[(result["beam"].replace(" ",""),"pure")]
        text += [f"## {result['beam']}", "", MODEL_DEFINITIONS[result["beam"]]["assumption"], "",
                 f"![{result['beam']} grid response](Step_08_{result['beam'].replace(' ','')}_Grid_Response.png)", "",
                 f"![{result['beam']} whole-grid deformation](Step_08_{result['beam'].replace(' ','')}_Whole_Grid_Deformed.png)", "",
                 "| Quantity | Pure beam | Plan-grid subframe |", "|---|---:|---:|",
                 f"| Peak sagging moment (kN m) | {pure['peak_sagging_kNm']:.3f} | {result['peak_sagging_kNm']:.3f} |",
                 f"| Peak hogging moment (kN m) | {pure['peak_hogging_kNm']:.3f} | {result['peak_hogging_kNm']:.3f} |",
                 f"| Peak absolute shear (kN) | {pure['peak_abs_shear_kN']:.3f} | {result['peak_abs_shear_kN']:.3f} |",
                 f"| Peak absolute axial (kN) | {pure['peak_abs_axial_kN']:.3f} | {result['peak_abs_axial_kN']:.3f} |",
                 f"| Maximum vertical displacement (mm) | {1000*pure['max_vertical_displacement_m']:.3f} | {1000*result['max_vertical_displacement_m']:.3f} |", "",
                 "The pure model restrains only the marked line. The grid subframe introduces column/wall rotational stiffness and alternate paths through perpendicular members; consequently its moments, reactions and deflection differ. The grid subframe is the more defensible of these two for load distribution, while the pure model remains a transparent limiting/check model.", ""]
    text += ["## Task 12 cross-check", "", "| Beam | Grid point | HW1 one-floor G+Q (kN) | Grid reaction (kN) | Difference |", "|---|---|---:|---:|---:|"]
    text += [f"| {r['beam']} | {r['grid_point']} | {r['HW1_one_floor_G_plus_Q_kN']:.3f} | {r['grid_subframe_base_reaction_kN']:.3f} | {r['difference_percent']:+.1f}% |" for r in cross]
    text += ["", "![Task 12 comparison](Step_12_HW1_Grid_Subframe_Cross_Check.png)", "", "The signs and force scale must be checked first. Remaining differences are expected because HW1 assigns the complete floor directly by vertical-element tributary regions, whereas these local grids contain only listed beam branches and omit direct wall slab loads, unresolved core load, slab diaphragm/plate stiffness and upper-storey participation. Large differences therefore identify model-scope mismatch rather than being hidden by artificial nodal loads.", "",
             "## Reproduction and process evidence", "", "- Script: `step08_grid_subframes.py`.", "- Source loads: `Step_05_Beam_Load_Profiles.csv`.", "- Machine-readable results: `Step_08_BeamA_Grid_Result.json`, `Step_08_BeamB_Grid_Result.json`.", "- Reactions and response ordinates: the Step 08 CSV files.", "- Independent checks: `verify_step08_grid_subframes.py` and `Step_08_Grid_Subframe_Verification.csv`.", "",
             "Student sign-off remains required for the image-derived beam mapping, wall-end idealisations, hand moment bounds and four hand-drawn deformation sketches."]
    (ROOT/"Step_08_Grid_Subframes_and_Task12.md").write_text("\n".join(text)+"\n",encoding="utf-8")


def cross_check_figure(rows):
    labels=[f"{r['beam'][-1]}:{r['grid_point']}" for r in rows]
    hw1=[r["HW1_one_floor_G_plus_Q_kN"] for r in rows]
    grid=[r["grid_subframe_base_reaction_kN"] for r in rows]
    x=np.arange(len(rows)); width=.38
    fig,ax=plt.subplots(figsize=(11,5.8),layout="constrained")
    ax.bar(x-width/2,hw1,width,label="HW1 one-floor G+Q",color="#4776b4")
    ax.bar(x+width/2,grid,width,label="Plan-grid subframe reaction",color="#d46a42")
    for i,row in enumerate(rows):
        ax.text(i,max(hw1[i],grid[i])+5,f"{row['difference_percent']:+.0f}%",ha="center",fontsize=8)
    ax.set_xticks(x,labels);ax.set_ylabel("Vertical force (kN)")
    ax.set_title("Task 12 scope check: HW1 tributary axial vs local-grid base reaction")
    ax.legend();ax.grid(axis="y",alpha=.2)
    fig.savefig(ROOT/"Step_12_HW1_Grid_Subframe_Cross_Check.png",dpi=190)
    plt.close(fig)


if __name__ == "__main__":
    main()
