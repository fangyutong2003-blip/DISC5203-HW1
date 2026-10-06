"""Independent analytic and exported-data checks for the mixed-edge revision."""
import csv
import json
import math
from pathlib import Path

from shapely.geometry import shape, box, Point
from shapely.ops import unary_union

from hw2_beam_loads import Segment, PANELS, BEAMS
from hw2_mixed_supports import partition, EDGE_CASES, SUPPORTS

ROOT = Path(__file__).resolve().parent


def main():
    checks=[]
    def check(label, actual, expected, tol=1e-8):
        checks.append(dict(check=label,actual=actual,expected=expected,tolerance=tol,
                           status="PASS" if abs(actual-expected)<=tol else "FAIL"))
    def read(name):
        with (ROOT/name).open(encoding="utf-8-sig",newline="") as stream:
            return list(csv.DictReader(stream))

    # Independent closed-form unit-square benchmarks. Temporary supports never
    # enter the plan or saved schedule.
    ids=["test_bottom","test_left","test_top","test_right"]
    corners=[(0,0,1,0),(0,0,0,1),(0,1,1,1),(1,0,1,1)]
    test=dict(panel_id="test",polygon=[(0,0),(1,0),(1,1),(0,1)],supports=ids)
    try:
        for support,coords in zip(ids,corners):
            SUPPORTS[support]=Segment(support,*coords)
        for condition in ("S","C"):
            EDGE_CASES["test"]={s:condition for s in ids}
            result=partition(test)
            for support in ids:
                check(f"square all-{condition}: {support}",result[support].area,.25)
        EDGE_CASES["test"]={s:"C" if s==ids[0] else "S" for s in ids}
        result=partition(test)
        height=math.sqrt(3)/(1+math.sqrt(3))
        expected=height-height**2/math.sqrt(3)
        check("square mixed continuous edge closed-form area",result[ids[0]].area,expected)
        boundary=result[ids[0]].boundary.intersection(result[ids[1]].boundary)
        check("mixed shared boundary passes through 60 degree ray",boundary.distance(Point(.1,math.sqrt(3)*.1)),0)
        check("mixed square closure",unary_union(list(result.values())).area,1)
    finally:
        EDGE_CASES.pop("test",None)
        for support in ids:
            SUPPORTS.pop(support,None)

    features=json.loads((ROOT/"Step_04_Closed_Regions.geojson").read_text())["features"]
    resolved=[f for f in features if f["properties"]["support_id"]!="UNRESOLVED"]
    geoms=[shape(f["geometry"]) for f in resolved]
    unresolved=unary_union([shape(f["geometry"]) for f in features if f["properties"]["support_id"]=="UNRESOLVED"])
    combined=unary_union(geoms)
    check("exported resolved polygons overlap",sum(g.area for g in geoms)-combined.area,0)
    check("exported floor area incl unresolved",combined.union(unresolved).area,179.25)
    check("unresolved is not allocated twice",combined.intersection(unresolved).area,0)
    voids=unary_union([box(4.7,10.6,5.75,11.85),box(6,10.6,6.55,11.85),box(4.7,7.45,6.55,10.35)])
    check("O1 O2 S1 excluded",combined.union(unresolved).intersection(voids).area,0)
    check("all exported geometries valid",sum(not shape(f["geometry"]).is_valid for f in features),0)

    # Measure angles from ACTUAL output P3 boundaries, not from drawing labels.
    p3={f["properties"]["support_id"]:shape(f["geometry"]) for f in resolved if f["properties"]["panel_id"]=="P3"}
    # Adjacent independently clipped edges can differ by ~1e-15 m. Check both
    # boundary distances rather than a fragile exact topological intersection.
    for support in ("D16","D11"):
        check("exported P3 mixed 60 degree point on "+support,p3[support].boundary.distance(Point(.5,6.05+math.sqrt(3)*.5)),0)
    for support in ("D16","D12"):
        check("exported P3 matched 45 degree point on "+support,p3[support].boundary.distance(Point(3.1,6.55)),0)

    loads=read("Step_05_Beam_Line_Loads.csv")
    profiles=read("Step_05_Beam_Load_Profiles.csv")
    endpoints=read("Step_05_Beam_Endpoint_Loads.csv")
    check("all 25 beam IDs present",len(set(r["beam_id"] for r in loads) ^ set(r["beam_id"] for r in BEAMS)),0)
    for row in loads:
        beam=row["beam_id"]; length=float(row["span_m"])
        bins=[r for r in profiles if r["beam_id"]==beam]
        ends=[r for r in endpoints if r["beam_id"]==beam]
        intervals=[(float(r["s0_m"]),float(r["s1_m"])) for r in bins]
        gaps=abs(intervals[0][0])+abs(intervals[-1][1]-length)
        gaps+=sum(abs(b-c) for (a,b),(c,d) in zip(intervals,intervals[1:]))
        check(beam+" profile continuous coverage",gaps,0)
        area=sum((b-a)*float(r["tributary_width_m"]) for (a,b),r in zip(intervals,bins))
        area+=sum(float(r["tributary_area_m2"]) for r in ends)
        check(beam+" profile area vs summary",area,float(row["tributary_area_m2"]))
        polygon_area=sum(shape(f["geometry"]).area for f in resolved if f["properties"]["support_id"]==beam)
        check(beam+" polygon area vs summary",polygon_area,float(row["tributary_area_m2"]))
        force=sum((b-a)*float(r["service_kN_m"]) for (a,b),r in zip(intervals,bins))
        force+=sum(float(r["service_kN"]) for r in ends)
        check(beam+" total service force",force,float(row["service_udl_total_load_equiv_kN_m"])*length,1e-7)
        # Independently integrate the piecewise-linear midspan influence function.
        def antiderivative(x):
            return x*x/4 if x<=length/2 else length*x/2-x*x/4-length*length/8
        moment=sum(float(r["service_kN_m"])*(antiderivative(b)-antiderivative(a)) for (a,b),r in zip(intervals,bins))
        check(beam+" midspan influence integration",8*moment/length**2,float(row["service_udl_midspan_moment_equiv_kN_m"]),1e-7)

    # Compare assignment at interior sample points against a separate explicit
    # nearest-point distance formula (not the affine polygon-clipping algorithm).
    wrong=0; tested=0
    for panel in PANELS:
        outputs={f["properties"]["support_id"]:shape(f["geometry"]) for f in resolved if f["properties"]["panel_id"]==panel["panel_id"]}
        bounds=unary_union(list(outputs.values())).bounds
        for i in range(19):
            for j in range(23):
                x=bounds[0]+(bounds[2]-bounds[0])*(i+.371)/19
                y=bounds[1]+(bounds[3]-bounds[1])*(j+.619)/23
                point=Point(x,y)
                if not unary_union(list(outputs.values())).contains(point):
                    continue
                scores=[]
                for support in panel["supports"]:
                    seg=SUPPORTS[support]
                    closest_x=min(max(x,min(seg.x1,seg.x2)),max(seg.x1,seg.x2))
                    closest_y=min(max(y,min(seg.y1,seg.y2)),max(seg.y1,seg.y2))
                    weight=math.sqrt(3) if EDGE_CASES[panel["panel_id"]][support]=="C" and panel["panel_id"] not in {"P4","P6","P8"} else 1
                    scores.append((abs(x-closest_x)+abs(y-closest_y))/weight)
                winner=panel["supports"][min(range(len(scores)),key=lambda k:scores[k])]
                tested+=1
                wrong+=not outputs[winner].buffer(1e-9).covers(point)
    check(f"independent point ownership ({tested} samples)",wrong,0)

    with (ROOT/"Step_04_Independent_Mixed_Verification.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(checks[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(checks)
    failures=[r for r in checks if r["status"]!="PASS"]
    if failures:
        raise SystemExit(str(failures))
    print(f"Independent mixed-support verification: {len(checks)}/{len(checks)} passed")


if __name__=="__main__":
    main()
