"""Preserve Task 1A image evidence without inventing labels or coordinates."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from plan_context import context

ROOT = Path(__file__).resolve().parents[1]


def main():
    plan, source, output = context()
    out = output / "stage01"
    out.mkdir(parents=True, exist_ok=True)
    hashes = []
    for path in sorted((ROOT / "sources").rglob("*")):
        if path.is_file():
            hashes.append({"file": path.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    hash_target = ROOT / "records" / "Source_Hashes.json" if plan == "Plan3" and output.name == "Plan3" else out / "Source_Hashes.json"
    hash_target.write_text(
        json.dumps(hashes, indent=2), encoding="utf-8")
    grey = cv2.imread(str(source), cv2.IMREAD_GRAYSCALE)
    if grey is None:
        raise ValueError("Cannot read source image")
    ink = (grey < 225).astype(np.uint8) * 255
    # Both diagonal directions are retained separately to make orientation explicit.
    diagonal = np.fliplr(np.eye(11, dtype=np.uint8)).copy()
    hatch = cv2.morphologyEx(ink, cv2.MORPH_OPEN, diagonal)
    closed = cv2.morphologyEx(hatch, cv2.MORPH_CLOSE, np.ones((17, 17), np.uint8))
    mask = cv2.morphologyEx(closed, cv2.MORPH_OPEN, np.ones((21, 21), np.uint8))
    opened17 = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((17, 17), np.uint8))
    horizontal = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((1, 81), np.uint8))
    vertical = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((81, 1), np.uint8))
    no_lines = cv2.bitwise_not(cv2.subtract(ink, cv2.bitwise_or(horizontal, vertical)))
    images = {"01_Threshold": ink, "02_Diagonal_Hatching": hatch,
              "03_Close17": closed, "04_Open21": mask,
              "05_Open17_Alternative": opened17, "06_OCR_Long_Lines_Removed": no_lines}
    for name, image in images.items():
        if not cv2.imwrite(str(out / (name + ".png")), image):
            raise IOError(name)
    count, components, stats, centres = cv2.connectedComponentsWithStats(mask, 8)
    overlay = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
    records = []
    for idx in range(1, count):
        x, y, w, h, area = map(int, stats[idx])
        ratio = max(w, h) / min(w, h)
        kind = "wall_candidate" if ratio >= 4 else "column_candidate"
        records.append({"component_id": idx, "bbox_px": [x, y, w, h],
                        "centroid_px": centres[idx].tolist(), "area_px": area,
                        "aspect_ratio": ratio, "shape_rule_class": kind,
                        "labels": [], "status": "unmatched; not a named element"})
        cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.putText(overlay, str(idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2)
    cv2.imwrite(str(out / "07_Component_Overlay.png"), overlay)
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": source.relative_to(ROOT).as_posix(), "image_shape_hw": list(grey.shape),
        "parameters": {"ink_less_than": 225, "diagonal_line_px": 11,
                       "close_square_px": 17, "open_square_px": 21,
                       "wall_aspect_ratio": 4, "long_line_kernel_px": 81},
        "parameter_note": "Close17/open21 follows L09's L07 recap. The brief says open17/open21; the open17 alternative is also preserved. No tuning to reference labels has occurred.",
        "scale_px_per_m": {"x": None, "y": None},
        "components": records,
        "score_sheet": {"component_count": count-1, "named_elements_found": None,
                        "merged": None, "broken": None,
                        "reason": "Label matching and independent reference are pending."},
        "pending": ["dual OCR", "bar/label matching", "label-derived scale",
                    "independent reference", "frozen flags", "random forest", "two VLM runs"],
    }
    (out / "Classical_Components.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert ink.shape == mask.shape == grey.shape
    assert set(np.unique(mask)).issubset({0, 255})
    assert sum(r["area_px"] for r in records) == int(np.count_nonzero(mask))
    print(f"PASS: source shape, binary mask and component area closure; {count-1} components")
    print("Named elements, scale and merge/break scores remain unscored until label matching.")


if __name__ == "__main__":
    main()
