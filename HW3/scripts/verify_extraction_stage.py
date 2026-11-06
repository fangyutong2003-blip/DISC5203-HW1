"""Independently inspect exported extraction evidence, without rerunning builders."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
checks=[]


def check(name, condition):
    checks.append({"check":name,"pass":bool(condition)})


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


for item in load("records/Source_Hashes.json"):
    check("source hash "+item["file"],hashlib.sha256((ROOT/item["file"]).read_bytes()).hexdigest()==item["sha256"])
ocr=load("outputs/Plan3/stage02/Dual_OCR.json")
for name, p in ocr["raw_passes"].items():
    check("OCR input hash "+name,hashlib.sha256((ROOT/p["source"]).read_bytes()).hexdigest()==p["sha256"])
    check("OCR boxes "+name,all(len(d["box_px"])==4 for d in p["detections"]))
bars=load("outputs/Plan3/stage03/Bar_Label_Matches.json")
matches=bars["matches"]
check("unique labels",len({m["label"] for m in matches})==len(matches))
check("unique bars",len({m["candidate_id"] for m in matches})==len(matches))
check("all OCR hypotheses matched",{m["label"] for m in matches}=={h["label"] for h in ocr["label_hypotheses"]})
readings={r["detection_id"]:r for h in ocr["label_hypotheses"] for r in h["readings"]}
check("match sizes trace to OCR",all(m["size_mm"]==readings[m["ocr_source"]]["size_mm"] for m in matches))
forest=load("outputs/Plan3/stage04_forest/Forest_Report.json")
check("forest never selected",forest["selected"] is False)
check("feature importance sums to one",abs(sum(forest["feature_importance"].values())-1)<1e-10)
check("forest artifact retained",(ROOT/"outputs/Plan3/stage04_forest/Forest_Never_Selected.joblib").stat().st_size>0)
flags=load("outputs/Plan3/review_package_draft/Flag_Manifest.json")
check("no fictitious reader runs",flags["model_runs"]==[])
for f in flags["flags"]:
    p=ROOT/"outputs/Plan3/review_package_draft"/f["crop"]
    check("crop hash "+f["flag_id"],hashlib.sha256(p.read_bytes()).hexdigest()==f["sha256"])
    with Image.open(p) as image:
        x0,y0,x1,y1=f["crop_bbox_px"]
        check("crop extent "+f["flag_id"],image.size==(x1-x0,y1-y0))
result={"checks":checks,"passed":sum(c["pass"] for c in checks),"total":len(checks),
        "scope":"Artifact integrity and internal consistency only; not independent geometry accuracy or a final HW3 verification.",
        "package_versions":{p:importlib.metadata.version(p) for p in
                            ["numpy","Pillow","opencv-python","scikit-learn","rapidocr-onnxruntime","openseespy"]}}
(ROOT/"records/Extraction_Stage_Verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(f"Artifact verification {result['passed']}/{result['total']} passed")
if result["passed"]!=result["total"]:
    raise SystemExit(1)
