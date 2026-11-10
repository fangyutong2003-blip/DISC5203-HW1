"""Split concrete candidates into directional bars and match unique OCR labels."""
import json
from pathlib import Path
import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
from plan_context import context

ROOT = Path(__file__).resolve().parents[1]


def main():
    plan, source, output = context()
    out = output / "stage03"
    out.mkdir(parents=True, exist_ok=True)
    initial = json.loads((output / "stage01/Classical_Components.json").read_text())
    ocr = json.loads((output / "stage02/Dual_OCR.json").read_text())
    mask = cv2.imread(str(output / "stage01/04_Open21.png"), 0)
    grey = cv2.imread(str(source), 0)
    candidates = []
    for direction, kernel in (("x", np.ones((1, 121), np.uint8)),
                              ("y", np.ones((121, 1), np.uint8))):
        bars = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        cv2.imwrite(str(out / f"Bars_{direction}.png"), bars)
        n, _, stats, centres = cv2.connectedComponentsWithStats(bars, 8)
        for i in range(1, n):
            x, y, w, h, area = map(int, stats[i])
            if min(x, y) <= 2 or x+w >= mask.shape[1]-2 or y+h >= mask.shape[0]-2:
                continue
            if max(w, h)/min(w, h) < 3:
                continue
            candidates.append({"candidate_id": len(candidates)+1, "class": "wall",
                               "direction": direction, "bbox_px": [x, y, w, h],
                               "centre_px": centres[i].tolist()})
    for item in initial["components"]:
        x, y, w, h = item["bbox_px"]
        if .65 <= w/h <= 1.55 and item["area_px"] > 1000:
            candidates.append({"candidate_id": len(candidates)+1, "class": "column",
                               "direction": None, "bbox_px": [x, y, w, h],
                               "centre_px": item["centroid_px"]})
    labels = ocr["label_hypotheses"]
    # Use square-column sizes to estimate scale without a pre-existing metric schedule.
    column_widths = [np.mean(c["bbox_px"][2:]) for c in candidates if c["class"] == "column"]
    printed_columns = [h["readings"][0]["size_mm"][0]/1000 for h in labels if h["label"].startswith("C")]
    scale_seed = float(np.median(column_widths)/np.median(printed_columns)) if column_widths and printed_columns else None
    cost = np.full((len(labels), len(candidates)), 1e9)
    for i, label in enumerate(labels):
        if scale_seed is None:
            continue
        readings = label["readings"]
        best = max(readings, key=lambda r: r["confidence"])
        a, b = best["size_mm"]
        text_centre = np.mean(best["box_px"], axis=0)
        kind = "column" if label["label"].startswith("C") else "wall"
        for j, candidate in enumerate(candidates):
            if candidate["class"] != kind:
                continue
            x, y, w, h = candidate["bbox_px"]
            thickness = min(w, h)
            expected_thickness = min(a, b)/1000*scale_seed
            mismatch = abs(thickness-expected_thickness)/expected_thickness
            nominal_classes=sorted({min(h["readings"][0]["size_mm"]) for h in labels})
            observed_class=min(nominal_classes,key=lambda c:abs(thickness/scale_seed*1000-c))
            if observed_class!=min(a,b):
                continue
            if mismatch > .45:
                continue
            distance = np.linalg.norm(np.array(candidate["centre_px"])-text_centre)
            cost[i, j] = distance + 300*mismatch
    rows, cols = linear_sum_assignment(cost)
    matched = []
    for i, j in zip(rows, cols):
        if cost[i, j] >= 1e8:
            continue
        label, bar = labels[i], candidates[j]
        best = max(label["readings"], key=lambda r:r["confidence"])
        matched.append({**bar, "label": label["label"], "size_mm": best["size_mm"],
                        "ocr_source": best["detection_id"], "match_cost_px": float(cost[i, j]),
                        "status": "provisional; independent reference and extent support pending"})
    overlay = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
    for item in matched:
        x,y,w,h = item["bbox_px"]
        cv2.rectangle(overlay,(x,y),(x+w,y+h),(255,0,0),3)
        cv2.putText(overlay,item["label"],(x,y-5),cv2.FONT_HERSHEY_SIMPLEX,.8,(255,0,0),2)
    cv2.imwrite(str(out / "Provisional_Label_Matches.png"),overlay)
    result = {"scale_seed_px_per_m": scale_seed,
              "scale_note": "Provisional square-column median; stroke growth NOT yet subtracted. Not final label-derived scale." if scale_seed is not None else "No scale seed: square-column pixel widths or printed column sizes absent. No fabricated size or matching fallback.",
              "thickness_gate_relative": .45, "directional_opening_px": 121,
              "candidates": candidates, "matches": matched,
              "unmatched_labels": sorted({l["label"] for l in labels}-{m["label"] for m in matched}),
              "unclaimed_candidates": [c["candidate_id"] for c in candidates if c["candidate_id"] not in {m["candidate_id"] for m in matched}]}
    (out / "Bar_Label_Matches.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    assert len({m["candidate_id"] for m in matched}) == len(matched)
    assert len({m["label"] for m in matched}) == len(matched)
    print(f"PASS: unique claims; {len(candidates)} candidates, {len(matched)} provisional matches")
    print("Unmatched labels:",result["unmatched_labels"])
    print("Scale seed, NOT final:",round(scale_seed,3) if scale_seed is not None else None)


if __name__ == "__main__":
    main()
