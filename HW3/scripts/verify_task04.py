"""Check saved OpenSees responses against separate analytical and equilibrium routes."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
a=json.loads((ROOT/"outputs/Plan3/task3/Analytical_Result.json").read_text())
r=json.loads((ROOT/"outputs/Plan3/task4/OpenSees_Result.json").read_text())
checks=[]


def check(name,ok,error=None):
    v={"check":name,"pass":bool(ok)}
    if error is not None:v["error"]=float(error)
    checks.append(v)


cm=np.array(r["CM_m"]);F=np.array(r["F_about_CM"]);K=np.array(r["K_about_CM"])
case=a["cases"][a["adopted_case"]];expectedF=np.array(case["F_about_CM"])
err=np.max(abs(F-expectedF))/np.max(abs(expectedF))
check("hand/model flexibility",err<1e-6,err)
err_cr=np.max(abs(np.array(r["CR_m"])-case["CR_m"]))
check("hand/model CR",err_cr<1e-5,err_cr)
check("symmetric flexibility",np.max(abs(F-F.T))/np.max(abs(F))<1e-10)
check("positive-definite stiffness",np.all(np.linalg.eigvalsh(K)>0))
check("K F identity",np.max(abs(K@F-np.eye(3)))<1e-10)
check("explicit rigid diaphragm",r["model"]["diaphragm_command"]=="rigidDiaphragm(3,1,*wall_top_nodes)" and r["model"]["constraints"]=="Transformation")
check("one Timoshenko element per wall",r["model"]["wall_elements"]==len(a["walls"])==12 and r["model"]["elements_per_wall"]==1 and r["model"]["element_type"]=="ElasticTimoshenkoBeam")
check("wall cantilever top rotations free",r["model"]["wall_top_fixity"]==[0,0,1,0,0,0])
check("weak axis and intrinsic torsion match briefing",r["model"]["weak_axis_included"] and r["model"]["intrinsic_vertical_wall_torsion_J_m4"]==0)
all_cases={f"unit_{i}":c for i,c in enumerate(r["unit_cases"])}|{"design":r["demonstration_direct"]}|r["task5_cases"]
for name,c in all_cases.items():
    load=np.array(c["load_at_CM_Px_Py_Mz"]);q=np.array(c["master_displacement_u_v_phi"])
    reactions=np.zeros(3);max_constraint=0
    for w in c["walls"]:
        R=w["base_reaction_global"];dx,dy=np.array(w["centre_m"])-cm
        reactions+=np.array([R[0],R[1],R[5]+dx*R[1]-dy*R[0]])
        disp=w["top_displacement_global"]
        max_constraint=max(max_constraint,abs(disp[0]-(q[0]-dy*q[2])),abs(disp[1]-(q[1]+dx*q[2])),abs(disp[5]-q[2]))
    check(name+" converged",c["solver_exit"]==0)
    check(name+" horizontal/moment equilibrium",np.max(abs(reactions+load))<1e-7,np.max(abs(reactions+load)))
    check(name+" rigid-plane kinematics",max_constraint<1e-11,max_constraint)
    check(name+" load response agrees with F",np.max(abs(q-F@load))<1e-11)
bending=np.array(r["bending_only_F_about_CM"]);expected=np.array(a["cases"]["matched_rectangular_bending_only"]["F_about_CM"])
check("Euler-Bernoulli bending-only limit",np.max(abs(bending-expected))/np.max(abs(expected))<1e-6)
for i,l in enumerate(r["isolated_wall_limits"]):
    w=next(w for w in a["walls"] if w["label"]==l["wall"])
    direction="strong" if l["load_xy"][0] else "weak"
    field=f"k_{direction}_{'bending' if l['bending_only'] else 'shear'}_kN_m"
    actual=l["ux_m"] if direction=="strong" else l["uy_m"]
    check(f"isolated cantilever limit {i} ({direction})",abs(actual-1/w[field])/(1/w[field])<1e-7)
for name in ("unit_x_through_CR","unit_y_through_CR"):
    check(name+" zero rotation",abs(r["task5_cases"][name]["master_displacement_u_v_phi"][2])<1e-12)
check("unit forces at CM rotate",abs(r["unit_cases"][0]["master_displacement_u_v_phi"][2])+abs(r["unit_cases"][1]["master_displacement_u_v_phi"][2])>1e-12)
push=r["task5_cases"]["push_y_through_CR"];turn=r["task5_cases"]["pure_torque"];direct=r["demonstration_direct"]
check("push plus turn displacement",np.max(abs(np.array(push["master_displacement_u_v_phi"])+turn["master_displacement_u_v_phi"]-np.array(direct["master_displacement_u_v_phi"])))<1e-11)
expected_walls={w["wall"]:w for w in a["demonstration_y_force"]["wall_forces"]}
for d,p,t in zip(direct["walls"],push["walls"],turn["walls"]):
    vec=lambda x:np.array([x["resisting_demand_fx_kN"],x["resisting_demand_fy_kN"]])
    check("push/turn wall force "+d["wall"],np.max(abs(vec(p)+vec(t)-vec(d)))<1e-7)
    hand=expected_walls[d["wall"]]
    check("wall demand versus analytical "+d["wall"],np.max(abs(vec(d)-[hand["total_x_kN"],hand["total_y_kN"]]))<1e-7)
positive=sum(max(0,w["resisting_demand_fx_kN"]) for w in direct["walls"])
negative=sum(min(0,w["resisting_demand_fx_kN"]) for w in direct["walls"])
check("cross-direction forces equal and opposite in total",abs(positive+negative)<1e-7)
result={"passed":sum(c["pass"] for c in checks),"total":len(checks),"checks":checks,
        "relative_hand_model_F_error":err,"max_hand_model_CR_error_m":float(err_cr),
        "scope":"Tasks 4/5 numerical model and decomposition checks; inherited image/reader uncertainty is not removed."}
(ROOT/"records/Task4_5_Verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(f"Tasks 4/5 verification {result['passed']}/{result['total']}; CR error {err_cr:.3g} m; relative F error {err:.3g}")
if result["passed"]!=result["total"]:
    print([c for c in checks if not c["pass"]]);raise SystemExit(1)
