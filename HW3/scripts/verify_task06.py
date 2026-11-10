"""Verify modification outputs independently of optimisation and model builders."""
import hashlib
import json
from pathlib import Path
import numpy as np
from shapely.geometry import box,shape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/Plan3/task6"
r=json.loads((OUT/"Modification_Result.json").read_text());checks=[]
base_path=ROOT/"outputs/Plan3/task3/Analytical_Result.json"
base=json.loads(base_path.read_text());p=base["parameters"];cm=np.array(base["mass"]["CM_m"])


def check(name,ok,error=None):
    v={"check":name,"pass":bool(ok)}
    if error is not None:v["error"]=float(error)
    checks.append(v)


def footprint(w):
    x,y=w["centre_m"];L=w["length_m"];t=w["thickness_m"]
    ww,hh=(L,t) if w["angle_deg"]==0 else (t,L)
    return box(x-ww/2,y-hh/2,x+ww/2,y+hh/2)


def matrix(walls):
    K=np.zeros((3,3));E=p["E_kN_m2"];G=E/(2*(1+p["nu"]));H=p["height_m"]
    for w in walls:
        L=w["length_m"];t=w["thickness_m"];Av=p["shear_factor"]*L*t
        strong=3*E*(t*L**3/12)/(H**3+3*E*(t*L**3/12)*H/(G*Av))
        weak=3*E*(L*t**3/12)/(H**3+3*E*(L*t**3/12)*H/(G*Av))
        kx,ky=(strong,weak) if w["angle_deg"]==0 else (weak,strong)
        x,y=np.array(w["centre_m"])-cm
        K[0,0]+=kx;K[1,1]+=ky;K[0,2]-=kx*y;K[1,2]+=ky*x;K[2,2]+=kx*y*y+ky*x*x
    K[2,0]=K[0,2];K[2,1]=K[1,2]
    return K


check("baseline hash unchanged",hashlib.sha256(base_path.read_bytes()).hexdigest()==r["baseline_sha256"])
check("saved before walls equal baseline",r["walls_before"]==base["walls"])
check("mass record unchanged",r["fixed_mass"]==base["mass"])
zones={f["properties"]["zone"]:shape(f["geometry"]) for f in json.loads((ROOT/"outputs/Plan3/task1/Floor_Zones.geojson").read_text())["features"]}
geometry=json.loads((ROOT/p["element_record"]).read_text())
cols=[]
for e in geometry["elements"]:
    if e["class"]=="column":
        x,y=e["centre_m"];a,b=np.array(e["size_mm"])/1000;cols.append(box(x-a/2,y-b/2,x+a/2,y+b/2))
for name,walls in (("ideal",r["walls_ideal"]),("rounded",r["walls_rounded"])):
    for old,new in zip(r["walls_before"],walls):
        check(name+" unchanged length/direction "+old["label"],old["length_m"]==new["length_m"] and old["angle_deg"]==new["angle_deg"])
        if old["label"] not in r["config"]["changed_walls"]:
            check(name+" unselected wall preserved "+old["label"],old==new)
        else:
            delta=new["thickness_m"]-old["thickness_m"]
            expected=np.array(old["centre_m"])+([delta/2,0] if old["label"]=="T9" else [0,delta/2])
            check(name+" inward growth "+old["label"],np.max(abs(expected-new["centre_m"]))<1e-12)
            g=footprint(new)
            check(name+" inside floor "+old["label"],g.difference(zones["gross"]).area<=1e-6)
            check(name+" avoids void/stair "+old["label"],g.intersection(zones["voids"].union(zones["separate_stair"])).area<=1e-6)
            check(name+" avoids columns "+old["label"],all(g.intersection(c).area<=1e-6 for c in cols))
for change in r["changes"]:
    old=next(w for w in r["walls_before"] if w["label"]==change["wall"])
    expected=p["height_m"]*old["length_m"]*(change["ideal_thickness_m"]-old["thickness_m"])
    check("added volume "+change["wall"],abs(expected-change["added_concrete_m3_per_storey"])<1e-12)
    check("added weight "+change["wall"],abs(expected*r["config"]["concrete_unit_weight_kN_m3"]-change["added_dead_weight_kN_per_storey"])<1e-10)
mass=np.diag([base["mass"]["one_storey_mass_t"]]*2+[base["mass"]["polar_mass_moment_about_CM_t_m2"]])
for name,walls in (("before",r["walls_before"]),("ideal_aligned",r["walls_ideal"]),("rounded_5mm",r["walls_rounded"])):
    l=r["layouts"][name];K=matrix(walls);F=np.array(l["solver_F_about_CM"])
    cr=np.array([cm[0]+K[1,2]/K[1,1],cm[1]-K[0,2]/K[0,0]])
    check(name+" independent K",np.max(abs(K-np.array(l["analytical"]["K_about_CM"])))/np.max(abs(K))<1e-10)
    check(name+" positive stiffness",np.all(np.linalg.eigvalsh(K)>0))
    check(name+" hand/model F",np.max(abs(np.linalg.inv(K)-F))/np.max(abs(F))<1e-6)
    check(name+" hand/model CR",np.max(abs(cr-l["solver_CR_m"]))<1e-5)
    check(name+" unchanged mass matrix",np.max(abs(mass-l["modal"]["mass_matrix_about_CM"]))<1e-8)
    for direction,c in l["loads"].items():
        q=np.array(c["master_displacement_u_v_phi"]);force=np.array(c["load_at_CM_Px_Py_Mz"])
        check(name+direction+" solve matches K",np.max(abs(q-np.linalg.solve(K,force)))<1e-11)
        reaction=np.zeros(3)
        for w in c["walls"]:
            R=w["base_reaction_global"];x,y=np.array(w["centre_m"])-cm
            reaction+=np.array([R[0],R[1],R[5]+x*R[1]-y*R[0]])
        check(name+direction+" global equilibrium",np.max(abs(reaction+force))<1e-7)
        rows=[v for v in r["force_amplification_rows"] if v["layout"]==name and v["force_direction"]==direction]
        error=max(abs(v["observed_amplification"]-v["analytical_amplification"]) for v in rows)
        check(name+direction+" signed amplification formula",error<1e-8,error)
    for h,s in zip(l["modal"]["coupled_analytical_modes"],l["modal"]["opensees_modes"]):
        lam=h["omega_squared_rad2_s2"];v=np.array(h["mass_normalized_shape_u_v_phi"]);sv=np.array(s["master_shape_u_v_phi"])
        check(name+f" eigenvalue {h['mode']}",abs(lam-s["omega_squared_rad2_s2"])/lam<1e-6)
        check(name+f" modal residual {h['mode']}",np.linalg.norm(K@v-lam*mass@v)/(np.linalg.norm(K)*np.linalg.norm(v))<1e-9)
        mac=(v@mass@sv)**2/((v@mass@v)*(sv@mass@sv))
        check(name+f" model modal shape {h['mode']}",abs(mac-1)<1e-6)
ideal=r["layouts"]["ideal_aligned"]
check("ideal target CM=CR",ideal["solver_eccentricity_m"]<=r["config"]["target_eccentricity_m"])
for direction in ("x","y"):
    check("aligned CM force no turn "+direction,abs(ideal["loads"][direction]["master_displacement_u_v_phi"][2])<1e-12)
    check("aligned all wall factors one "+direction,all(abs(v["observed_amplification"]-1)<1e-8 for v in r["force_amplification_rows"] if v["layout"]=="ideal_aligned" and v["force_direction"]==direction))
check("rounded design reduces eccentricity",r["layouts"]["rounded_5mm"]["solver_eccentricity_m"]<r["layouts"]["before"]["solver_eccentricity_m"])
result={"passed":sum(c["pass"] for c in checks),"total":len(checks),"checks":checks,
        "scope":"Tasks 6/7 fixed-mass modification and numerical interpretation; not a construction design or final Task 2 promotion."}
(ROOT/"records/Task6_7_Verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(f"Tasks 6/7 verification: {result['passed']}/{result['total']}")
if result["passed"]!=result["total"]:
    print([c for c in checks if not c["pass"]]);raise SystemExit(1)
