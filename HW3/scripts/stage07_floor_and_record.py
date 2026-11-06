"""Complete Task 1 geometry/area records with retained dimension-chain floor data."""
import ast
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import cv2
import numpy as np
from shapely.geometry import box, mapping
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent


def archived_literal(source,name):
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(name)


def partition(elements,rects,excluded,step):
    xs=(np.arange(round(10.2/step))+.5)*step
    ys=-1.2+(np.arange(round(20.9/step))+.5)*step
    X=xs[None,:]; Y=ys[:,None]
    valid=np.zeros((len(ys),len(xs)),bool)
    for x,y,w,h in rects:
        valid|=(X>=x)&(X<x+w)&(Y>=y)&(Y<y+h)
    for _,x,y,w,h in excluded:
        valid&=~((X>=x)&(X<x+w)&(Y>=y)&(Y<y+h))
    best=np.full(valid.shape,np.inf)
    owner=np.full(valid.shape,-1,dtype=np.int16)
    for idx,e in enumerate(elements):
        cx,cy=e["centre_m"]
        if e["class"]=="column":
            ax=bx=cx; ay=by=cy
        else:
            L=max(e["size_mm"])/1000
            ax,bx=(cx-L/2,cx+L/2) if e["angle_deg"]==0 else (cx,cx)
            ay,by=(cy,cy) if e["angle_deg"]==0 else (cy-L/2,cy+L/2)
        d=np.abs(X-np.clip(X,ax,bx))+np.abs(Y-np.clip(Y,ay,by))
        win=d<best
        owner[win]=idx; best[win]=d[win]
    owner[~valid]=-1
    return owner,np.bincount(owner[valid],minlength=len(elements))*step**2


def polygons(owner,step):
    active={}; rectangles={}
    for row in range(owner.shape[0]+1):
        runs=set()
        if row<owner.shape[0]:
            a=owner[row]
            cuts=np.r_[0,np.flatnonzero(a[1:]!=a[:-1])+1,len(a)]
            for l,r in zip(cuts[:-1],cuts[1:]):
                if a[l]>=0:runs.add((int(a[l]),int(l),int(r)))
        for key in list(active):
            if key not in runs:
                idx,l,r=key; start=active.pop(key)
                rectangles.setdefault(idx,[]).append(box(l*step,-1.2+start*step,r*step,-1.2+row*step))
        for key in runs:
            active.setdefault(key,row)
    return {idx:unary_union(rects) for idx,rects in rectangles.items()}


def main():
    out=ROOT/"outputs/Plan3/task1"
    out.mkdir(parents=True,exist_ok=True)
    source=subprocess.check_output(["git","show","5f1eafe:tributary_regions.py"],cwd=REPO).decode("utf-8")
    slabs=archived_literal(source,"slabs"); exclusions=archived_literal(source,"openings")
    outline=unary_union([box(x,y,x+w,y+h) for x,y,w,h in slabs])
    flat=outline.difference(unary_union([box(x,y,x+w,y+h) for _,x,y,w,h in exclusions]))
    void=unary_union([box(x,y,x+w,y+h) for n,x,y,w,h in exclusions if n!="S1"])
    stair=next(box(x,y,x+w,y+h) for n,x,y,w,h in exclusions if n=="S1")
    geometry=json.loads((ROOT/"outputs/Plan3/stage05/Classical_Elements_Unpromoted.json").read_text())
    original=json.loads((ROOT/"outputs/Plan3/stage01/Classical_Components.json").read_text())
    matches=json.loads((ROOT/"outputs/Plan3/stage03/Bar_Label_Matches.json").read_text())["matches"]
    # The local labelled-length fit is retained, but a global dimension anchor is
    # necessary to put image-derived centres on the inherited dimensioned floor.
    # This deterministic affine calibration uses only observed exterior extents
    # and printed overall chains; it does not snap individual walls or clip them.
    old_calibration=json.loads((ROOT/"outputs/Plan3/stage05/Metric_Calibration.json").read_text())
    left=min(m["bbox_px"][0] for m in matches)
    right=max(m["bbox_px"][0]+m["bbox_px"][2] for m in matches)
    top=min(m["bbox_px"][1] for m in matches)
    bottom=max(m["bbox_px"][1]+m["bbox_px"][3] for m in matches)
    adopted_scale={"x":(right-left)/10.2,"y":(bottom-top)/19.2}
    for e in geometry["elements"]:
        m=next(m for m in matches if m["label"]==e["labels"][0])
        x,y,w,h=m["bbox_px"]
        e["audit"]["prior_label_scale_centre_m"]=e["centre_m"]
        e["centre_m"]=[(x+w/2-left)/adopted_scale["x"],(bottom-y-h/2)/adopted_scale["y"]]
    geometry["scale_px_per_m"]=adopted_scale
    (out/"Global_Dimension_Anchor.json").write_text(json.dumps({
        "adopted_scale_px_per_m":adopted_scale,"origin_px":[left,bottom],
        "printed_chains_m":{"x":[1.,8.2,1.],"y":[19.2]},
        "label_median_scale_px_per_m":old_calibration["scale_px_per_m"],
        "reason":"Local labelled-length scale caused five footprint/floor mismatches. A single global dimension-anchored affine transform is applied to all measured centres; no per-element coordinate snapping, clipping, or VLM measurement.",
        "limitation":"Observed exterior bar extents carry pixel/stroke uncertainty; dimension chains are image-derived, not CAD."},indent=2),encoding="utf-8")
    grouped={}
    for m in matches:
        cx,cy=m["centre_px"]
        contained=[]
        for c in original["components"]:
            x,y,w,h=c["bbox_px"]
            if x<=cx<=x+w and y<=cy<=y+h:contained.append(c)
        if contained:
            c=min(contained,key=lambda c:c["bbox_px"][2]*c["bbox_px"][3])
            grouped.setdefault(c["component_id"],[]).append(m["label"])
    alone=sum(len(labels)==1 for labels in grouped.values())
    shared=sum(len(labels) for labels in grouped.values() if len(labels)>1)
    unclaimed=len(original["components"])-len(grouped)
    score={"association_route":"Retrospective label-to-initial-component bbox audit; not an unseen detector benchmark.",
           "classical":{"labelled_elements_located":sum(map(len,grouped.values())),
                        "one_to_one_labels":alone,"merged_groups":[v for v in grouped.values() if len(v)>1],
                        "labels_sharing_object":shared,"unlabelled_objects":unclaimed,
                        "score":alone-shared-unclaimed,
                        "broken_elements_observed":0,"break_note":"No axial breaks in the 21 matched bars under the current review; short returns are grouped, not additional elements."},
           "label_supervised":{"one_to_one_labels":len(matches),"merged_groups":0,"unclaimed_bars":0,"score":len(matches)}}
    (out/"Score_Sheet.json").write_text(json.dumps(score,indent=2),encoding="utf-8")
    floor={"source":"Archived HW1 dimension-chain reading, commit 5f1eafe; rebuilt as rectangle union, not an ink contour.",
           "source_sha256":hashlib.sha256(source.encode()).hexdigest(),"rectangles_m":slabs,
           "exclusions_m":exclusions,"gross_area_m2":outline.area,"ordinary_flat_area_m2":flat.area,
           "void_area_m2":void.area,"separate_stair_area_m2":stair.area,
           "net_horizontal_area_including_stair_m2":outline.area-void.area,
           "assumptions":["Five balconies retained; P10 location and short returns remain image-derived.",
                          "O1/O2 remain voids. S1 is separately loaded, not silently treated as ordinary flat slab.",
                          "The outline is inherited from the documented HW1 reading; no claim of newly automated outline detection."]}
    (out/"Floor_Dimension_Record.json").write_text(json.dumps(floor,indent=2),encoding="utf-8")
    fc={"type":"FeatureCollection","features":[{"type":"Feature","properties":{"zone":n},"geometry":mapping(g)} for n,g in (("gross",outline),("ordinary_flat_slab",flat),("voids",void),("separate_stair",stair))]}
    (out/"Floor_Zones.geojson").write_text(json.dumps(fc),encoding="utf-8")
    owner,areas=partition(geometry["elements"],slabs,exclusions,.01)
    _,coarse=partition(geometry["elements"],slabs,exclusions,.02)
    regions=polygons(owner,.01)
    assert abs(sum(g.area for g in regions.values())-flat.area)<1e-7
    assert unary_union(list(regions.values())).symmetric_difference(flat).area<1e-7
    assert abs(sum(g.area for g in regions.values())-unary_union(list(regions.values())).area)<1e-7
    features=[]
    # Historic source fields are preserved exactly rather than guessed from names.
    historic_csv=subprocess.check_output(["git","show","5f1eafe:Step_01C_Tributary_Areas.csv"],cwd=REPO).decode("utf-8")
    historic_rows=list(csv.DictReader(io.StringIO(historic_csv)))
    area_key=next(k for k in historic_rows[0] if "area" in k and "m2" in k)
    old_areas={r["element_id"]:float(r[area_key]) for r in historic_rows}
    rows=[]
    for idx,e in enumerate(geometry["elements"]):
        label=e["labels"][0]; area=float(areas[idx])
        features.append({"type":"Feature","properties":{"element":label,"area_m2":area},"geometry":mapping(regions[idx])})
        rows.append({"element":label,"area_m2":area,"historic_HW1_area_m2":old_areas[label],
                     "difference_m2":area-old_areas[label],"change_2cm_to_1cm_m2":float(areas[idx]-coarse[idx]),
                     "flat_G_plus_Q_one_floor_kN":area*8.75})
    (out/"Closed_Tributary_Regions.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features}),encoding="utf-8")
    with (out/"Candidate_Tributary_Areas.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    # Retain HW1 loads separately: this new diagnostic does not replace accepted HW1 results.
    historic_loads=subprocess.check_output(["git","show","5f1eafe:Step_02_Element_Load_Summary.csv"],cwd=REPO)
    (out/"Inherited_HW1_Loads.csv").write_bytes(historic_loads)
    geometry["floor"]={"outline_area_m2":outline.area,"load_kN_m2":8.75,"storeys":5,
                       "ordinary_flat_area_m2":flat.area,"void_area_m2":void.area,"separate_stair_area_m2":stair.area}
    geometry["checks"]={"sum_areas_m2":float(sum(areas)),"sum_axial_kN":float(sum(areas)*8.75*5),
                        "axial_scope":"five-storey ordinary-flat-slab G+Q contribution only; S1 and element self-weight are in Inherited_HW1_Loads.csv",
                        "region_union_error_m2":unary_union(list(regions.values())).symmetric_difference(flat).area}
    geometry.pop("status",None)
    manifest=json.loads((ROOT/"outputs/Plan3/reader_package_v1/Flag_Manifest.json").read_text())
    shape_audit=[]
    revision_audit=[]
    hatch=cv2.imread(str(ROOT/"outputs/Plan3/stage01/02_Diagonal_Hatching.png"),0)
    calibration=json.loads((ROOT/"outputs/Plan3/stage05/Metric_Calibration.json").read_text())
    for e in geometry["elements"]:
        e["audit"].update(merged=False,partly_missed=[])
        applicable=[f for f in manifest["flags"] if f["candidate_label"]==e["labels"][0]]
        e["audit"]["flags"] += [{"flag_id":f["flag_id"],"kind":f["flag"],"source":f["source"]} for f in applicable]
        e["audit"]["short_returns"]="Not separately modelled; labelled rectangular main body only. Historic HW1 grouped returns are retained in its source files."
        cx,cy=e["centre_m"]
        a,b=e["size_mm"]
        if e["class"]=="wall":
            w,h=(max(a,b)/1000,min(a,b)/1000) if e["angle_deg"]==0 else (min(a,b)/1000,max(a,b)/1000)
        else:w,h=a/1000,b/1000
        footprint=box(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
        outside=footprint.difference(outline).area
        prior_x,prior_y=e["audit"]["prior_label_scale_centre_m"]
        prior_outside=box(prior_x-w/2,prior_y-h/2,prior_x+w/2,prior_y+h/2).difference(outline).area
        revision_audit.append({"element":e["labels"][0],"prior_outside_m2":prior_outside,"adopted_outside_m2":outside})
        match=next(m for m in matches if m["label"]==e["labels"][0])
        px,py,pw,ph=match["bbox_px"]
        hc=hatch[py:py+ph,px:px+pw]
        support=float(np.mean(np.any(hc>0,axis=0 if match["direction"]=="x" else 1)))
        e["audit"]["hatch_axial_support"]=support
        if support<.85:e["audit"]["partly_missed"].append("less than 85% axial support in original diagonal-hatching pass")
        e["audit"]["footprint_outside_dimension_floor_m2"]=outside
        e["audit"]["geometric_warnings"]=["Metric calibration and retained dimension-floor mismatch; not corrected by a VLM."] if outside>1e-6 else []
        shape_audit.append({"element":e["labels"][0],"outside_m2":outside,"hatch_axial_support":support})
    (out/"Element_Geometry_Audit.json").write_text(json.dumps({"elements":shape_audit,
        "note":"Nonzero outside area is retained as a geometry warning, not hidden by clipping or a reader-supplied coordinate."},indent=2),encoding="utf-8")
    (out/"Calibration_Revision_Audit.json").write_text(json.dumps(revision_audit,indent=2),encoding="utf-8")
    (out/"Elements_Classical.json").write_text(json.dumps(geometry,indent=2),encoding="utf-8")
    # Column grid: preserve measured coordinates, cluster only within 0.15 m.
    grid={}
    for ax,dim in (("x",0),("y",1)):
        groups=[]
        for v in sorted(e["centre_m"][dim] for e in geometry["elements"] if e["class"]=="column"):
            if groups and abs(v-np.mean(groups[-1]))<=.15:groups[-1].append(v)
            else:groups.append([v])
        grid[ax]=[float(np.mean(g)) for g in groups]
    (out/"Column_Grid.json").write_text(json.dumps({"tolerance_m":.15,"axes_m":grid,"note":"Measured column axes; no silent snapping of element coordinates."},indent=2),encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,12))
    for i,e in enumerate(geometry["elements"]):
        g=regions[i]
        for p in ([g] if g.geom_type=="Polygon" else g.geoms):
            x,y=p.exterior.xy;ax.fill(x,y,alpha=.25);ax.plot(x,y,"--",lw=.5,color="gray")
            for ring in p.interiors:ax.fill(*ring.xy,color="white")
        ax.text(*g.representative_point().coords[0],e["labels"][0],fontsize=8)
    for n,x,y,w,h in exclusions:
        ax.add_patch(plt.Rectangle((x,y),w,h,facecolor="white",edgecolor="orange",hatch="xx" if n!="S1" else "//"))
        ax.text(x+w/2,y+h/2,n,ha="center",fontsize=8)
    ax.plot(*outline.exterior.xy,color="black",lw=1.5)
    ax.set(aspect="equal",xlabel="x (m)",ylabel="y (m)",title="Task 1 | Candidate closed L1 regions; retained dimension-chain floor")
    fig.tight_layout();fig.savefig(out/"Floor_and_Closed_Regions.png",dpi=160);plt.close(fig)
    print("Floor gross / ordinary / void / stair:",outline.area,flat.area,void.area,stair.area)
    print("Closed regions:",len(regions),"area:",sum(areas),"max grid sensitivity:",max(abs(areas-coarse)))
    print("Scores:",score)


if __name__=="__main__":
    main()
