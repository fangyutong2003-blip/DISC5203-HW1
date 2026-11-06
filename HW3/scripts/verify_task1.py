"""Check Task 1 delivery from saved artifacts, including explicit residual warnings."""
import hashlib
import json
from pathlib import Path
import numpy as np
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/Plan3"
checks=[]


def load(p):return json.loads((OUT/p).read_text(encoding="utf-8"))
def check(name,ok):checks.append({"check":name,"pass":bool(ok)})


base=load("task1/Elements_Classical.json")
after=load("task1/Elements_After_Reader_A.json")
floor=load("task1/Floor_Dimension_Record.json")
check("required root schema",set(base)=={"source","scale_px_per_m","elements","floor","checks"})
check("21 unique named elements",len(base["elements"])==len({e["labels"][0] for e in base["elements"]})==21)
check("nine columns and twelve walls",sum(e["class"]=="column" for e in base["elements"])==9 and sum(e["class"]=="wall" for e in base["elements"])==12)
for a,b in zip(base["elements"],after["elements"]):
    check("reader keeps measured centre "+a["labels"][0],a["centre_m"]==b["centre_m"])
    check("audit provenance "+a["labels"][0],bool(a["audit"]["source"]) and "merged" in a["audit"] and "partly_missed" in a["audit"])
zones={f["properties"]["zone"]:shape(f["geometry"]) for f in load("task1/Floor_Zones.geojson")["features"]}
regions=[shape(f["geometry"]) for f in load("task1/Closed_Tributary_Regions.geojson")["features"]]
check("regions valid and closed",all(g.is_valid for g in regions))
check("no tributary overlap",abs(sum(g.area for g in regions)-unary_union(regions).area)<1e-7)
check("no ordinary slab gaps",unary_union(regions).symmetric_difference(zones["ordinary_flat_slab"]).area<1e-7)
check("ordinary excludes both voids and stair",zones["ordinary_flat_slab"].intersection(zones["voids"].union(zones["separate_stair"])).area<1e-8)
check("floor decomposition",abs(floor["ordinary_flat_area_m2"]+floor["void_area_m2"]+floor["separate_stair_area_m2"]-floor["gross_area_m2"])<1e-8)
check("raster area matches polygons",abs(base["checks"]["sum_areas_m2"]-sum(g.area for g in regions))<1e-7)
check("scoped axial total",abs(base["checks"]["sum_axial_kN"]-5*8.75*zones["ordinary_flat_slab"].area)<1e-6)
package=load("reader_package_v1/Flag_Manifest.json")
ref_file=OUT/"independent_reference/Reference.json"
check("reference frozen hash",hashlib.sha256(ref_file.read_bytes()).hexdigest()==package["reference_sha256"])
answers=load("reader_A_task1/Raw_Answers.json")
refs={r["flag_id"]:r for r in load("independent_reference/Reference.json")["records"]}
check("actual answers in flag order",[a["flag_id"] for a in answers]==[f["flag_id"] for f in package["flags"]])
for f,a in zip(package["flags"],answers):
    check("question/crop hash "+f["flag_id"],hashlib.sha256((OUT/"reader_package_v1"/f["crop"]).read_bytes()).hexdigest()==f["sha256"])
    check("asked fields agree with reference "+f["flag_id"],all(a[k]==refs[f["flag_id"]]["expected"][k] for k in f["asked_fields"]))
check("original preserved hash",hashlib.sha256((OUT/"task1/Elements_Classical.json").read_bytes()).hexdigest()==load("reader_A_task1/Application_Log.json")["original_sha256"])
check("no Task2 promotion",load("reader_A_task1/Run_Metadata.json")["model_promoted"] is False)
forest=load("stage04_forest/Forest_Report.json")
check("forest trained but never chosen",forest["selected"] is False and forest["trees"]==60 and forest["training_pixels"]==120000)
check("feature scores sum one",abs(sum(forest["feature_importance"].values())-1)<1e-10)
warnings=load("task1/Element_Geometry_Audit.json")
check("all adopted footprints inside floor",all(e["outside_m2"]<1e-6 for e in warnings["elements"]))
check("hatch completion support at least 85 percent",all(e["hatch_axial_support"]>=.85 for e in warnings["elements"]))
anchor=load("task1/Global_Dimension_Anchor.json")
check("final schema scale uses declared global anchor",base["scale_px_per_m"]==anchor["adopted_scale_px_per_m"])
report={"passed":sum(c["pass"] for c in checks),"total":len(checks),"checks":checks,
        "known_geometry_warnings":[e for e in warnings["elements"] if e["outside_m2"]>1e-6 or e["hatch_axial_support"]<.85],
        "scope":"Task 1 pipeline/artifact consistency. Passing checks do not erase explicitly listed geometry warnings or establish a Task 2 model winner."}
(ROOT/"records/Task1_Verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(f"Task 1 verification: {report['passed']}/{report['total']}; residual geometry warnings: {len(report['known_geometry_warnings'])}")
if report["passed"]!=report["total"]:raise SystemExit(1)
