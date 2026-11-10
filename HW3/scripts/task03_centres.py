"""Compute signed-rectangle CM and analytical rectangular-wall diaphragm stiffness."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def assemble(walls,centre,shear=True,weak=True):
    K=np.zeros((3,3))
    for w in walls:
        ks=w["k_strong_shear_kN_m"] if shear else w["k_strong_bending_kN_m"]
        kw=(w["k_weak_shear_kN_m"] if shear else w["k_weak_bending_kN_m"]) if weak else 0.
        kx,ky=(ks,kw) if w["angle_deg"]==0 else (kw,ks)
        x,y=np.array(w["centre_m"])-centre
        ax=np.array([1.,0.,-y]);ay=np.array([0.,1.,x])
        K+=kx*np.outer(ax,ax)+ky*np.outer(ay,ay)
    return K


def stiffness_case(walls,cm,shear,weak):
    K=assemble(walls,np.array(cm),shear,weak)
    F=np.linalg.inv(K)
    xr=cm[0]+K[1,2]/K[1,1];yr=cm[1]-K[0,2]/K[0,0]
    fr=[cm[0]-F[2,1]/F[2,2],cm[1]+F[2,0]/F[2,2]]
    cr=[float(xr),float(yr)]
    return {"shear_included":shear,"weak_axis_included":weak,"K_about_CM":K.tolist(),
            "F_about_CM":F.tolist(),"CR_m":cr,"CR_from_flexibility_m":fr,
            "eccentricity_m":float(np.linalg.norm(np.array(cr)-cm)),
            "K_about_CR":assemble(walls,np.array(cr),shear,weak).tolist()}


def main():
    out=ROOT/"outputs/Plan3/task3";out.mkdir(parents=True,exist_ok=True)
    params=load(ROOT/"params_mechanics.json")
    geom=load(ROOT/params["element_record"]); floor=load(ROOT/params["floor_record"])
    g=params["gravity_m_s2"]; ordinary=params["ordinary_mass_intensity_kN_m2"]; stair=params["separate_stair_mass_intensity_kN_m2"]
    rectangles=[]
    for i,(x,y,w,h) in enumerate(floor["rectangles_m"]):
        rectangles.append({"zone":f"gross_R{i+1}","sign":1,"x_m":x,"y_m":y,"width_m":w,"height_m":h,"intensity_kN_m2":ordinary})
    for name,x,y,w,h in floor["exclusions_m"]:
        rectangles.append({"zone":name+"_deduct","sign":-1,"x_m":x,"y_m":y,"width_m":w,"height_m":h,"intensity_kN_m2":ordinary})
        if name=="S1":rectangles.append({"zone":"S1_separate_equivalent_mass","sign":1,"x_m":x,"y_m":y,"width_m":w,"height_m":h,"intensity_kN_m2":stair})
    for r in rectangles:
        r["signed_area_m2"]=r["sign"]*r["width_m"]*r["height_m"]
        r["centroid_x_m"]=r["x_m"]+r["width_m"]/2;r["centroid_y_m"]=r["y_m"]+r["height_m"]/2
        r["signed_mass_t"]=r["signed_area_m2"]*r["intensity_kN_m2"]/g
    M=sum(r["signed_mass_t"] for r in rectangles)
    cm=np.array([sum(r["signed_mass_t"]*r[k] for r in rectangles)/M for k in ("centroid_x_m","centroid_y_m")])
    I=sum(r["signed_mass_t"]*((r["width_m"]**2+r["height_m"]**2)/12+(r["centroid_x_m"]-cm[0])**2+(r["centroid_y_m"]-cm[1])**2) for r in rectangles)
    E=params["E_kN_m2"];G=E/(2*(1+params["nu"]));H=params["height_m"];kap=params["shear_factor"]
    walls=[]
    for e in geom["elements"]:
        if e["class"]!="wall":continue
        L=max(e["size_mm"])/1000;t=min(e["size_mm"])/1000
        A=L*t;Av=kap*A;Is=t*L**3/12;Iw=L*t**3/12
        kb=3*E*Is/H**3;kwb=3*E*Iw/H**3
        ks=1/(1/kb+H/(G*Av));kw=1/(1/kwb+H/(G*Av))
        walls.append({"label":e["labels"][0],"centre_m":e["centre_m"],"angle_deg":e["angle_deg"],
                      "length_m":L,"thickness_m":t,"A_m2":A,"Av_m2":Av,"I_strong_m4":Is,"I_weak_m4":Iw,
                      "k_strong_bending_kN_m":kb,"k_strong_shear_kN_m":ks,
                      "k_weak_bending_kN_m":kwb,"k_weak_shear_kN_m":kw,
                      "shear_flexibility_fraction":(H/(G*Av))/(H**3/(3*E*Is)+H/(G*Av))})
    cases={"matched_rectangular_shear":stiffness_case(walls,cm,True,True),
           "matched_rectangular_bending_only":stiffness_case(walls,cm,False,True),
           "brief_strong_direction_only_shear":stiffness_case(walls,cm,True,False),
           "brief_strong_direction_only_bending":stiffness_case(walls,cm,False,False)}
    adopted=cases["matched_rectangular_shear"];K=np.array(adopted["K_about_CM"]);Fmat=np.array(adopted["F_about_CM"])
    cr=np.array(adopted["CR_m"]);J=np.array(adopted["K_about_CR"])[2,2]
    force=params["design_demonstration_force_kN"];q=Fmat@np.array([0.,force,0.])
    T=(cm[0]-cr[0])*force
    force_rows=[]
    for w in walls:
        kx,ky=(w["k_strong_shear_kN_m"],w["k_weak_shear_kN_m"]) if w["angle_deg"]==0 else (w["k_weak_shear_kN_m"],w["k_strong_shear_kN_m"])
        dx,dy=np.array(w["centre_m"])-cr
        fx=-kx*dy*T/J;fy=ky/K[1,1]*force+ky*dx*T/J
        force_rows.append({"wall":w["label"],"kx_kN_m":kx,"ky_kN_m":ky,"x_minus_CR_m":dx,"y_minus_CR_m":dy,
                           "push_y_share":ky/K[1,1],"turn_y_per_unit_torque_1_m":ky*dx/J,
                           "turn_x_per_unit_torque_1_m":-kx*dy/J,"direct_y_kN":ky/K[1,1]*force,
                           "torsional_y_kN":ky*dx*T/J,"total_y_kN":fy,"total_x_kN":fx})
    mass_matrix=np.diag([M,M,I]);values,vectors=eigh(K,mass_matrix)
    modes=[{"mode":i+1,"period_s":float(2*np.pi/np.sqrt(lam)),
            "mass_normalized_shape":vectors[:,i].tolist(),"torsional_mass_fraction":float(I*vectors[2,i]**2)} for i,lam in enumerate(values)]
    report={"status":params["selection_status"],"input_sha256":{k:hashlib.sha256((ROOT/params[k]).read_bytes()).hexdigest() for k in ("element_record","floor_record")},
            "parameters":params,"mass":{"CM_m":cm.tolist(),"one_storey_mass_t":M,"five_storey_total_mass_t":M*params["storeys"],
            "polar_mass_moment_about_CM_t_m2":I,"equivalent_mass_area_m2":sum(r["signed_area_m2"] for r in rectangles),"rectangles":rectangles},
            "walls":walls,"cases":cases,"adopted_case":"matched_rectangular_shear","modes":modes,
            "demonstration_y_force":{"F_kN":force,"torque_about_CR_kN_m":float(T),"displacement_at_CM_m_m_rad":q.tolist(),
                                     "wall_forces":force_rows,"sum_wall_fx_kN":sum(r["total_x_kN"] for r in force_rows),"sum_wall_fy_kN":sum(r["total_y_kN"] for r in force_rows)}}
    (out/"Analytical_Result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    for name,rows in (("Mass_Rectangles.csv",rectangles),("Wall_Force_Shares.csv",force_rows)):
        with (out/name).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    wall_rows=[{k:v for k,v in w.items() if k!="centre_m"}|{"x_m":w["centre_m"][0],"y_m":w["centre_m"][1]} for w in walls]
    with (out/"Wall_Stiffnesses.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(wall_rows[0]));writer.writeheader();writer.writerows(wall_rows)
    text=["# HW3 Task 3 - Analytical CM, stiffness and CR","",
          "Status: provisional common-geometry baseline; formal Task 2 promotion remains pending. This is an agent-generated analytical calculation, not claimed as handwritten student work.","",
          "## Assumptions and mass","",
          "The floor reuses the retained HW1 dimension-chain rectangles including balconies. O1/O2 are voids. S1 is deducted from ordinary slab and added separately as an equivalent-horizontal mass zone, with the inherited 8.75 kN/m2 service intensity. No vertical-member self-weight is added to this prescribed uniform floor mass. Full G+Q mass is an exercise convention, not a code seismic combination.","",
          f"Net equivalent mass area = {report['mass']['equivalent_mass_area_m2']:.6f} m2. CM = ({cm[0]:.6f}, {cm[1]:.6f}) m. One-storey mass = {M:.6f} t; five-storey sum = {M*params['storeys']:.6f} t. The assignment's factor n=5 produces a total, not a per-storey mass. Polar mass moment about CM = {I:.6f} t m2.","",
          "See [signed rectangle calculation](outputs/Plan3/task3/Mass_Rectangles.csv). Positive body/balcony rectangles, negative void rectangles and a separately added S1 make the accounting explicit.","",
          "## Wall stiffness and matrix derivation","",
          "E=30e6 kN/m2, nu=0.2, G=12.5e6 kN/m2, H=3 m, Av=(5/6)Lt. Walls are cantilevers: k_b=3EI/H^3 and k_bs=1/[H^3/(3EI)+H/(GAv)]. Strong I=tL^3/12; weak I=Lt^3/12. The matched rectangular-wall baseline retains both bending directions, excludes intrinsic vertical wall torsion, columns, approximate short returns and cracking. The brief's strong-direction-only construction is reported separately as a sensitivity case.","",
          "About CM, q=(u,v,phi), a_x=(1,0,-dy), a_y=(0,1,dx). Assemble K=sum[kx outer(a_x,a_x)+ky outer(a_y,a_y)]. Thus Kxphi=-sum(kx*dy), Kyphi=sum(ky*dx). For orthogonal walls, xr=xm+Kyphi/Kyy and yr=ym-Kxphi/Kxx. From F=inv(K), xr=xm-Fphiy/Fphiphi and yr=ym+Fphix/Fphiphi. The two routes must agree.","",
          "The brief's stiffness ratio Kphix/Kphiphi has units 1/m, so it cannot be added to a coordinate. The flexibility ratios above have units m. K uses mixed translational/rotational units: its 2x2 translational block is kN/m, translation-rotation entries kN and the rotational entry kN m. Angles are radians.","",
          "[Per-wall stiffness table](outputs/Plan3/task3/Wall_Stiffnesses.csv) includes bending-only and shear-inclusive values and the shear fraction of strong-axis flexibility.","",
          "| Assumption | CR x (m) | CR y (m) | Eccentricity (m) |","|---|---:|---:|---:|"]
    text += [f"| {name} | {case['CR_m'][0]:.6f} | {case['CR_m'][1]:.6f} | {case['eccentricity_m']:.6f} |" for name,case in cases.items()]
    text += ["","### Matched baseline K about CM","","```text",np.array2string(K,precision=6,suppress_small=True),"```","",
             "### Matched baseline flexibility F about CM","","```text",np.array2string(Fmat,precision=12,suppress_small=False),"```","",
             "## Demonstration force shares","",
             f"A separately declared demonstration force Fy={force:.1f} kN acts at CM. It is an assumed linear-analysis test, not a code design demand. Torque about CR is (xm-xr)*Fy={T:.6f} kN m. In general Tz=(xm-xr)*Fy-(ym-yr)*Fx; e*F is a maximum lever-arm envelope, not the torque for every force direction.","",
             "At CR, direct y force share is ky/sum(ky), torsional y coefficient is ky*dx/J, and torsional x coefficient is -kx*dy/J. [Force-share table](outputs/Plan3/task3/Wall_Force_Shares.csv) records direct and torsional components separately. Unit-torque coefficients have units 1/m, not dimensionless percentages.","",
             "## Reproduction and verification","",
             "Run python HW3/scripts/task03_centres.py, then python HW3/scripts/verify_task03.py. The independent checker uses polygon boundary integrals, direct weighted CR and separately assembled equilibrium equations. OpenSees matching is a later stage, not asserted by this analytical report.","",
             "The [pre-solve briefing](records/Task_03_PreSolve_Briefing.md) and params_mechanics.json were committed before this calculation. Input hashes and all intermediate matrices are retained in [Analytical_Result.json](outputs/Plan3/task3/Analytical_Result.json)."]
    (ROOT/"HW3_Task_03_Analytical_Report.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from shapely.geometry import shape
    zones={f["properties"]["zone"]:shape(f["geometry"]) for f in load(ROOT/"outputs/Plan3/task1/Floor_Zones.geojson")["features"]}
    fig,(ax,bx)=plt.subplots(1,2,figsize=(12,10),gridspec_kw={"width_ratios":[1.2,1]})
    ax.fill(*zones["gross"].exterior.xy,color="#f0f3f6",edgecolor="black")
    for name in ("voids","separate_stair"):
        z=zones[name]
        for poly in ([z] if z.geom_type=="Polygon" else z.geoms):ax.fill(*poly.exterior.xy,color="white",edgecolor="orange",hatch="xx" if name=="voids" else "//")
    for w in walls:
        x,y=w["centre_m"];L=w["length_m"];t=w["thickness_m"]
        width,height=(L,t) if w["angle_deg"]==0 else (t,L)
        ax.add_patch(plt.Rectangle((x-width/2,y-height/2),width,height,color="#c74635"))
        ax.annotate(w["label"],(x,y),xytext=(4,4),textcoords="offset points",fontsize=8)
    ax.scatter(*cm,marker="+",s=180,c="black",label="CM")
    ax.scatter(*cr,marker="o",s=90,facecolors="none",edgecolors="purple",label="CR, shear included")
    ax.plot([cm[0],cr[0]],[cm[1],cr[1]],"--",color="purple",label=f"e = {adopted['eccentricity_m']:.3f} m")
    ax.set(aspect="equal",xlabel="x (m)",ylabel="y (m)",title="Provisional Plan 3 baseline: CM and CR")
    ax.legend(loc="upper left",fontsize=8)
    inds=np.arange(len(walls));bx.barh(inds-.18,[w["k_strong_bending_kN_m"]/1000 for w in walls],height=.36,label="Bending only")
    bx.barh(inds+.18,[w["k_strong_shear_kN_m"]/1000 for w in walls],height=.36,label="Bending + shear")
    bx.set(yticks=inds,yticklabels=[w["label"] for w in walls],xlabel="Strong-axis stiffness (MN/m)",title="Wall stiffness sensitivity")
    bx.legend();fig.tight_layout();fig.savefig(out/"CM_CR_and_Wall_Stiffness.png",dpi=160);plt.close(fig)
    print("CM",cm,"mass per storey",M)
    for name,c in cases.items():print(name,"CR",c["CR_m"],"e",c["eccentricity_m"])
    print("Wall force totals",report["demonstration_y_force"]["sum_wall_fx_kN"],report["demonstration_y_force"]["sum_wall_fy_kN"])


if __name__=="__main__":main()
