"""Write the matched OpenSees/decomposition report and inspectable figures."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/"outputs/Plan3/task4"
    r=json.loads((out/"OpenSees_Result.json").read_text())
    a=json.loads((ROOT/"outputs/Plan3/task3/Analytical_Result.json").read_text())
    v=json.loads((ROOT/"records/Task4_5_Verification.json").read_text())
    cr=r["CR_m"];cm=r["CM_m"];q=r["demonstration_direct"]["master_displacement_u_v_phi"]
    direct=r["demonstration_direct"]["walls"];hand={w["wall"]:w for w in a["demonstration_y_force"]["wall_forces"]}
    rows=["# HW3 Tasks 4 and 5 - Rigid diaphragm and no-rotation check","",
          "Status: verified numerical model of the provisional common-geometry baseline. Task 2 experiment-control and identity limits remain documented.","",
          "## Model and conventions","",
          f"OpenSeesPy engine {r['solver_version']}; 3D, six DOF per node, one 3 m vertical ElasticTimoshenkoBeam per wall, 12 main-wall rectangles, fixed bases. E=30e6 kN/m2, nu=0.2, G=12.5e6 kN/m2, shear area=(5/6)Lt in each principal direction. Local y follows the wall length; Iz=tL^3/12 is strong and Iy=Lt^3/12 weak. Both are retained. Intrinsic vertical wall torsion J=0 is excluded consistently with the analytical model. Short returns, columns, cracking and slab flexibility are excluded.","",
          "The CM master has fixity (0,0,1,1,1,0). Wall-top z is fixed, bending rotations remain free. ops.rigidDiaphragm(3, master, *tops) and Transformation constraints explicitly enforce the floor plane. This is not a very-stiff-slab substitute or fixed-fixed wall model.","",
          "The command usage follows the official [ElasticTimoshenkoBeam documentation](https://openseespydoc.readthedocs.io/en/latest/src/ElasticTimoshenkoBeam.html) and [rigidDiaphragm documentation](https://openseespydoc.readthedocs.io/en/latest/src/rigidDiaphragm.html). The [model briefing](records/Task_04_Model_Briefing.md) and analytical result were committed before executing OpenSees.","",
          "## Three independent unit loads","",
          "Three rebuilt models apply Px=1 kN, Py=1 kN and Mz=1 kN m at CM. Master u, v and phi are the columns of F. K=inv(F). Units are kN, m and radians; mixed matrix entries carry their corresponding translational/rotational units.","",
          "```text","F about CM:",np.array2string(np.array(r["F_about_CM"]),precision=12),"","K about CM:",np.array2string(np.array(r["K_about_CM"]),precision=6),"```","",
          f"CM=({cm[0]:.6f}, {cm[1]:.6f}) m. Flexibility-derived CR=({cr[0]:.6f}, {cr[1]:.6f}) m; e={r['eccentricity_m']:.6f} m. Maximum analytical/OpenSees CR difference is {v['max_hand_model_CR_error_m']:.3e} m; relative flexibility error is {v['relative_hand_model_F_error']:.3e}.","",
          "[Raw solver responses](outputs/Plan3/task4/OpenSees_Result.json) retain unit loads, master and wall-top displacements, base reactions and element end forces. The no-shear sensitivity is an actual rebuilt elasticBeamColumn model; isolated strong/weak cantilever tests also check local-axis orientation and shear compliance.","",
          "## Assumed 100 kN y demonstration","",
          "The test force is explicitly assumed for linear verification; it is not a specified code design earthquake load. The same wall geometry and shear assumptions apply to every CR reported above.","",
          f"Master response: u={q[0]*1000:.6f} mm, v={q[1]*1000:.6f} mm, phi={q[2]:.9g} rad. Positive demand values below are minus the corresponding base reaction. The raw six-component base reactions are retained in [the reaction table](outputs/Plan3/task4/Demonstration_Wall_Reactions.csv).","",
          "| Wall | Push y (kN) | Turn y (kN) | Total y (kN) | Total x (kN) |","|---|---:|---:|---:|---:|"]
    rows += [f"| {w['wall']} | {hand[w['wall']]['direct_y_kN']:.6f} | {hand[w['wall']]['torsional_y_kN']:.6f} | {w['resisting_demand_fy_kN']:.6f} | {w['resisting_demand_fx_kN']:.6f} |" for w in direct]
    rows += ["","Total y resistance equals 100 kN. Total x resistance is zero, with positive and negative cross-direction forces balancing. In an asymmetric layout individual walls need not form equal pairs; the full signed group must balance. Base force/moment sums and each top node's rigid-plane displacement relation are independently checked.","",
             "![Wall forces under the demonstration load](outputs/Plan3/task4/Wall_Force_Comparison.png)","",
             "## Task 5 - push through CR, and push plus turn","",
             "A force at a plan offset is applied at the CM master with its equivalent signed moment. Unit Px through CR has moment -(yr-ym); unit Py through CR has moment +(xr-xm). Their rotations are:","",
             "| Case | Rotation (rad) |","|---|---:|"]
    for name in ("unit_x_through_CR","unit_y_through_CR"):
        rows.append(f"| {name} | {r['task5_cases'][name]['master_displacement_u_v_phi'][2]:.6e} |")
    rows += ["",f"The direct 100 kN force at CM decomposes into a push through CR plus signed torque T=(xm-xr)*Fy={r['torque_for_decomposition_kN_m']:.6f} kN m. Rebuilt push and torque runs superpose to the direct run in all master responses and all wall forces. General torque is ex*Fy-ey*Fx; total eccentricity times force applies only for a perpendicular force direction.","",
             "## Verification and reproduction","",
             f"{v['passed']}/{v['total']} checks passed. See [verification record](records/Task4_5_Verification.json) for flexibility symmetry, positive stiffness, hand/model agreement, single-wall limits, actual bending-only limit, reaction closure, rigid-plane kinematics, zero rotation through CR and load decomposition.","",
             "```text","python HW3/scripts/task04_opensees.py","python HW3/scripts/verify_task04.py","python HW3/scripts/write_task04_report.py","```","",
             "This validates the declared numerical idealisation; it does not certify the image-derived source geometry or complete the remaining HW3 tasks."]
    (ROOT/"HW3_Task_04_05_OpenSees_Report.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    fig,(ax,bx)=plt.subplots(1,2,figsize=(12,7))
    labels=[w["wall"] for w in direct];ix=np.arange(len(labels))
    ax.barh(ix,[hand[n]["direct_y_kN"] for n in labels],label="Push through CR",color="#719ab5")
    ax.barh(ix,[hand[n]["torsional_y_kN"] for n in labels],left=[hand[n]["direct_y_kN"] for n in labels],label="Signed turn component",color="#d1915f")
    ax.scatter([w["resisting_demand_fy_kN"] for w in direct],ix,c="black",marker="x",label="OpenSees total")
    ax.set(yticks=ix,yticklabels=labels,xlabel="Global y wall demand (kN)",title="100 kN y force at CM: push + turn")
    ax.legend(fontsize=8)
    bx.barh(ix,[w["resisting_demand_fx_kN"] for w in direct],color="#7d79a8")
    bx.axvline(0,color="black",lw=.7);bx.set(yticks=ix,yticklabels=labels,xlabel="Global x wall demand (kN)",title="Cross-direction forces: signed sum = 0")
    fig.tight_layout();fig.savefig(out/"Wall_Force_Comparison.png",dpi=160);plt.close(fig)
    print("Wrote Tasks 4/5 English report and wall-force figure")


if __name__=="__main__":main()
