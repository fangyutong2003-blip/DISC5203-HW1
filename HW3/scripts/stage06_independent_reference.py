"""Freeze a separately tuned local OCR/raw-ink reference before scoring readers."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/"outputs/Plan3/independent_reference"
    out.mkdir(parents=True,exist_ok=True)
    frozen=ROOT/"outputs/Plan3/reader_package_v1/Flag_Manifest.json"
    if frozen.exists():
        existing=json.loads(frozen.read_text())
        reference=out/"Reference.json"
        if hashlib.sha256(reference.read_bytes()).hexdigest()!=existing["reference_sha256"]:
            raise ValueError("Frozen reference changed; create a new package revision")
        for f in existing["flags"]:
            if hashlib.sha256((frozen.parent/f["crop"]).read_bytes()).hexdigest()!=f["sha256"]:
                raise ValueError("Frozen crop changed; create a new package revision")
        print("Existing frozen v1 reference and crops verified; no overwrite")
        return
    draft=ROOT/"outputs/Plan3/review_package_draft"
    manifest=json.loads((draft/"Flag_Manifest.json").read_text())
    matches=json.loads((ROOT/"outputs/Plan3/stage03/Bar_Label_Matches.json").read_text())["matches"]
    image=cv2.imread(str(ROOT/"sources/assets/FloorPlan3.png"))
    engine=RapidOCR()
    records=[]
    for f in manifest["flags"]:
        x0,y0,x1,y1=f["crop_bbox_px"]
        crop=image[y0:y1,x0:x1]
        # Independent preprocessing: threshold 180, no hatching kernel, no line removal.
        binary=(cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)>180).astype(np.uint8)*255
        result,_=engine(binary)
        raw=[{"box_px":np.asarray(box).tolist(),"text":text,"confidence":float(conf)} for box,text,conf in (result or [])]
        label=f["candidate_label"]
        readings=[]
        for r in raw:
            text=r["text"].upper().replace(" ","").replace("\u00d7","X")
            m=re.search(re.escape(label)+r"([0-9]{3,4})X([0-9]{3,4})(?![0-9])",text)
            if m and r["confidence"]>=.85:
                readings.append((m[1]+"x"+m[2],r["confidence"]))
        unique=sorted({r[0] for r in readings})
        match=next(m for m in matches if m["label"]==label)
        x,y,w,h=match["bbox_px"]
        # Bbox merely locates the queried wall. The reference examines raw interior
        # ink, not the morphology mask used to generate the continuity flags.
        trim=8
        interior=image[y+trim:y+h-trim,x+trim:x+w-trim]
        ink=cv2.cvtColor(interior,cv2.COLOR_BGR2GRAY)<180
        along=np.mean(ink,axis=0 if match["direction"]=="x" else 1)
        supported=along>.15
        support=float(np.mean(supported))
        continuous=bool(support>=.95)
        known=unique[0] if len(unique)==1 else None
        expected={"label":label if known else None,"size_mm":known,
                  "continuous":continuous if "continuous" in f["asked_fields"] else None}
        resolved=known is not None if "size_mm" in f["asked_fields"] else support>=.95
        records.append({"flag_id":f["flag_id"],"expected":expected,"reference_resolved":resolved,
                        "independent_ocr":raw,"raw_ink_axial_support":support,
                        "threshold":180,"interior_trim_px":trim,
                        "source_crop_sha256":hashlib.sha256(crop.tobytes()).hexdigest(),
                        "crop_bbox_px":f["crop_bbox_px"]})
        cv2.imwrite(str(out/(f["flag_id"]+"_Reference_Input.png")),binary)
    report={"created_utc":datetime.now(timezone.utc).isoformat(),
            "route":"Second classical pass: raw unmarked crops, threshold 180 and independent local OCR; raw interior-ink axial occupancy for continuity.",
            "independence_limits":"Shares OCR engine and query locations with the main pipeline, but uses neither main OCR answers nor hatching morphology masks as reference answers. No VLM response is used. This is a defensible alternative reading, not CAD ground truth or independent human signoff.",
            "records":records}
    (out/"Reference.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("Independent-route reference resolved",sum(r["reference_resolved"] for r in records),"/",len(records))
    if not all(r["reference_resolved"] for r in records):
        raise ValueError("Reference ambiguous; do not freeze/promote readers")
    package=ROOT/"outputs/Plan3/reader_package_v1"
    package.mkdir(parents=True,exist_ok=True)
    for f in manifest["flags"]:
        (package/f["crop"]).write_bytes((draft/f["crop"]).read_bytes())
    instruction=(ROOT/"prompts/Reader_Instructions.md").read_bytes()
    (package/"Reader_Instructions.md").write_bytes(instruction)
    manifest.update(status="FROZEN inputs v1; Task 2 scoring pending",frozen_utc=report["created_utc"],
                    reference_sha256=hashlib.sha256((out/"Reference.json").read_bytes()).hexdigest(),
                    prompt_sha256=hashlib.sha256(instruction).hexdigest())
    (package/"Flag_Manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    questions=["# Frozen reader questions v1","","Read Reader_Instructions.md first. Answer each question in this order.",""]
    for f in manifest["flags"]:
        questions += ["## "+f["flag_id"],"",f["question"],"",f"![{f['flag_id']}]({f['crop']})",""]
    (package/"Questions.md").write_text("\n".join(questions),encoding="utf-8")
    print("Frozen identical-reader package:",package)


if __name__=="__main__":
    main()
