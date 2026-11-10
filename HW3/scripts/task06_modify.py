"""Optimise two inward wall thicknesses, then rebuild hand and OpenSees models."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import least_squares
from shapely.geometry import box,shape
import openseespy.opensees as ops
from task03_centres import stiffness_case
from task04_opensees import build,solve

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def recalc(w,p):
    L=w["length_m"];t=w["thickness_m"];E=p["E_kN_m2"];G=E/(2*(1+p["nu"]));H=p["height_m"]
    A=L*t;Av=p["shear_factor"]*A;Is=t*L**3/12;Iw=L*t**3/12
    kb=3*E*Is/H**3;kwb=3*E*Iw/H**3
    w.update(A_m2=A,Av_m2=Av,I_strong_m4=Is,I_weak_m4=Iw,
             k_strong_bending_kN_m=kb,k_weak_bending_kN_m=kwb,
             k_strong_shear_kN_m=1/(1/kb+H/(G*Av)),k_weak_shear_kN_m=1/(1/kwb+H/(G*Av)),
             shear_flexibility_fraction=(H/(G*Av))/(1/kb+H/(G*Av)))


def changed_walls(base,thickness,p,config):
    walls=copy.deepcopy(base)
    for label,t in zip(config["changed_walls"],thickness):
        w=next(w for w in walls if w["label"]==label)
        old=w["thickness_m"]
        if label=="T9" and w["angle_deg"]==90:w["centre_m"][0]+=(t-old)/2
        elif label=="T10" and w["angle_deg"]==0:w["centre_m"][1]+=(t-old)/2
        else:raise ValueError("Growth rule is defined only for T9/T10 and must match their directions")
        w["thickness_m"]=float(t);recalc(w,p)
    return walls


def footprint(w):
    x,y=w["centre_m"];L=w["length_m"];t=w["thickness_m"]
    width,height=(L,t) if w["angle_deg"]==0 else (t,L)
    return box(x-width/2,y-height/2,x+width/2,y+height/2)


def geometry_checks(base,after,config,element_record):
    zones={f["properties"]["zone"]:shape(f["geometry"]) for f in load(ROOT/"outputs/Plan3/task1/Floor_Zones.geojson")["features"]}
    forbidden=zones["voids"].union(zones["separate_stair"])
    columns=[]
    for e in element_record["elements"]:
        if e["class"]=="column":
            x,y=e["centre_m"];a,b=np.array(e["size_mm"])/1000
            columns.append((e["labels"][0],box(x-a/2,y-b/2,x+a/2,y+b/2)))
    records=[];tol=config["geometry_area_tolerance_m2"]
    for w in after:
        if w["label"] not in config["changed_walls"]:continue
        g=footprint(w);outside=g.difference(zones["gross"]).area
        exclusions=g.intersection(forbidden).area
        clashes=[{"column":name,"area_m2":g.intersection(c).area} for name,c in columns if g.intersection(c).area>tol]
        new_wall_clashes=[]
        original=next(b for b in base if b["label"]==w["label"])
        for other in after:
            if other["label"]==w["label"]:continue
            old_other=next(b for b in base if b["label"]==other["label"])
            new_area=g.intersection(footprint(other)).area
            old_area=footprint(original).intersection(footprint(old_other)).area
            if new_area>tol and old_area<=tol:new_wall_clashes.append({"wall":other["label"],"area_m2":new_area})
        records.append({"wall":w["label"],"outside_floor_m2":outside,"overlap_void_or_stair_m2":exclusions,
                        "column_clashes":clashes,"new_wall_clashes":new_wall_clashes,
                        "passed":outside<=tol and exclusions<=tol and not clashes and not new_wall_clashes})
    return records


def modal(walls,cm,p,mass):
    hand=stiffness_case(walls,cm,True,True);K=np.array(hand["K_about_CM"])
    M=mass["one_storey_mass_t"];I=mass["polar_mass_moment_about_CM_t_m2"]
    matrix=np.diag([M,M,I]);values,vectors=eigh(K,matrix)
    modes=[{"mode":i+1,"omega_squared_rad2_s2":float(lam),"period_s":float(2*np.pi/np.sqrt(lam)),
            "mass_normalized_shape_u_v_phi":vectors[:,i].tolist(),"torsional_mass_fraction":float(I*vectors[2,i]**2)} for i,lam in enumerate(values)]
    build(walls,cm,p)
    ops.mass(1,M,M,0.,0.,0.,I)
    solver_values=list(map(float,ops.eigen("-fullGenLapack",3)))
    solver_modes=[]
    for i,lam in enumerate(solver_values):
        if not (np.isfinite(lam) and lam>0):raise ValueError("Invalid OpenSees eigenvalue")
        solver_modes.append({"mode":i+1,"omega_squared_rad2_s2":lam,"period_s":float(2*np.pi/np.sqrt(lam)),
                             "master_shape_u_v_phi":[float(ops.nodeEigenvector(1,i+1,d)) for d in (1,2,6)]})
    # Characteristic uncoupled scales are not the actual modes of the eccentric floor.
    J=np.array(hand["K_about_CR"])[2,2]
    tx=2*np.pi*np.sqrt(M/K[0,0]);ty=2*np.pi*np.sqrt(M/K[1,1]);tt=2*np.pi*np.sqrt(I/J)
    torsional=max(modes,key=lambda m:m["torsional_mass_fraction"])
    return {"mass_matrix_about_CM":matrix.tolist(),"coupled_analytical_modes":modes,"opensees_modes":solver_modes,
            "torsion_dominant_mode":torsional["mode"],"characteristic_uncoupled_periods_s":{"Tx":float(tx),"Ty":float(ty),"Ttheta":float(tt)},
            "characteristic_ratio_Ttheta_Tx":float(tt/tx),"characteristic_ratio_Ttheta_Ty":float(tt/ty),
            "characteristic_note":"Uses I about CM and torsional stiffness about CR as uncoupled scales; actual coupled modes above are authoritative before alignment."}


def analyse_layout(walls,cm,p,mass):
    analytical=stiffness_case(walls,cm,True,True)
    units=[solve(walls,cm,p,unit) for unit in np.eye(3)]
    F=np.array([u["master_displacement_u_v_phi"] for u in units]).T
    cr=np.array([cm[0]-F[2,1]/F[2,2],cm[1]+F[2,0]/F[2,2]])
    force=p["design_demonstration_force_kN"]
    loads={"x":solve(walls,cm,p,[force,0,0]),"y":solve(walls,cm,p,[0,force,0])}
    return {"analytical":analytical,"solver_F_about_CM":F.tolist(),"solver_CR_m":cr.tolist(),
            "solver_eccentricity_m":float(np.linalg.norm(cr-cm)),"unit_cases":units,"loads":loads,
            "modal":modal(walls,cm,p,mass)}


def force_rows(layout,walls,cm,name):
    K=np.array(layout["analytical"]["K_about_CM"]);cr=np.array(layout["solver_CR_m"])
    J=np.array(layout["analytical"]["K_about_CR"])[2,2]
    result=[]
    for direction,c in layout["loads"].items():
        force=c["load_at_CM_Px_Py_Mz"][0 if direction=="x" else 1]
        e_direction=cm[1]-cr[1] if direction=="x" else cm[0]-cr[0]
        denominator=K[0,0] if direction=="x" else K[1,1]
        rt2=J/denominator
        for w,response in zip(walls,c["walls"]):
            ks=w["k_strong_shear_kN_m"];kw=w["k_weak_shear_kN_m"]
            kx,ky=(ks,kw) if w["angle_deg"]==0 else (kw,ks)
            k=kx if direction=="x" else ky
            d=w["centre_m"][1]-cr[1] if direction=="x" else w["centre_m"][0]-cr[0]
            share=k/denominator;direct=share*force
            total=response["resisting_demand_fx_kN"] if direction=="x" else response["resisting_demand_fy_kN"]
            result.append({"layout":name,"force_direction":direction,"wall":w["label"],"direct_share":share,
                           "direct_force_kN":direct,"total_aligned_force_kN":total,"torsional_increment_kN":total-direct,
                           "signed_perpendicular_e_m":float(e_direction),"signed_wall_arm_m":float(d),"torsional_radius_squared_m2":float(rt2),
                           "analytical_amplification":float(1+e_direction*d/rt2),"observed_amplification":total/direct})
    return result


def main():
    out=ROOT/"outputs/Plan3/task6";out.mkdir(parents=True,exist_ok=True)
    baseline_path=ROOT/"outputs/Plan3/task3/Analytical_Result.json"
    baseline=load(baseline_path);config=load(ROOT/"params_modification.json")
    p=baseline["parameters"];cm=np.array(baseline["mass"]["CM_m"]);base=baseline["walls"]
    if not config["mass_layout_fixed"]:raise ValueError("This design route keeps mass fixed by assignment")
    trace=[]
    def residual(thickness):
        candidate=changed_walls(base,thickness,p,config)
        case=stiffness_case(candidate,cm,True,True)
        diff=np.array(case["CR_m"])-cm
        trace.append({"evaluation":len(trace)+1,"thicknesses_m":list(map(float,thickness)),"CR_m":case["CR_m"],"eccentricity_m":float(np.linalg.norm(diff))})
        return diff
    fit=least_squares(residual,config["initial_thickness_m"],bounds=(config["lower_thickness_m"],config["upper_thickness_m"]),xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=config["max_function_evaluations"])
    (out/"Optimisation_Trajectory.json").write_text(json.dumps({"evaluations":trace,"success":bool(fit.success),"message":str(fit.message),"nfev":fit.nfev},indent=2),encoding="utf-8")
    if not fit.success or np.linalg.norm(fit.fun)>config["target_eccentricity_m"]:
        raise RuntimeError("Design did not meet frozen target; retain trajectory and revise openly")
    ideal=changed_walls(base,fit.x,p,config)
    rounded_t=np.round(fit.x/config["rounding_grid_m"])*config["rounding_grid_m"]
    rounded=changed_walls(base,rounded_t,p,config)
    geo=load(ROOT/p["element_record"])
    audits={"ideal":geometry_checks(base,ideal,config,geo),"rounded":geometry_checks(base,rounded,config,geo)}
    if not all(row["passed"] for rows in audits.values() for row in rows):
        (out/"Failed_Geometry_Audit.json").write_text(json.dumps(audits,indent=2),encoding="utf-8")
        raise RuntimeError("Modified walls violate frozen geometry constraints")
    layouts={"before":analyse_layout(base,cm,p,baseline["mass"]),"ideal_aligned":analyse_layout(ideal,cm,p,baseline["mass"]),"rounded_5mm":analyse_layout(rounded,cm,p,baseline["mass"])}
    changes=[]
    for label in config["changed_walls"]:
        old=next(w for w in base if w["label"]==label);new=next(w for w in ideal if w["label"]==label);rnd=next(w for w in rounded if w["label"]==label)
        volume=p["height_m"]*old["length_m"]*(new["thickness_m"]-old["thickness_m"])
        changes.append({"wall":label,"original_thickness_m":old["thickness_m"],"ideal_thickness_m":new["thickness_m"],"rounded_thickness_m":rnd["thickness_m"],
                        "old_centre_m":old["centre_m"],"new_centre_m":new["centre_m"],"centre_shift_m":(np.array(new["centre_m"])-old["centre_m"]).tolist(),
                        "added_concrete_m3_per_storey":volume,"added_dead_weight_kN_per_storey":volume*config["concrete_unit_weight_kN_m3"]})
    forces=[]
    for name,walls in (("before",base),("ideal_aligned",ideal),("rounded_5mm",rounded)):
        forces.extend(force_rows(layouts[name],walls,cm,name))
    result={"status":p["selection_status"],"baseline_sha256":hashlib.sha256(baseline_path.read_bytes()).hexdigest(),"config":config,
            "fixed_mass":baseline["mass"],"changes":changes,"walls_before":base,"walls_ideal":ideal,"walls_rounded":rounded,
            "layouts":layouts,"geometry_audits":audits,"force_amplification_rows":forces,
            "added_weight_note":"Reported separately; not added to the fixed prescribed floor mass in this exercise.","solver_version":ops.version()}
    (out/"Modification_Result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (out/"Force_Amplification_Comparison.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(forces[0]));writer.writeheader();writer.writerows(forces)
    print("Ideal thicknesses (m):",fit.x,"rounded:",rounded_t)
    for name,layout in layouts.items():
        print(name,"CR",layout["solver_CR_m"],"e",layout["solver_eccentricity_m"],"torsion-dominant mode",layout["modal"]["torsion_dominant_mode"])
        print("periods",[m["period_s"] for m in layout["modal"]["opensees_modes"]])


if __name__=="__main__":main()
