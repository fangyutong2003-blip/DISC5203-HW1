"""Write design/interpretation reports and figures from verified numerical outputs."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from shapely.geometry import shape

ROOT=Path(__file__).resolve().parents[1]


def wall_patch(ax,w,**kwargs):
    x,y=w["centre_m"];L=w["length_m"];t=w["thickness_m"]
    width,height=(L,t) if w["angle_deg"]==0 else (t,L)
    ax.add_patch(Rectangle((x-width/2,y-height/2),width,height,**kwargs))


def main():
    out=ROOT/"outputs/Plan3/task6"
    r=json.loads((out/"Modification_Result.json").read_text())
    v=json.loads((ROOT/"records/Task6_7_Verification.json").read_text())
    b=json.loads((ROOT/"outputs/Plan3/task3/Analytical_Result.json").read_text())
    cm=r["fixed_mass"]["CM_m"];layouts=r["layouts"];rows=r["force_amplification_rows"]
    before=layouts["before"];after=layouts["ideal_aligned"];rounded=layouts["rounded_5mm"]
    volume=sum(c["added_concrete_m3_per_storey"] for c in r["changes"])
    weight=sum(c["added_dead_weight_kN_per_storey"] for c in r["changes"])
    extra_mass=weight/b["parameters"]["gravity_m_s2"]
    text=["# HW3 Tasks 6 and 7 - Aligning CM and CR by wall modification","",
          "Student: Fangyutong | ID: 21353319 | Floor Plan 3","",
          "Status: verified modification of the declared provisional common-geometry model. Task 2's formal experiment-control limitations and Task 8 remain open. This is a mathematical design proposal, not a construction design or student-signed hand prediction.","",
          "## 1. Frozen design intent and constraints","",
          "The [pre-solve design briefing](records/Task_06_PreSolve_Design_Briefing.md) and [modification parameters](params_modification.json) were committed before optimisation. Only T9 and T10 thicknesses may increase (0.25 to 1.00 m). Main lengths, directions, columns, voids, S1 and the mass layout remain fixed. T9 grows inward from its exterior left face; T10 grows upward from its exterior bottom face. Their axes therefore move by half the thickness increase, a declared geometric rule rather than a reader edit.","",
          "These locations were chosen because CR initially lies right and above CM. Increasing y stiffness at the left-side T9 and x stiffness at the bottom-side T10 should pull CR left/down. Both strong and weak rectangular-wall stiffnesses and shear flexibility are recalculated at every step. No columns or architectural grid lines are relocated, and no new wall is inserted through the core openings.","",
          "## 2. Modification and cost","",
          "| Wall | Original thickness (mm) | Ideal thickness (mm) | 5 mm rounded (mm) | Centre shift dx,dy (m) | Added concrete per storey (m3) |",
          "|---|---:|---:|---:|---|---:|"]
    for c in r["changes"]:
        dx,dy=c["centre_shift_m"]
        text.append(f"| {c['wall']} | {1000*c['original_thickness_m']:.1f} | {1000*c['ideal_thickness_m']:.6f} | {1000*c['rounded_thickness_m']:.1f} | ({dx:.6f}, {dy:.6f}) | {c['added_concrete_m3_per_storey']:.6f} |")
    text += ["",f"The ideal proposal adds {volume:.6f} m3 concrete and {weight:.6f} kN dead weight per storey (25 kN/m3). That is approximately {extra_mass:.6f} t, or {100*extra_mass/r['fixed_mass']['one_storey_mass_t']:.2f}% of the prescribed equivalent floor mass. This increase is quantified separately and is **not** added to the fixed mass in the exercise. A real design must revisit the additional mass, gravity/foundation loads, connections, reinforcement and architectural clearances.","",
             "All proposed main rectangles remain inside the retained floor and avoid O1/O2, S1 and existing columns; no new main-wall overlap is introduced. See the saved geometry audits in [Modification_Result.json](outputs/Plan3/task6/Modification_Result.json). These checks address the available image-derived geometry, not unprovided architectural/reinforcement details.","",
             "![Changed walls and centre alignment](outputs/Plan3/task6/Modified_Walls_and_Centres.png)","",
             "## 3. CM/CR before and after","",
             f"The unchanged CM is ({cm[0]:.6f}, {cm[1]:.6f}) m; one-storey mass is {r['fixed_mass']['one_storey_mass_t']:.6f} t. All models use E=30e6 kN/m2, nu=0.2, H=3 m, both principal bending axes and shear, 12 main-wall Timoshenko cantilevers, zero intrinsic vertical wall torsion, fixed bases and an explicit Transformation rigid diaphragm. No lateral columns or cracking are introduced.","",
             "| Layout | Hand CR x,y (m) | OpenSees CR x,y (m) | Eccentricity (m) | Rotation under 100 kN x (rad) | Rotation under 100 kN y (rad) |",
             "|---|---|---|---:|---:|---:|"]
    for name,l in layouts.items():
        hx,hy=l["analytical"]["CR_m"];sx,sy=l["solver_CR_m"]
        text.append(f"| {name} | ({hx:.6f}, {hy:.6f}) | ({sx:.6f}, {sy:.6f}) | {l['solver_eccentricity_m']:.9g} | {l['loads']['x']['master_displacement_u_v_phi'][2]:.6e} | {l['loads']['y']['master_displacement_u_v_phi'][2]:.6e} |")
    text += ["",f"The ideal target e<=1e-6 m is met. The 5 mm-rounded proposal leaves e={rounded['solver_eccentricity_m']*1000:.3f} mm rather than claiming exact coincidence after rounding. Numerical alignment does not imply millimetre accuracy of the source image. [Optimisation_Trajectory.json](outputs/Plan3/task6/Optimisation_Trajectory.json) preserves all actual residual evaluations and termination status.","",
             "## 4. Why the forces change","",
             "The load tests are separately assumed 100 kN forces in x and y at CM, not code earthquake design demands. The signed torque about CR is T=(xm-xr)Fy-(ym-yr)Fx. The maximum magnitude envelope is e*F only when the force is perpendicular to the eccentricity vector.","",
             "For a y force: f_i,dir=(ky_i/Kyy)F, f_i,turn=ky_i*(x_i-xr)*T/J, and factor=1+(xm-xr)*(x_i-xr)/r_ty^2 with r_ty^2=J/Kyy. For an x force the factor is 1+(ym-yr)*(y_i-yr)/r_tx^2 with r_tx^2=J/Kxx. Here J is floor torsional stiffness about CR, not an individual wall's section torsion constant. The brief's radius-only denominator is dimensionally inconsistent; a squared radius is required. The wall stiffness factor cannot be omitted from the force term.","",
             "| Force | Most amplified original wall(s) | Original factor | Increase over direct share |","|---|---|---:|---:|"]
    for d in ("x","y"):
        original=[row for row in rows if row["layout"]=="before" and row["force_direction"]==d]
        factor=max(row["observed_amplification"] for row in original)
        names=[row["wall"] for row in original if abs(row["observed_amplification"]-factor)<1e-8]
        text.append(f"| {d} | {', '.join(names)} | {factor:.6f} | {100*(factor-1):.3f}% |")
    text += ["","This identifies the plan-specific penalty: the low-y walls T10/T11 are amplified for the x push; low-x T9 is amplified for the y push. A negative torsional increment can instead relieve another wall. After ideal alignment all aligned-force factors equal 1 and the cross-direction turn vanishes.","",
             "### Peak aligned wall force","","| Assumed force | Peak before (wall, kN) | Peak ideal after (wall, kN) | Change |","|---|---|---|---:|"]
    for d in ("x","y"):
        peak=lambda name:max([row for row in rows if row["layout"]==name and row["force_direction"]==d],key=lambda row:abs(row["total_aligned_force_kN"]))
        old,new=peak("before"),peak("ideal_aligned")
        change=100*(abs(new["total_aligned_force_kN"])/abs(old["total_aligned_force_kN"])-1)
        text.append(f"| {d}, 100 kN | {old['wall']}, {old['total_aligned_force_kN']:.6f} | {new['wall']}, {new['total_aligned_force_kN']:.6f} | {change:+.3f}% |")
    text += ["","The reduction in the peaks combines torsion removal **and** stiffness redistribution. It must not all be attributed to removing e. The thickened walls attract more direct load; not every wall demand decreases. [Force_Amplification_Comparison.csv](outputs/Plan3/task6/Force_Amplification_Comparison.csv) reports each wall's direct share, torsional increment, final force, squared torsional radius and analytical/observed factors for both directions and all three layouts.","",
             "![Forces and actual coupled periods](outputs/Plan3/task6/Forces_and_Periods.png)","",
             "## 5. Modes and period ratios","",
             "The mass matrix is diag(M,M,I_CM), identical in all layouts. The analytical generalized eigenproblem and actual OpenSees eigenanalysis with mass at the diaphragm master are both retained. The official [eigen command documentation](https://openseespydoc.readthedocs.io/en/latest/src/eigen.html) explains the fullGenLapack option used to obtain all three inertial modes. These are one-storey fixed-base subsystem periods, not five-storey building periods.","",
             "| Layout | Coupled periods T1,T2,T3 (s) | Torsion-dominant mode | Rotational mass fraction of that mode | Characteristic Ttheta/Tx | Characteristic Ttheta/Ty |",
             "|---|---|---:|---:|---:|---:|"]
    for name,l in layouts.items():
        m=l["modal"];periods=[v["period_s"] for v in m["opensees_modes"]]
        torsion=max(m["coupled_analytical_modes"],key=lambda v:v["torsional_mass_fraction"])
        text.append(f"| {name} | {', '.join(f'{t:.6f}' for t in periods)} | {torsion['mode']} | {torsion['torsional_mass_fraction']:.6f} | {m['characteristic_ratio_Ttheta_Tx']:.6f} | {m['characteristic_ratio_Ttheta_Ty']:.6f} |")
    text += ["","The actual torsion-dominant mode is mode 3 before and after this proposal; it was not the first mode on this plan. Its original rotational mass fraction is approximately 0.667 and becomes 1 after ideal alignment: the floor's translational and rotational motions decouple. Aligning centres does not guarantee a particular mode ordering. Characteristic ratios use Ttheta=2*pi*sqrt(I_CM/J), Tx=2*pi*sqrt(M/Kxx), Ty=2*pi*sqrt(M/Kyy); for the eccentric floor they are labelled scales, not replacements for the actual coupled modes.","",
             "## 6. Scope, cost and the vision link","",
             "CM=CR removes the eccentric torque for a pure horizontal force on this uniform rigid floor. It does not remove torsional resistance or the torsional natural mode. It does not make a building immune to accidental eccentricity, cracking, mass/stiffness changes over height, nonuniform or rotational ground motion, or different storey layouts. A wall-position or size error in extraction would change K and CR and therefore change this numerical design target. This design is conditional on the retained image-derived rectangles and modelling assumptions; final reader-promotion and independent-plan evidence are still separate requirements.","",
             f"Added concrete and its {weight:.3f} kN per-storey weight are the principal quantified cost here. The fixed-mass instruction is a controlled exercise assumption. A practical redesign that includes this new mass must recalculate CM and repeat the alignment, rather than claiming the fixed-mass optimum is automatically a final building design.","",
             "## 7. Verification and reproduction","",
             f"{v['passed']}/{v['total']} independent checks passed. See [Task6_7_Verification.json](records/Task6_7_Verification.json). Checks cover preserved baseline, mass, lengths, growth faces, geometry/clashes, independently assembled K, hand/model F and CR, static equilibrium, signed amplification, modal eigenvalues/shapes and ideal zero rotation. All baseline outputs remain intact.","",
             "```text","python HW3/scripts/task06_modify.py","python HW3/scripts/verify_task06.py","python HW3/scripts/write_task06_report.py","```","",
             "The code is parameterised by saved inputs; the T9/T10 growth choice is a disclosed Plan 3 design decision, not a general automatically selected wall strategy. [Iteration log](records/Iteration_Log.md) and [readable Git history](records/Git_History.md) retain the chronology."]
    (ROOT/"HW3_Task_06_07_Modification_Report.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    zones={f["properties"]["zone"]:shape(f["geometry"]) for f in json.loads((ROOT/"outputs/Plan3/task1/Floor_Zones.geojson").read_text())["features"]}
    fig,(ax,bx)=plt.subplots(1,2,figsize=(12,10),gridspec_kw={"width_ratios":[1,1.2]})
    for axis in (ax,bx):
        axis.fill(*zones["gross"].exterior.xy,facecolor="#f3f5f7",edgecolor="black")
        for name in ("voids","separate_stair"):
            g=zones[name]
            for poly in ([g] if g.geom_type=="Polygon" else g.geoms):axis.fill(*poly.exterior.xy,facecolor="white",edgecolor="orange",hatch="xx" if name=="voids" else "//")
        for w in r["walls_before"]:
            if w["label"] not in r["config"]["changed_walls"]:wall_patch(axis,w,facecolor="#8b959e",edgecolor="#525b63")
        for w in r["walls_ideal"]:
            if w["label"] in r["config"]["changed_walls"]:wall_patch(axis,w,facecolor="#96c1dd",edgecolor="#21618c",lw=1.8)
        for w in r["walls_before"]:
            if w["label"] in r["config"]["changed_walls"]:wall_patch(axis,w,facecolor="none",edgecolor="#b34236",ls="--",lw=1.8)
        axis.set(aspect="equal",xlabel="x (m)",ylabel="y (m)")
    ax.scatter(*cm,s=150,marker="+",c="black",label="Fixed CM")
    ax.scatter(*before["solver_CR_m"],s=75,facecolors="none",edgecolors="purple",label="Original CR")
    ax.scatter(*after["solver_CR_m"],s=140,facecolors="none",edgecolors="green",label="Ideal CR = CM")
    ax.plot([cm[0],before["solver_CR_m"][0]],[cm[1],before["solver_CR_m"][1]],"--",color="purple")
    ax.legend(loc="upper left",fontsize=8);ax.set_title("Plan 3: fixed mass, changed T9/T10")
    bx.set_xlim(-.15,4.9);bx.set_ylim(-.25,2.4);bx.set_title("Inward thickening: original dashed, ideal blue")
    for c in r["changes"]:
        x,y=c["new_centre_m"]
        bx.annotate(f"{c['wall']}\n250 -> {1000*c['ideal_thickness_m']:.1f} mm",(x,y),xytext=(15,35),textcoords="offset points",arrowprops={"arrowstyle":"->"},fontsize=10)
    fig.suptitle(f"Ideal e ~ 0; 5 mm-rounded thicknesses give e = {rounded['solver_eccentricity_m']*1000:.2f} mm",fontsize=12)
    fig.tight_layout();fig.savefig(out/"Modified_Walls_and_Centres.png",dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(16,8))
    labels=[w["label"] for w in r["walls_before"]];ix=np.arange(len(labels))
    for axis,d in zip(axes[:2],("x","y")):
        old={v["wall"]:v for v in rows if v["layout"]=="before" and v["force_direction"]==d}
        new={v["wall"]:v for v in rows if v["layout"]=="ideal_aligned" and v["force_direction"]==d}
        axis.barh(ix-.18,[old[n]["total_aligned_force_kN"] for n in labels],height=.36,label="Before")
        axis.barh(ix+.18,[new[n]["total_aligned_force_kN"] for n in labels],height=.36,label="Ideal aligned")
        axis.set(yticks=ix,yticklabels=labels,xlabel=f"Global {d} demand (kN)",title=f"100 kN {d} force at CM")
        axis.legend(fontsize=8)
    axis=axes[2];modes=np.arange(1,4)
    axis.bar(modes-.18,[v["period_s"] for v in before["modal"]["opensees_modes"]],width=.36,label="Before")
    axis.bar(modes+.18,[v["period_s"] for v in after["modal"]["opensees_modes"]],width=.36,label="Ideal aligned")
    axis.set(xticks=modes,xlabel="Actual coupled mode",ylabel="Period (s)",title="Fixed-base one-storey periods")
    axis.legend(fontsize=8);fig.tight_layout();fig.savefig(out/"Forces_and_Periods.png",dpi=160);plt.close(fig)
    import re
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)",(ROOT/"HW3_Task_06_07_Modification_Report.md").read_text()):
        if not target.startswith(("https:","http:")) and not (ROOT/target).exists():raise FileNotFoundError(target)
    print("Wrote Tasks 6/7 report and figures; report links valid")


if __name__=="__main__":main()
