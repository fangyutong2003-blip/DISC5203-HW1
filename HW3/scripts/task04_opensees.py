"""Explicit rigid-diaphragm Timoshenko model and independent load cases."""
import csv
import json
from pathlib import Path
import numpy as np
import openseespy.opensees as ops

ROOT=Path(__file__).resolve().parents[1]


def build(walls,cm,p,bending_only=False):
    ops.wipe();ops.model("basic","-ndm",3,"-ndf",6)
    E=p["E_kN_m2"];G=E/(2*(1+p["nu"]));H=p["height_m"]
    ops.node(1,float(cm[0]),float(cm[1]),H);ops.fix(1,0,0,1,1,1,0)
    ops.geomTransf("Linear",1,0,1,0)
    ops.geomTransf("Linear",2,-1,0,0)
    tops=[]
    for i,w in enumerate(walls):
        base=100+i;top=200+i;tag=1000+i
        x,y=w["centre_m"]
        ops.node(base,x,y,0);ops.node(top,x,y,H)
        ops.fix(base,1,1,1,1,1,1);ops.fix(top,0,0,1,0,0,0)
        transformation=1 if w["angle_deg"]==0 else 2
        if bending_only:
            ops.element("elasticBeamColumn",tag,base,top,w["A_m2"],E,G,p["wall_intrinsic_torsion_J_m4"],w["I_weak_m4"],w["I_strong_m4"],transformation)
        else:
            ops.element("ElasticTimoshenkoBeam",tag,base,top,E,G,w["A_m2"],p["wall_intrinsic_torsion_J_m4"],w["I_weak_m4"],w["I_strong_m4"],w["Av_m2"],w["Av_m2"],transformation)
        tops.append(top)
    ops.rigidDiaphragm(3,1,*tops)
    ops.constraints("Transformation")
    ops.numberer("RCM");ops.system("FullGeneral");ops.algorithm("Linear")
    ops.integrator("LoadControl",1.);ops.analysis("Static")


def solve(walls,cm,p,load,bending_only=False):
    build(walls,cm,p,bending_only)
    ops.timeSeries("Constant",1);ops.pattern("Plain",1,1)
    ops.load(1,float(load[0]),float(load[1]),0,0,0,float(load[2]))
    code=ops.analyze(1)
    if code:raise RuntimeError(f"OpenSees failed: {code}")
    ops.reactions()
    q=[float(ops.nodeDisp(1,d)) for d in (1,2,6)]
    rows=[]
    for i,w in enumerate(walls):
        reaction=list(map(float,ops.nodeReaction(100+i)))
        rows.append({"wall":w["label"],"centre_m":w["centre_m"],"base_reaction_global":reaction,
                     "resisting_demand_fx_kN":-reaction[0],"resisting_demand_fy_kN":-reaction[1],
                     "top_displacement_global":list(map(float,ops.nodeDisp(200+i))),
                     "element_global_end_forces":list(map(float,ops.eleForce(1000+i)))})
    return {"load_at_CM_Px_Py_Mz":list(map(float,load)),"master_displacement_u_v_phi":q,"walls":rows,"solver_exit":code}


def isolated_wall_limit(w,p,bending_only,load):
    ops.wipe();ops.model("basic","-ndm",3,"-ndf",6)
    E=p["E_kN_m2"];G=E/(2*(1+p["nu"]));H=p["height_m"]
    ops.node(1,0,0,0);ops.node(2,0,0,H)
    ops.fix(1,1,1,1,1,1,1);ops.fix(2,0,0,1,0,0,1)
    ops.geomTransf("Linear",1,0,1,0)
    if bending_only:
        ops.element("elasticBeamColumn",1,1,2,w["A_m2"],E,G,0.,w["I_weak_m4"],w["I_strong_m4"],1)
    else:
        ops.element("ElasticTimoshenkoBeam",1,1,2,E,G,w["A_m2"],0.,w["I_weak_m4"],w["I_strong_m4"],w["Av_m2"],w["Av_m2"],1)
    ops.timeSeries("Constant",1);ops.pattern("Plain",1,1);ops.load(2,float(load[0]),float(load[1]),0,0,0,0)
    ops.constraints("Transformation");ops.numberer("RCM");ops.system("FullGeneral")
    ops.algorithm("Linear");ops.integrator("LoadControl",1);ops.analysis("Static")
    code=ops.analyze(1)
    if code:raise RuntimeError("Isolated wall failed")
    return {"wall":w["label"],"bending_only":bending_only,"load_xy":load,
            "ux_m":ops.nodeDisp(2,1),"uy_m":ops.nodeDisp(2,2)}


def main():
    analytical=json.loads((ROOT/"outputs/Plan3/task3/Analytical_Result.json").read_text())
    walls=analytical["walls"];cm=np.array(analytical["mass"]["CM_m"]);p=analytical["parameters"]
    out=ROOT/"outputs/Plan3/task4";out.mkdir(parents=True,exist_ok=True)
    units=[solve(walls,cm,p,v) for v in np.eye(3)]
    F=np.array([u["master_displacement_u_v_phi"] for u in units]).T
    K=np.linalg.inv(F)
    cr=np.array([cm[0]-F[2,1]/F[2,2],cm[1]+F[2,0]/F[2,2]])
    F_bend=np.array([solve(walls,cm,p,v,True)["master_displacement_u_v_phi"] for v in np.eye(3)]).T
    force=p["design_demonstration_force_kN"]
    direct=solve(walls,cm,p,[0,force,0])
    dx,dy=cr-cm;torque=-dx*force
    tests={"unit_x_through_CR":solve(walls,cm,p,[1,0,-dy]),
           "unit_y_through_CR":solve(walls,cm,p,[0,1,dx]),
           "push_y_through_CR":solve(walls,cm,p,[0,force,force*dx]),
           "pure_torque":solve(walls,cm,p,[0,0,torque])}
    limits=[]
    sample=walls[0]
    for bending in (False,True):
        for load in ([1,0],[0,1]):limits.append(isolated_wall_limit(sample,p,bending,load))
    result={"status":p["selection_status"],"solver_version":ops.version(),
            "model":{"ndm":3,"ndf":6,"wall_elements":len(walls),"element_type":"ElasticTimoshenkoBeam",
                     "elements_per_wall":1,"height_m":p["height_m"],"shear_included":True,
                     "weak_axis_included":True,"intrinsic_vertical_wall_torsion_J_m4":0.,
                     "diaphragm_command":"rigidDiaphragm(3,1,*wall_top_nodes)","constraints":"Transformation",
                     "master_fixity":[0,0,1,1,1,0],"wall_top_fixity":[0,0,1,0,0,0],
                     "orientation":"local x vertical; local y along horizontal wall length; Iz strong and Iy weak"},
            "CM_m":cm.tolist(),"F_about_CM":F.tolist(),"K_about_CM":K.tolist(),"CR_m":cr.tolist(),
            "eccentricity_m":float(np.linalg.norm(cr-cm)),"unit_cases":units,
            "bending_only_F_about_CM":F_bend.tolist(),"demonstration_direct":direct,
            "task5_cases":tests,"isolated_wall_limits":limits,
            "torque_for_decomposition_kN_m":float(torque)}
    (out/"OpenSees_Result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (out/"Demonstration_Wall_Reactions.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f);writer.writerow(["wall","x_m","y_m","base_Rx_kN","base_Ry_kN","base_Rz_kN","base_Mx_kN_m","base_My_kN_m","base_Mz_kN_m","resisting_fx_kN","resisting_fy_kN"])
        for w in direct["walls"]:writer.writerow([w["wall"],*w["centre_m"],*w["base_reaction_global"],w["resisting_demand_fx_kN"],w["resisting_demand_fy_kN"]])
    print("OpenSees",result["solver_version"],"CR",cr,"e",result["eccentricity_m"])
    print("Relative F error",np.max(abs(F-np.array(analytical["cases"][analytical["adopted_case"]]["F_about_CM"])))/np.max(abs(F)))
    print("CR unit-push rotations",tests["unit_x_through_CR"]["master_displacement_u_v_phi"][2],tests["unit_y_through_CR"]["master_displacement_u_v_phi"][2])


if __name__=="__main__":main()
