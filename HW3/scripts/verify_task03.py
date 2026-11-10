"""Independently verify analytical centres using polygon integrals and force sums."""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import shape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/Plan3/task3"
r=json.loads((OUT/"Analytical_Result.json").read_text())
p=r["parameters"];checks=[]


def check(name,ok,error=None):
    row={"check":name,"pass":bool(ok)}
    if error is not None:row["error"]=float(error)
    checks.append(row)


def ring_integrals(coords,sign):
    xy=np.array(coords);a=xy[:-1];b=xy[1:]
    c=a[:,0]*b[:,1]-b[:,0]*a[:,1]
    A=c.sum()/2
    mx=((a[:,0]+b[:,0])*c).sum()/6
    my=((a[:,1]+b[:,1])*c).sum()/6
    J=((a[:,0]**2+a[:,0]*b[:,0]+b[:,0]**2+a[:,1]**2+a[:,1]*b[:,1]+b[:,1]**2)*c).sum()/12
    return np.array([A,mx,my,J])*sign*np.sign(A)


def integrate(g):
    result=np.zeros(4)
    for poly in ([g] if g.geom_type=="Polygon" else g.geoms):
        result+=ring_integrals(poly.exterior.coords,1)
        for hole in poly.interiors:result+=ring_integrals(hole.coords,-1)
    return result


zones={f["properties"]["zone"]:shape(f["geometry"]) for f in json.loads((ROOT/"outputs/Plan3/task1/Floor_Zones.geojson").read_text())["features"]}
integral=(integrate(zones["ordinary_flat_slab"])*p["ordinary_mass_intensity_kN_m2"]+
          integrate(zones["separate_stair"])*p["separate_stair_mass_intensity_kN_m2"])/p["gravity_m_s2"]
M=integral[0];cm=integral[1:3]/M;I=integral[3]-M*np.dot(cm,cm)
check("polygon-integral one-storey mass",abs(M-r["mass"]["one_storey_mass_t"])<1e-8,abs(M-r["mass"]["one_storey_mass_t"]))
check("polygon-integral CM",np.max(abs(cm-r["mass"]["CM_m"]))<1e-9,np.max(abs(cm-r["mass"]["CM_m"])))
check("polygon-integral polar mass",abs(I-r["mass"]["polar_mass_moment_about_CM_t_m2"])<1e-6,abs(I-r["mass"]["polar_mass_moment_about_CM_t_m2"]))
check("five-storey sum not storey mass",abs(r["mass"]["five_storey_total_mass_t"]-p["storeys"]*M)<1e-8)
E=p["E_kN_m2"];G=E/(2*(1+p["nu"]));H=p["height_m"];kap=p["shear_factor"]
walls=r["walls"];values=[]
for w in walls:
    L=w["length_m"];t=w["thickness_m"]
    Is=t*L**3/12;Iw=L*t**3/12;A=kap*L*t
    ks=3*E*Is/(H**3+3*E*Is*H/(G*A))
    kw=3*E*Iw/(H**3+3*E*Iw*H/(G*A))
    check("shear stiffness independent formula "+w["label"],abs(ks-w["k_strong_shear_kN_m"])/ks<1e-12)
    check("shear increases flexibility "+w["label"],0<ks<w["k_strong_bending_kN_m"])
    kx,ky=(ks,kw) if w["angle_deg"]==0 else (kw,ks)
    values.append((w,kx,ky))
case=r["cases"][r["adopted_case"]];K=np.array(case["K_about_CM"]);F=np.array(case["F_about_CM"])
xx=sum(kx for w,kx,ky in values);yy=sum(ky for w,kx,ky in values)
cr=np.array([sum(ky*w["centre_m"][0] for w,kx,ky in values)/yy,sum(kx*w["centre_m"][1] for w,kx,ky in values)/xx])
direct=np.array([[xx,0,sum(kx*(cm[1]-w["centre_m"][1]) for w,kx,ky in values)],
                 [0,yy,sum(ky*(w["centre_m"][0]-cm[0]) for w,kx,ky in values)],
                 [0,0,sum(kx*(w["centre_m"][1]-cm[1])**2+ky*(w["centre_m"][0]-cm[0])**2 for w,kx,ky in values)]])
direct[2,0]=direct[0,2];direct[2,1]=direct[1,2]
check("independent scalar-sum K",np.max(abs(direct-K))/np.max(abs(K))<1e-12)
check("weighted-position CR",np.max(abs(cr-case["CR_m"]))<1e-9,np.max(abs(cr-case["CR_m"])))
check("flexibility CR",np.max(abs(cr-case["CR_from_flexibility_m"]))<1e-9)
check("symmetric K",np.max(abs(K-K.T))<1e-8)
check("positive-definite K",np.all(np.linalg.eigvalsh(K)>0))
check("K F identity",np.max(abs(K@F-np.eye(3)))<1e-10)
B=np.array([[1,0,cr[1]-cm[1]],[0,1,cm[0]-cr[0]],[0,0,1]])
shift=B.T@K@B
check("coordinate shift matches K at CR",np.max(abs(shift-np.array(case["K_about_CR"])))/np.max(abs(K))<1e-12)
check("zero coupling at CR",np.max(abs(shift[:2,2]))/np.max(abs(K))<1e-12)
for direction,load in (("x",[1,0,-(cr[1]-cm[1])]),("y",[0,1,cr[0]-cm[0]])):
    check("unit push through CR no rotation "+direction,abs((F@load)[2])<1e-12)
check("CM force rotates eccentric floor",abs(F[2,0])+abs(F[2,1])>1e-12)
q=F@np.array([0,p["design_demonstration_force_kN"],0])
fx=fy=mz=0.
saved={w["wall"]:w for w in r["demonstration_y_force"]["wall_forces"]}
for w,kx,ky in values:
    dx,dy=np.array(w["centre_m"])-cm
    wx=kx*(q[0]-dy*q[2]);wy=ky*(q[1]+dx*q[2]);fx+=wx;fy+=wy;mz+=dx*wy-dy*wx
    check("direct solve versus push-turn "+w["label"],abs(wx-saved[w["label"]]["total_x_kN"])+abs(wy-saved[w["label"]]["total_y_kN"])<1e-8)
check("demonstration horizontal x closure",abs(fx)<1e-8,abs(fx))
check("demonstration horizontal y closure",abs(fy-p["design_demonstration_force_kN"])<1e-8,abs(fy-p["design_demonstration_force_kN"]))
check("demonstration moment closure about CM",abs(mz)<1e-8,abs(mz))
result={"passed":sum(c["pass"] for c in checks),"total":len(checks),"checks":checks,
        "independent_polygon_CM_m":cm.tolist(),"independent_weighted_CR_m":cr.tolist(),
        "scope":"Analytical consistency and independent integration only; OpenSees agreement not yet checked."}
(ROOT/"records/Task3_Verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(f"Task 3 independent verification {result['passed']}/{result['total']}")
if result["passed"]!=result["total"]:raise SystemExit(1)
