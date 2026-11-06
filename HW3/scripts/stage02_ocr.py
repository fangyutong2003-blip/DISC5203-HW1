"""Run two OCR readings and preserve unedited detections and label hypotheses."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / "outputs" / "Plan3" / "stage02"
    out.mkdir(parents=True, exist_ok=True)
    engine = RapidOCR()
    inputs = {
        "original": ROOT / "sources/assets/FloorPlan3.png",
        "lines_removed": ROOT / "outputs/Plan3/stage01/06_OCR_Long_Lines_Removed.png",
    }
    raw = {}
    candidates = []
    for name, path in inputs.items():
        result, elapsed = engine(str(path))
        detections = []
        for idx, (box, text, confidence) in enumerate(result or []):
            item = {"detection_id": f"{name}_{idx:03d}", "box_px": np.asarray(box).tolist(),
                    "text": text, "confidence": float(confidence)}
            detections.append(item)
            # Only explicit OCR text is parsed. No historical label schedule is loaded.
            normalized = text.upper().replace(" ", "").replace("\u00d7", "X")
            match = re.search(r"([CT])([0-9]+)X([0-9]{3,4})(?![0-9])", normalized)
            parses = []
            spaced = re.search(r"([CT][0-9]{1,2})\s+([0-9]{3,4})[X\u00d7]([0-9]{3,4})", text.upper())
            if match:
                digits = match[2]
                for cut in (1, 2):
                    if len(digits[cut:]) not in (3, 4):
                        continue
                    a, b = int(digits[cut:]), int(match[3])
                    if min(a, b) >= 100 and min(a, b) <= 1000:
                        parses.append((match[1]+digits[:cut], [a, b]))
            if spaced:
                parses = [(spaced[1], [int(spaced[2]), int(spaced[3])])]
            if len(parses) == 1:
                label, size = parses[0]
                candidates.append({"label": label,
                                   "size_mm": size,
                                   "source": name, "detection_id": item["detection_id"],
                                   "box_px": item["box_px"], "raw_text": text,
                                   "confidence": float(confidence)})
        raw[name] = {"source": path.relative_to(ROOT).as_posix(),
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "detections": detections, "elapsed_seconds": list(map(float, elapsed))}
        print(name, len(detections), "raw OCR detections", flush=True)
    by_label = {}
    for item in candidates:
        by_label.setdefault(item["label"], []).append(item)
    hypotheses = []
    for label, items in sorted(by_label.items()):
        sizes = {tuple(i["size_mm"]) for i in items}
        hypotheses.append({"label": label, "readings": items,
                           "size_disagreement": len(sizes) > 1,
                           "status": "OCR hypothesis; bar association and reference not yet checked"})
    record = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "engine": "RapidOCR ONNX 1.4.4; local text detection/recognition",
              "method_note": "OCR transcription only; this is not a VLM flag-resolution run.",
              "raw_passes": raw, "label_hypotheses": hypotheses,
              "named_hypotheses": len(hypotheses),
              "pending": ["bar matching", "scale from labelled lengths and measured growth",
                          "independent reference", "frozen reader flags"]}
    (out / "Dual_OCR.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    rows = ["# Task 1B - Dual OCR evidence", "",
            "Raw text, boxes, confidence and source hashes are retained in Dual_OCR.json.",
            "These are OCR hypotheses, not accepted structural elements.", "",
            "| Label | Read sizes (mm) | Disagreement |", "|---|---|---|"]
    for item in hypotheses:
        sizes = sorted({"x".join(map(str, i["size_mm"])) for i in item["readings"]})
        rows.append(f"| {item['label']} | {', '.join(sizes)} | {item['size_disagreement']} |")
    (out / "Dual_OCR_Review.md").write_text("\n".join(rows)+"\n", encoding="utf-8")
    print("OCR label hypotheses:", len(hypotheses), flush=True)


if __name__ == "__main__":
    main()
