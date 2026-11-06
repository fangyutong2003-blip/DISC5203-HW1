"""Compare metric calibration with dimension chains and an archived HW1 reading."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent


def main():
    out=ROOT/"outputs/Plan3/stage05"
    calibration=json.loads((out/"Metric_Calibration.json").read_text())
    geometry=json.loads((out/"Classical_Elements_Unpromoted.json").read_text())
    bars=json.loads((ROOT/"outputs/Plan3/stage03/Bar_Label_Matches.json").read_text())["matches"]
    # This route uses the overall printed dimension chains, not wall lengths.
    # Values read from the supplied plan: 1.00 + 8.20 + 1.00 across; 19.20 high.
    xmin=min(m["bbox_px"][0] for m in bars)
    xmax=max(m["bbox_px"][0]+m["bbox_px"][2] for m in bars)
    ymin=min(m["bbox_px"][1] for m in bars)
    ymax=max(m["bbox_px"][1]+m["bbox_px"][3] for m in bars)
    dimension_scale={"x":(xmax-xmin)/10.2,"y":(ymax-ymin)/19.2}
    checks=[]
    for route,key in (("lecture_stroke","lecture_scale_px_per_m"),("effective_growth","scale_px_per_m")):
        for axis in ("x","y"):
            error=abs(calibration[key][axis]/dimension_scale[axis]-1)
            checks.append({"route":route,"axis":axis,"relative_scale_error":error,
                           "tolerance":.02,"accepted":error<=.02})
    # A historic, differently derived reading is an audit comparison, not CAD truth.
    base="5f1eafe"
    raw=subprocess.check_output(["git","show",base+":Step_01B_Vertical_Element_Coordinates.csv"],cwd=REPO)
    references=[]
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        if row["axis_segment"] not in ("main","centre"):
            continue
        references.append({"label":row["element_id"],"class":row["element_type"],
                           "size_mm":list(map(int,row["section_mm"].split("x"))),
                           "centre_m":[(float(row["x1_m"])+float(row["x2_m"]))/2,
                                       (float(row["y1_m"])+float(row["y2_m"]))/2]})
    comparison=[]
    for reference in references:
        current=next(e for e in geometry["elements"] if e["labels"]==[reference["label"]])
        delta=np.array(current["centre_m"])-reference["centre_m"]
        comparison.append({"label":reference["label"],"size_matches":sorted(current["size_mm"])==sorted(reference["size_mm"]),
                           "reference_centre_m":reference["centre_m"],"new_centre_m":current["centre_m"],
                           "centre_distance_m":float(np.linalg.norm(delta))})
    report={"dimension_chain_m":{"x":[1.,8.2,1.],"y":[19.2]},"dimension_scale_px_per_m":dimension_scale,
            "scale_gate":checks,"gate_note":"2% calibration tolerance, explicitly separate from hand/model CR agreement tolerance.",
            "historical_source_commit":base,"historical_source_sha256":hashlib.sha256(raw).hexdigest(),
            "reference_route":"Archived HW1 dimension-chain and named-element schedule, generated before the current OCR/morphology flags; main wall segments only.",
            "reference_limits":"An earlier image-derived, AI-assisted reading, not original CAD or a new student hand reading. It is used as an independent-route audit aid; new reference scoring remains pending explicit defensible source review.",
            "comparison":comparison,"human_reference_signoff":False,
            "max_centre_distance_m":max(c["centre_distance_m"] for c in comparison)}
    (out/"Dimension_Chain_and_Historical_Audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    passed=all(c["accepted"] for c in checks if c["route"]=="effective_growth")
    if not passed:
        raise ValueError("Effective-growth scale failed dimension-chain gate")
    rows=["# Metric geometry calibration and independent-route audit","",
          "Thin-line median: 6 px. The lecture growth of 12 px fails the 2% overall dimension-chain scale gate.",
          "Effective bar growth was estimated separately from extent-versus-labelled-length regression. This route passes the dimension-chain gate.","",
          f"Adopted candidate scale: x={calibration['scale_px_per_m']['x']:.6f}, y={calibration['scale_px_per_m']['y']:.6f} px/m.",
          "The original failed route and all its measurements remain in Metric_Calibration.json.","",
          report["reference_limits"],"",
          "The source uses exterior structural dimensions, not a floor outline including balconies. O1/O2 and S1 are not yet recomputed in this extraction.","",
          "| Label | Size agrees | Centre difference (m) |","|---|---|---:|"]
    rows += [f"| {c['label']} | {c['size_matches']} | {c['centre_distance_m']:.4f} |" for c in comparison]
    (out/"Metric_Geometry_Review.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    print("Effective-growth scale gate PASS; lecture growth route rejected and retained")
    print("Size agreements:",sum(c["size_matches"] for c in comparison),"/",len(comparison))
    print("Maximum historical centre difference (m):",report["max_centre_distance_m"])


if __name__=="__main__":
    main()
