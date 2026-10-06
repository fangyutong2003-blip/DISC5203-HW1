"""Closed polygon allocation using the coursework 45/60/30-degree convention.

This is a geometric sensitivity model, not a stiffness or general yield-line
solution. Every adopted edge condition is exported for review. Existing HW1
geometry is retained; uncovered core area is reported as unresolved explicitly.
"""
from __future__ import annotations

import csv
import json
import math
import zipfile
import io
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPolygon, Patch
import numpy as np
from shapely.geometry import Polygon, box, mapping, LineString
from shapely.ops import unary_union

from hw2_beam_loads import BEAMS, BEAM_MAP, SEGMENTS, SUPPORTS, PANELS, distance_l1

ROOT = Path(__file__).resolve().parent
SQRT3 = math.sqrt(3.0)
PROFILE_DX = 0.01
ANGLE_SOURCE = "HW2.md, hint 04 (L04): matched 45/45; mixed 60 from fixed and 30 from simple."
# S and C are slab-edge idealisations; they do not specify beam-end releases.
EDGE_CASES = {
    "P1": {"D01":"C", "W_T1":"C", "D02":"S", "W_T2":"C", "W_T3":"C", "D06":"C", "D09":"C", "W_T4":"C", "D03":"C", "D07":"C"},
    "P2": {"D04":"C", "W_T3":"C", "D05":"S", "D06":"C", "D08":"C"},
    "P3": {"D08":"C", "D11":"S", "D12":"C", "D16":"C"},
    "P4": {"D12":"C", "W_CORE_R":"C"},
    "P5": {"W_T4":"C", "D10":"C", "D13":"S", "W_T7":"C", "D14":"C", "D15":"S", "D18":"C"},
    "P6": {"W_T8":"C", "D17":"C"},
    "P7": {"D16":"C", "D19":"S", "D20":"C", "D23":"C"},
    "P8": {"D20":"C", "D21":"C"},
    "P9": {"D18":"C", "D21":"C", "D22":"S", "D25":"C"},
}
ROOT_BEAMS = {"D01", "D03", "D04", "D07", "D10", "D23", "D24", "D25"}
ONE_WAY = {"P4", "P6", "P8"}


def polygons(geometry):
    if geometry.is_empty or geometry.area < 1e-9:
        return
    if geometry.geom_type == "Polygon":
        yield geometry
    elif hasattr(geometry, "geoms"):
        for child in geometry.geoms:
            yield from polygons(child)


def write_csv(name, rows, fields=None):
    with (ROOT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clip(vertices, a, b, c):
    """Clip a convex polygon by a*x+b*y+c <= 0."""
    if not vertices:
        return []
    result = []
    for start, end in zip(vertices, vertices[1:] + vertices[:1]):
        f = a * start[0] + b * start[1] + c
        g = a * end[0] + b * end[1] + c
        if f <= 1e-12:
            result.append(start)
        if (f < 0 < g) or (g < 0 < f):
            t = f / (f - g)
            result.append((start[0] + t*(end[0]-start[0]), start[1]+t*(end[1]-start[1])))
    return result


def affine_score(seg, x, y, weight):
    """Finite-segment L1 distance is affine inside each endpoint-defined tile."""
    def slope(value, lo, hi):
        return -1.0 if value < lo else (1.0 if value > hi else 0.0)
    a = slope(x, min(seg.x1, seg.x2), max(seg.x1, seg.x2)) / weight
    b = slope(y, min(seg.y1, seg.y2), max(seg.y1, seg.y2)) / weight
    return a, b, distance_l1(x, y, seg)/weight - a*x - b*y


def partition(panel, matched=False, tie_audit=None):
    shape = Polygon(panel["polygon"])
    segments = [SUPPORTS[s] for s in panel["supports"]]
    xmin, ymin, xmax, ymax = shape.bounds
    xs = sorted({xmin, xmax} | {v for s in segments for v in (s.x1,s.x2) if xmin < v < xmax})
    ys = sorted({ymin, ymax} | {v for s in segments for v in (s.y1,s.y2) if ymin < v < ymax})
    pieces = defaultdict(list)
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            tile = box(x0,y0,x1,y1).intersection(shape)
            if tile.area < 1e-12:
                continue
            scores = []
            for s in segments:
                condition = EDGE_CASES[panel["panel_id"]][s.support_id]
                weight = SQRT3 if condition == "C" and not matched and panel["panel_id"] not in ONE_WAY else 1.0
                scores.append(affine_score(s,(x0+x1)/2,(y0+y1)/2,weight))
            for i, s in enumerate(segments):
                vertices = [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
                for j in range(len(segments)):
                    if i == j:
                        continue
                    a,b,c = (scores[i][k]-scores[j][k] for k in range(3))
                    if max(abs(a),abs(b),abs(c)) < 1e-11:
                        if j < i:
                            vertices=[]
                            break
                    else:
                        vertices = clip(vertices,a,b,c)
                    if len(vertices) < 3:
                        break
                if len(vertices) >= 3:
                    cell = Polygon(vertices).intersection(tile)
                    if cell.area > 1e-12:
                        pieces[s.support_id].append(cell)
                        tied=[segments[j].support_id for j in range(len(segments)) if j!=i and max(abs(scores[i][k]-scores[j][k]) for k in range(3))<1e-11]
                        if tied and tie_audit is not None:
                            tie_audit.append(dict(panel_id=panel["panel_id"],adopted_support=s.support_id,
                                equally_scored_supports=";".join(tied),area_m2=cell.area,
                                convention="earlier listed support; geometric tie only, not a verified physical load path"))
    return {s:unary_union(parts) for s,parts in pieces.items()}


def reason(support):
    if support.startswith("W_"):
        return "Wall/core edge: monolithic rotational restraint assumed; connection and W_CORE_R geometry unverified."
    if support in ROOT_BEAMS:
        return "Cantilever-root edge: restrained whole-edge idealisation assumed; finite overhang coverage does not prove full fixity."
    if support in {"D02","D05","D11","D13","D15","D19","D22"}:
        return "Slab terminates or meets an opening: supported but rotationally simple assumed."
    return "Slab continues across an internal beam: continuous idealisation assumed; reinforcement unverified."


def draw_plan(regions, unresolved, name, coloured):
    fig,ax=plt.subplots(figsize=(9,14),layout="constrained")
    colours=plt.get_cmap("tab20")
    for (panel_id,support),geom in regions.items():
        colour=colours((int(support[1:])-1)%20) if support in BEAM_MAP else "#c8c8c8"
        for poly in polygons(geom):
            ax.add_patch(PlotPolygon(np.asarray(poly.exterior.coords),closed=True,
                facecolor=colour if coloured else "#fafafa", alpha=.5 if coloured else 1,
                edgecolor="#333333",linestyle=(0,(4,3)),linewidth=.7))
    for poly in polygons(unresolved):
        ax.add_patch(PlotPolygon(np.asarray(poly.exterior.coords),facecolor="#ffe6b7",hatch="xxx",edgecolor="#b77a20",linewidth=.5))
        for ring in poly.interiors:
            ax.add_patch(PlotPolygon(np.asarray(ring.coords),facecolor="white",edgecolor="#b77a20",linewidth=.5))
    # Physical wall/column outlines are a background reference, not extra supports.
    with (ROOT / "Step_01B_Vertical_Element_Coordinates.csv").open(encoding="utf-8-sig") as stream:
        physical = list(csv.DictReader(stream))
    for row in physical:
        x1,y1,x2,y2=(float(row[k]) for k in ("x1_m","y1_m","x2_m","y2_m"))
        if row["element_type"] == "wall":
            footprint=LineString([(x1,y1),(x2,y2)]).buffer(.125,cap_style=2)
        else:
            width,depth=(float(v)/1000 for v in row["section_mm"].split("x"))
            footprint=box(x1-width/2,y1-depth/2,x1+width/2,y1+depth/2)
        for poly in polygons(footprint):
            ax.add_patch(PlotPolygon(np.asarray(poly.exterior.coords),facecolor="#c7c7c7",hatch="///",edgecolor="#444",linewidth=.5))
        if row["axis_segment"] == "main" and row["element_id"] in {"T5","T6","T9","T10","T11","T12"}:
            ax.text((x1+x2)/2,(y1+y2)/2,row["element_id"],fontsize=7,ha="center",va="center",bbox=dict(facecolor="white",edgecolor="none",pad=.5))
    for s,seg in SUPPORTS.items():
        ax.plot([seg.x1,seg.x2],[seg.y1,seg.y2],color="#9a3497" if s=="W_CORE_R" else "#172033",linewidth=1,
                linestyle="--" if s=="W_CORE_R" else "-")
        ax.text((seg.x1+seg.x2)/2,(seg.y1+seg.y2)/2,s.replace("W_",""),fontsize=6.5,
            ha="center",va="center",bbox=dict(facecolor="white",edgecolor="none",alpha=.75,pad=1))
    for panel in PANELS:
        p=Polygon(panel["polygon"]).representative_point()
        ax.text(p.x,p.y,panel["panel_id"],fontsize=9,fontweight="bold")
    # Corner P3 bottom-left: C horizontal / S vertical; actual line slope sqrt(3).
    ax.annotate("60 deg from D16 (C)\n30 deg from D11 (S)",xy=(.5,6.05+SQRT3*.5),
                xytext=(-2.5,8.5),fontsize=8,arrowprops=dict(arrowstyle="->",color="#b12b2b"),color="#b12b2b")
    ax.annotate("45 deg: C/C",xy=(3.0,6.65),xytext=(4.4,5.4),fontsize=8,
                arrowprops=dict(arrowstyle="->",color="#215ba0"),color="#215ba0")
    ax.set(xlim=(-2.8,10.9),ylim=(-1.5,20.1),xlabel="x (m)",ylabel="y (m)")
    ax.set_aspect("equal")
    ax.set_title("Plan 3 | Provisional mixed-edge model: 45 / 60 / 30 degrees\n"+(
        "Closed tributary polygons" if coloured else "Dashed boundaries and wall axes"),fontsize=12)
    ax.legend(handles=[Patch(facecolor="#ccc",label="Image-derived physical walls / columns"),
        Patch(facecolor="#ffe6b7",hatch="xxx",label="Unresolved core geometry (not beam load)")],loc="upper left",fontsize=7)
    ax.text(5.6,9.0,"S1 excluded",fontsize=7,ha="center",color="#777")
    ax.text(5.2,11.2,"O1",fontsize=7,ha="center",color="#777")
    ax.text(6.25,11.2,"O2",fontsize=7,ha="center",color="#777")
    fig.savefig(ROOT/name,dpi=190)
    plt.close(fig)


def main():
    census_fields=["beam_id","x1_m","y1_m","x2_m","y2_m","span_m","width_mm","depth_mm","panels","role"]
    census=[]
    for beam in BEAMS:
        data=dict(beam,span_m=SEGMENTS[beam["beam_id"]].length)
        census.append({field:f"{data[field]:.4f}" if isinstance(data[field],float) else data[field] for field in census_fields})
    write_csv("Step_04_Beam_Census.csv",census)
    regions={}
    conditions=[]
    checks=[]
    tie_audit=[]
    def check(name,actual,expected,tol=1e-8):
        passed=abs(actual-expected)<=tol
        checks.append(dict(check=name,actual=actual,expected=expected,tolerance=tol,status="PASS" if passed else "FAIL"))
        if not passed:
            raise ValueError(f"{name}: {actual} != {expected}")
    matched_areas=defaultdict(float)
    for panel in PANELS:
        allocated=partition(panel,tie_audit=tie_audit)
        shape=Polygon(panel["polygon"])
        for s,g in allocated.items():
            regions[(panel["panel_id"],s)]=g
        merged=unary_union(list(allocated.values()))
        check(panel["panel_id"]+" coverage",merged.symmetric_difference(shape).area,0)
        check(panel["panel_id"]+" overlap",sum(g.area for g in allocated.values())-merged.area,0)
        for s,g in partition(panel,matched=True).items():
            matched_areas[s]+=g.area
        for s in panel["supports"]:
            conditions.append(dict(panel_id=panel["panel_id"],support_id=s,condition=EDGE_CASES[panel["panel_id"]][s],
                rule="one-way equal split; no corner-angle allocation" if panel["panel_id"] in ONE_WAY else "C/C or S/S:45; C/S:60 from C,30 from S",
                basis=reason(s),status="assumption requiring course review"))

    # Source-projection polygons. Clip cantilever roots by their actual coordinates.
    overhangs={"P10":box(3.75,19.2,6.4,19.7),"P11":box(0,15.2,2.45,16.2),
        "P12":box(7.75,13.8,8.25,18.1),"P13":box(7.75,12.1,10.2,13.0),"P14":box(1,-1.2,9.2,0)}
    root_ids={"P10":["D01","W_T1"],"P11":["D04"],"P12":["D03","D07"],"P13":["D10"],"P14":["D23","D24","D25"]}
    for panel,g in overhangs.items():
        for s in root_ids[panel]:
            seg=SUPPORTS[s]
            extent=box(min(seg.x1,seg.x2),-100,max(seg.x1,seg.x2),100) if seg.horizontal else box(-100,min(seg.y1,seg.y2),100,max(seg.y1,seg.y2))
            piece=g.intersection(extent)
            regions[(panel,s)]=piece
            matched_areas[s]+=piece.area
            conditions.append(dict(panel_id=panel,support_id=s,condition="cantilever root",rule="all to root; no 30/60 split",basis="overhang footprint clipped to finite root segment",status="image-derived"))
        check(panel+" coverage",sum(regions[(panel,s)].area for s in root_ids[panel]),g.area)

    # Explicitly preserve the HW1 footprint and exclusions, without a residual filler.
    gross=unary_union([box(0,0,10.2,12.1),box(0,12.1,7.75,15.2),box(2.45,15.2,7.75,19.2),*overhangs.values()])
    excluded=unary_union([box(4.7,10.6,5.75,11.85),box(6,10.6,6.55,11.85),box(4.7,7.45,6.55,10.35)])
    floor=gross.difference(excluded)
    coverage=unary_union(list(regions.values()))
    unresolved=floor.difference(coverage)
    check("HW1 ordinary floor",floor.area,179.25)
    check("allocated outside ordinary floor",coverage.difference(floor).area,0)
    check("inter-panel overlap",sum(g.area for g in regions.values())-coverage.area,0)
    check("allocation + explicitly unresolved",coverage.area+unresolved.area,floor.area)
    for key,g in regions.items():
        if not g.is_valid:
            raise ValueError(f"Invalid polygon {key}")
    feature_list=[dict(type="Feature",properties=dict(panel_id=p,support_id=s),geometry=mapping(g)) for (p,s),g in regions.items()]
    feature_list.append(dict(type="Feature",properties=dict(panel_id="unresolved",support_id="UNRESOLVED"),geometry=mapping(unresolved)))
    (ROOT/"Step_04_Closed_Regions.geojson").write_text(json.dumps(dict(type="FeatureCollection",features=feature_list)),encoding="utf-8")
    write_csv("Step_04_Slab_Edge_Conditions.csv",conditions)
    write_csv("Step_04_Finite_Edge_Ties.csv",tie_audit,
              ["panel_id","adopted_support","equally_scored_supports","area_m2","convention"])
    contributions=[dict(support_id=s,panel_id=p,tributary_area_m2=round(g.area,8),support_type="beam" if s in BEAM_MAP else "wall/direct support") for (p,s),g in regions.items()]
    contributions.append(dict(support_id="UNRESOLVED",panel_id="unresolved",tributary_area_m2=round(unresolved.area,8),support_type="unassigned; not a load-path result"))
    write_csv("Step_04_Beam_Tributary_Area_Contributions.csv",contributions)

    profiles=[]
    endpoint_rows=[]
    summary=[]
    for row in BEAMS:
        s=row["beam_id"]; seg=SEGMENTS[s]; L=seg.length
        g=unary_union([g for (p,t),g in regions.items() if t==s])
        origin=min(seg.x1,seg.x2) if seg.horizontal else min(seg.y1,seg.y2)
        stem=.25*(row["depth_mm"]/1000-.15)*25
        total=0.; moment=0.
        bins=round(L/PROFILE_DX)
        for i in range(bins):
            a=L*i/bins; b=L*(i+1)/bins
            strip=box(origin+a,-100,origin+b,100) if seg.horizontal else box(-100,origin+a,100,origin+b)
            area=g.intersection(strip).area
            width=area/(b-a)
            cuts=sorted({a,b} | ({L/2} if a<L/2<b else set()))
            influence_integral=sum((v-u)*.25*(min(u,L-u)+min(v,L-v)) for u,v in zip(cuts,cuts[1:]))
            moment+=8.75*width*influence_integral
            total+=area
            profiles.append(dict(beam_id=s,s0_m=a,s1_m=b,tributary_width_m=width,
                slab_dead_kN_m=width*3.75,beam_stem_kN_m=stem,live_kN_m=width*5,service_kN_m=width*8.75+stem))
        for end in (0.,L):
            lo,hi=(-100,origin) if end==0 else (origin+L,100)
            strip=box(lo,-100,hi,100) if seg.horizontal else box(-100,lo,100,hi)
            area=g.intersection(strip).area
            if area>1e-9:
                endpoint_rows.append(dict(beam_id=s,s_m=end,tributary_area_m2=area,dead_kN=area*3.75,live_kN=area*5,service_kN=area*8.75,
                    basis="finite-edge endpoint projection; assumption, not distributed width"))
            total+=area
        check(s+" profile + endpoint area",total,g.area,1e-7)
        summary.append(dict(beam_id=s,span_m=L,depth_mm=row["depth_mm"],panels=row["panels"],role=row["role"],
            tributary_area_m2=g.area,mean_tributary_width_m=g.area/L,load_shape="piecewise mixed-edge profile; see CSV",
            slab_dead_udl_kN_m=g.area*3.75/L,beam_stem_dead_udl_kN_m=stem,total_dead_udl_kN_m=g.area*3.75/L+stem,
            live_udl_kN_m=g.area*5/L,service_udl_total_load_equiv_kN_m=g.area*8.75/L+stem,
            service_udl_midspan_moment_equiv_kN_m=8*moment/L**2+stem))
    write_csv("Step_05_Beam_Line_Loads.csv",summary)
    write_csv("Step_05_Beam_Load_Profiles.csv",profiles)
    write_csv("Step_05_Beam_Endpoint_Loads.csv",endpoint_rows,
              ["beam_id","s_m","tributary_area_m2","dead_kN","live_kN","service_kN","basis"])
    write_csv("Step_04_Mixed_Support_Verification.csv",checks)
    # Before/after from the preserved checkpoint; no repeatedly changing baseline.
    with zipfile.ZipFile(ROOT/"HW2_Pre_Mixed_Support_Revision_b867ebd.zip") as archive:
        old={r["beam_id"]:r for r in csv.DictReader(io.StringIO(archive.read("Step_05_Beam_Line_Loads.csv").decode("utf-8-sig")))}
    delta=[dict(beam_id=r["beam_id"],old_area_m2=float(old[r["beam_id"]]["tributary_area_m2"]),new_area_m2=r["tributary_area_m2"],
        matched_exact_area_m2=matched_areas[r["beam_id"]],mixed_minus_matched_m2=r["tributary_area_m2"]-matched_areas[r["beam_id"]],
        old_service_kN_m=float(old[r["beam_id"]]["service_udl_total_load_equiv_kN_m"]),new_service_kN_m=r["service_udl_total_load_equiv_kN_m"]) for r in summary]
    write_csv("Step_04_Revision_Comparison.csv",delta)
    draw_plan(regions,unresolved,"HW2_Beam_Tributary_Areas.png",True)
    draw_plan(regions,unresolved,"HW2_Beam_Tributary_Boundaries.png",False)
    fig,ax=plt.subplots(figsize=(9,4),layout="constrained")
    for field,label in [("slab_dead_kN_m","Slab G"),("live_kN_m","Q"),("service_kN_m","G + Q incl. beam stem")]:
        points=[r for r in profiles if r["beam_id"]=="D18"]
        ax.step([(r["s0_m"]+r["s1_m"])/2 for r in points],[r[field] for r in points],where="mid",label=label)
    ax.set(xlabel="Distance along D18 (m)",ylabel="Line load (kN/m)",title="D18 | Actual mixed-support profile")
    ax.legend();ax.grid(alpha=.2);fig.savefig(ROOT/"HW2_D18_Worked_Line_Load.png",dpi=190);plt.close(fig)
    report(regions,unresolved,summary,conditions,delta,checks,tie_audit)
    print(f"Mixed-support revision: {len(checks)} checks; beam area {sum(r['tributary_area_m2'] for r in summary):.6f}; unresolved {unresolved.area:.6f} m2")


def report(regions,unresolved,summary,conditions,delta,checks,tie_audit):
    beam_area=sum(r["tributary_area_m2"] for r in summary)
    direct=sum(g.area for (p,s),g in regions.items() if s not in BEAM_MAP)
    text=["# Step 04 - Revised Mixed Slab-Edge Conditions", "", 
        "Revision of checkpoint b867ebd. The original Step 04-06 outputs and code are preserved in [the pre-revision archive](HW2_Pre_Mixed_Support_Revision_b867ebd.zip). HW1 geometry is unchanged.","",
        "## Method and source", "", ANGLE_SOURCE,"",
        "C = continuous/rotationally restrained idealisation; S = supported with simple rotation idealisation. These labels describe the slab edge, not the end releases of the supporting beam. Complexity alone does not select an angle. The exact edge connection cannot be read reliably from this plan; every C/S entry below is an explicit modelling assumption.","",
        "For adjacent perpendicular edges use score = finite L1 distance / weight, with w(S)=1 and w(C)=sqrt(3). If the horizontal edge is C and the vertical edge S, equal scores give y=sqrt(3)x: 60 degrees from C and 30 from S. Equal weights give 45 degrees. Opposite unequal edges meet at a shifted straight division, not a 60-degree intersection of parallel edges. This weighted-distance construction is an adopted extension to finite edges and L-shaped panels; it is not a general yield-line or elastic plate solution.","",
        "The rule comes from the supplied assignment. [HKConcrete 2013 Table 6.7](https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/CoP_SUC2013e.pdf) distinguishes continuous/discontinuous edges, but its coefficients are not identical to the geometric weighting used here. No code compliance or stiffness-based support classification is claimed.","",
        "## Edge schedule", "", "| Panel | Support | Condition | Basis |", "|---|---|---|---|"]
    text += [f"| {r['panel_id']} | {r['support_id']} | {r['condition']} | {r['basis']} |" for r in conditions]
    text += ["", "P4/P6/P8 retain their previous one-way equal reaction split; 30/60 corner rules are not applied to them. Cantilevers route all load to their actual root extent. Treating an entire cantilever-root edge as C is a sensitivity assumption, not proof of full fixity over that edge.","",
        "## Closed boundaries and areas","","![Dashed boundaries](HW2_Beam_Tributary_Boundaries.png)","","![Areas](HW2_Beam_Tributary_Areas.png)","",
        "Closed polygons are exported in [GeoJSON](Step_04_Closed_Regions.geojson) in local metres, not geographic coordinates. Hatched grey strips show wall axes/widths; orange cross-hatching identifies a geometry gap inherited from the panel reconstruction.","",
        "## Revised beam schedule","","| Beam | Previous area (m2) | Revised area (m2) | Angle-only change vs exact matched model (m2) |","|---|---:|---:|---:|"]
    text += [f"| {r['beam_id']} | {r['old_area_m2']:.4f} | {r['new_area_m2']:.4f} | {r['mixed_minus_matched_m2']:+.4f} |" for r in delta]
    text += ["","The full census remains in [Step 04 census](Step_04_Beam_Census.csv). The matched comparator uses the same exact geometry, so the last column isolates the angle change from polygon integration and cantilever-root corrections.","",
        "## Conservation and limitations","",f"- Beams: {beam_area:.6f} m2.",f"- Direct wall/support allocation: {direct:.6f} m2.",f"- Explicit unresolved geometry: {unresolved.area:.6f} m2.",f"- Total: {beam_area+direct+unresolved.area:.6f} m2 (HW1 ordinary slab).",
        f"- {len(checks)} checks passed; polygon closure/overlap tolerance 1e-8 m2; profile integration tolerance 1e-7 m2.",
        "- The unresolved region has not been assigned an invented wall reaction. The previous residual filler is removed. Complete load-path closure is still pending core geometry clarification.",
        "- Grey physical walls/columns come from the HW1 coordinate schedule for visual reference. Black support axes retain the earlier HW2 idealised segmentation, which is not identical to every physical wall extent. W_CORE_R (magenta dashed) is an unverified assumed core support, not a verified physical wall. The 30/60-degree update does not validate that earlier geometry.",
        f"- Finite-segment L1 scores also create {sum(r['area_m2'] for r in tie_audit):.6f} m2 of positive-area ties. These are provisionally assigned by support-list order, not mechanical evidence. [Tie audit](Step_04_Finite_Edge_Ties.csv) identifies the affected supports. This is a distinct uncertainty within allocated area, not additional unallocated floor area. It explains some changes versus the old raster tie handling, including D06; use the rectangular P3 corner tests as the clean 30/60 example.",
        "- Finite-edge cells projecting beyond a beam endpoint are exported as endpoint forces, not as artificially enormous line-load ordinates.",
        "- P12 now uses the actual y=13.8 to 18.1 extent across D07/D03; the previous 4.0/0.3 m root split was inconsistent with that footprint.","",
        "Reproduce: `python hw2_beam_loads.py`. Verification: `python verify_hw2_mixed_supports.py`."]
    (ROOT/"Step_04_Beam_Census_and_Tributary_Areas.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    text=["# Step 05 - Revised Beam Line Loads", "", "Uses the closed mixed-support polygons from revised Step 04. Units: m, m2, kN and kN/m.","",
        "Slab G=3.75 kN/m2; Q=5.00 kN/m2. Beam stem G=0.25(d-0.15)*25 kN/m. For each profile interval q(s)=8.75*b(s)+G_stem. Force-equivalent UDL is total force/L. The midspan-moment-equivalent UDL is 8*M(L/2)/L^2, integrating the simply-supported influence line 0.5*min(s,L-s). Neither is a substitute for the actual shear or moment diagram, especially with asymmetric loading.","",
        "[Profile CSV](Step_05_Beam_Load_Profiles.csv) stores exact strip areas divided by strip length (0.01 m strips). [Endpoint forces](Step_05_Beam_Endpoint_Loads.csv) are kept separately. Step 06 reads these distributions directly and no longer reconstructs symmetric shapes from two UDLs.","",
        "| Beam | L (m) | Area (m2) | Slab G | Stem G | Q | Total force-equivalent UDL | Midspan-moment-equivalent UDL |","|---|---:|---:|---:|---:|---:|---:|---:|"]
    text += [f"| {r['beam_id']} | {r['span_m']:.2f} | {r['tributary_area_m2']:.4f} | {r['slab_dead_udl_kN_m']:.4f} | {r['beam_stem_dead_udl_kN_m']:.4f} | {r['live_udl_kN_m']:.4f} | {r['service_udl_total_load_equiv_kN_m']:.4f} | {r['service_udl_midspan_moment_equiv_kN_m']:.4f} |" for r in summary]
    r=next(r for r in summary if r["beam_id"]=="D18")
    text += ["","## D18 worked example","",f"L={r['span_m']:.2f} m; A={r['tributary_area_m2']:.6f} m2; average width A/L={r['mean_tributary_width_m']:.6f} m. Slab G=3.75A/L={r['slab_dead_udl_kN_m']:.6f} kN/m; stem G={r['beam_stem_dead_udl_kN_m']:.6f} kN/m; Q=5A/L={r['live_udl_kN_m']:.6f} kN/m. Integrated simply-supported midspan moment={r['service_udl_midspan_moment_equiv_kN_m']*r['span_m']**2/8:.6f} kN m.","","![D18 profile](HW2_D18_Worked_Line_Load.png)","","The edge-condition assumptions and unresolved core area in Step 04 still govern the scope of these loads."]
    (ROOT/"Step_05_Beam_Line_Loads_and_Worked_Example.md").write_text("\n".join(text)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
