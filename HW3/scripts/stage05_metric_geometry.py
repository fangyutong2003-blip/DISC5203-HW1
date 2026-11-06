"""Measure line growth and directional scale, then export labelled rectangles."""
import json
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def measure_strokes(ink):
    lines=cv2.HoughLinesP(ink,1,np.pi/180,150,minLineLength=250,maxLineGap=8)
    records=[]
    for line in ([] if lines is None else np.asarray(lines).reshape(-1,4)):
        x0,y0,x1,y1=map(int,line)
        horizontal=abs(y1-y0)<=1
        vertical=abs(x1-x0)<=1
        if not (horizontal or vertical):
            continue
        for alpha in (.25,.5,.75):
            x=int(round(x0+alpha*(x1-x0))); y=int(round(y0+alpha*(y1-y0)))
            if not ink[y,x]:
                continue
            dx,dy=(0,1) if horizontal else (1,0)
            lengths=[]
            for sign in (-1,1):
                n=0
                for offset in range(1,20):
                    xx=x+sign*dx*offset; yy=y+sign*dy*offset
                    if not (0<=xx<ink.shape[1] and 0<=yy<ink.shape[0]) or not ink[yy,xx]:
                        break
                    n+=1
                lengths.append(n)
            width=1+sum(lengths)
            if 1<=width<=12:
                records.append({"point_px":[x,y],"orientation":"horizontal" if horizontal else "vertical",
                                "stroke_width_px":width})
    if not records:
        raise ValueError("No independent thin-line widths measured")
    return records


def main():
    out=ROOT/"outputs/Plan3/stage05"
    out.mkdir(parents=True,exist_ok=True)
    image=cv2.imread(str(ROOT/"sources/assets/FloorPlan3.png"))
    ink=(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)<225).astype(np.uint8)*255
    data=json.loads((ROOT/"outputs/Plan3/stage03/Bar_Label_Matches.json").read_text())
    strokes=measure_strokes(ink)
    width=float(np.median([r["stroke_width_px"] for r in strokes]))
    growth=2*width
    measurements=[]
    for m in data["matches"]:
        if m["class"]!="wall":
            continue
        x,y,w,h=m["bbox_px"]
        extent=w if m["direction"]=="x" else h
        length=max(m["size_mm"])/1000
        measurements.append({"label":m["label"],"axis":m["direction"],"extent_px":extent,
                             "labelled_length_m":length,"scale_px_per_m":(extent-growth)/length})
    lecture_scales={axis:float(np.median([m["scale_px_per_m"] for m in measurements if m["axis"]==axis])) for axis in ("x","y")}
    # Measure effective bar growth across different labelled lengths. This is a
    # separate calibration route, not a hidden adjustment of the thin-line rule.
    regression={}
    for axis in ("x","y"):
        rows=[m for m in measurements if m["axis"]==axis]
        slope,intercept=np.polyfit([m["labelled_length_m"] for m in rows],[m["extent_px"] for m in rows],1)
        regression[axis]={"slope_px_per_m":float(slope),"growth_px":float(intercept)}
    scales={axis:float(np.median([(m["extent_px"]-regression[axis]["growth_px"])/m["labelled_length_m"] for m in measurements if m["axis"]==axis])) for axis in ("x","y")}
    # Exterior structural datum, not the bounding box of all ink/dimension annotations.
    left=min(m["bbox_px"][0] for m in data["matches"])
    bottom=max(m["bbox_px"][1]+m["bbox_px"][3] for m in data["matches"])
    origin=[left+regression["x"]["growth_px"]/2,bottom-regression["y"]["growth_px"]/2]
    elements=[]
    diagnostics=[]
    overlay=image.copy()
    for m in data["matches"]:
        x,y,w,h=m["bbox_px"]
        # Geometry centre of the bar box avoids hatching's uneven ink centroid.
        cx=x+w/2; cy=y+h/2
        a,b=m["size_mm"]
        if m["class"]=="wall":
            thick=min(a,b)/1000; length=max(a,b)/1000
            wm,hm=(length,thick) if m["direction"]=="x" else (thick,length)
        else:
            wm,hm=a/1000,b/1000
        pw=wm*scales["x"]; ph=hm*scales["y"]
        x0=int(round(cx-pw/2)); x1=int(round(cx+pw/2))
        y0=int(round(cy-ph/2)); y1=int(round(cy+ph/2))
        roi=ink[max(0,y0):min(ink.shape[0],y1+1),max(0,x0):min(ink.shape[1],x1+1)]
        # Axial coverage asks whether ink supports each length station; not area IoU.
        axis=0 if m["direction"]=="x" else 1
        support=float(np.mean(np.any(roi>0,axis=axis))) if roi.size else 0
        flags=[]
        if support<.85: flags.append("low_axial_ink_support")
        diagnostics.append({"label":m["label"],"axial_ink_support":support,"threshold":.85,
                            "note":"Ink coverage can include lines; this is not an independent concrete check."})
        element={"id":len(elements)+1,"labels":[m["label"]],"class":m["class"],
                 "centre_m":[(cx-origin[0])/scales["x"],(origin[1]-cy)/scales["y"]],
                 "size_mm":m["size_mm"],"audit":{"flags":flags,"source":"dual OCR + directional bar pixels",
                 "status":"unpromoted classical extraction; independent reference and VLM review pending"}}
        if m["class"]=="wall":
            element.update(angle_deg=0. if m["direction"]=="x" else 90.,continuous=None)
        elements.append(element)
        cv2.rectangle(overlay,(x0,y0),(x1,y1),(0,170,0),2)
        cv2.putText(overlay,m["label"],(x0,y0-4),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,120,0),2)
    geometry={"source":{"file":"FloorPlan3.png"},"scale_px_per_m":scales,"elements":elements,
              "floor":{"outline_area_m2":None,"load_kN_m2":8.75,"storeys":5},
              "checks":{"sum_areas_m2":None,"sum_axial_kN":None},
              "status":"unpromoted classical candidate; floor extraction pending"}
    record={"stroke_samples":strokes,"median_stroke_width_px":width,"lecture_growth_px":growth,
            "lecture_scale_px_per_m":lecture_scales,
            "growth_assumption":"Lecture route uses two measured thin-line widths. Separately, effective bar growth is estimated as the intercept of extent versus labelled length. Both retained; choose only after a dimension-chain check.",
            "effective_growth_regression":regression,
            "scale_measurements":measurements,"scale_px_per_m":scales,"origin_px":origin,
            "origin_definition":"Bottom-left exterior structural datum, offset inward by half the effective-growth intercept from candidate extent; balconies may have negative coordinates.",
            "support_diagnostics":diagnostics,
            "scale_sensitivity_growth_zero":{axis:float(np.median([m["extent_px"]/m["labelled_length_m"] for m in measurements if m["axis"]==axis])) for axis in ("x","y")}}
    for name,obj in (("Classical_Elements_Unpromoted.json",geometry),("Metric_Calibration.json",record)):
        (out/name).write_text(json.dumps(obj,indent=2),encoding="utf-8")
    cv2.imwrite(str(out/"Labelled_Size_Rectangles.png"),overlay)
    print("Measured stroke width:",width,"growth:",growth,"scales:",scales,"origin:",origin)
    print("Elements:",len(elements),"low-support flags:",sum(bool(e["audit"]["flags"]) for e in elements))


if __name__=="__main__":
    main()
