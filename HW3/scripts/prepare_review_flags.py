"""Prepare review crops from recorded classical uncertainties, before reference scoring."""
import hashlib
import json
from pathlib import Path
import cv2

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT / "outputs/Plan3/review_package_draft"
    out.mkdir(parents=True,exist_ok=True)
    image=cv2.imread(str(ROOT / "sources/assets/FloorPlan3.png"))
    bars=json.loads((ROOT / "outputs/Plan3/stage03/Bar_Label_Matches.json").read_text())
    ocr=json.loads((ROOT / "outputs/Plan3/stage02/Dual_OCR.json").read_text())
    original=json.loads((ROOT / "outputs/Plan3/stage01/Classical_Components.json").read_text())
    # Component containment identifies merged groups without a hardcoded list of walls.
    groups={}
    for m in bars["matches"]:
        cx,cy=m["centre_px"]
        for component in original["components"]:
            x,y,w,h=component["bbox_px"]
            if x<=cx<=x+w and y<=cy<=y+h:
                groups.setdefault(component["component_id"],[]).append(m["label"])
    merged={label for group in groups.values() if len(group)>1 for label in group}
    hypotheses={h["label"]:h for h in ocr["label_hypotheses"]}
    flags=[]
    for m in sorted(bars["matches"],key=lambda i:i["label"]):
        readings=hypotheses[m["label"]]["readings"]
        single=len({r["source"] for r in readings})<2
        if not single and m["label"] not in merged:
            continue
        fid=f"P3-F{len(flags)+1:02d}"
        cx,cy=map(int,m["centre_px"])
        # Fixed pixel crop; not a metric measurement while final scale is pending.
        half=440
        x0=max(0,cx-half); y0=max(0,cy-half)
        x1=min(image.shape[1],cx+half); y1=min(image.shape[0],cy+half)
        crop=image[y0:y1,x0:x1].copy()
        cv2.drawMarker(crop,(cx-x0,cy-y0),(0,0,255),cv2.MARKER_CROSS,30,2)
        path=out / (fid+".png")
        cv2.imwrite(str(path),crop)
        question=(f"What element label and size string are printed beside the element at the red cross?"
                  if single else
                  "Is the hatched wall through the red cross continuous along its axis, or is there a genuine gap in the concrete?")
        flags.append({"flag_id":fid,"candidate_label":m["label"],
                      "flag": "single_pass_label_reading" if single else "merged_component_continuity_review",
                      "source":"recorded dual OCR / classical component containment",
                      "crop":path.name,"crop_bbox_px":[x0,y0,x1,y1],
                      "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                      "question":question,"asked_fields":["label","size_mm"] if single else ["continuous"]})
    record={"status":"DRAFT - independent reference must be frozen before reader runs",
            "model_runs":[],"confidence_threshold":.8,
            "threshold_note":"Confidence alone does not establish correctness; independent reference agreement is required.",
            "flags":flags}
    (out / "Flag_Manifest.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    rows=["# Draft review package", "",record["status"],"",
          "Use prompts/Reader_Instructions.md for both readers. Send only the crop and question below, not the independent reference or geometry match answers.",""]
    for f in flags:
        rows.extend(["## "+f["flag_id"],"",f["question"],"",f"![{f['flag_id']}]({f['crop']})",""])
    (out / "Questions.md").write_text("\n".join(rows),encoding="utf-8")
    print(f"Prepared {len(flags)} draft flags with source provenance and crop hashes")


if __name__ == "__main__":
    main()
