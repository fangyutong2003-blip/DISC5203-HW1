"""Retain a weakly supervised forest; never promote its pixel extraction."""
import json
import time
from pathlib import Path
import cv2
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[1]


def features(grey):
    ink = (grey < 225).astype(np.float32)
    data = [grey.astype(np.float32)/255,
            cv2.magnitude(cv2.Sobel(grey, cv2.CV_32F, 1, 0), cv2.Sobel(grey, cv2.CV_32F, 0, 1))/1024]
    names = ["grey", "edge_strength"]
    for n in (5, 9, 17):
        data.append(cv2.blur(ink, (n,n))); names.append(f"ink_density_{n}")
        kernel = np.fliplr(np.eye(n,dtype=np.float32)).copy()/n
        data.append(cv2.filter2D(ink,-1,kernel)); names.append(f"diagonal_45_{n}")
    for sigma in (1,2,4,8):
        data.append(cv2.GaussianBlur(ink,(0,0),sigma)); names.append(f"blur_{sigma}")
    for n, shape in ((9,(1,9)),(17,(1,17)),(17,(17,1))):
        data.append(cv2.blur(ink,shape)); names.append(f"directional_{shape[0]}_{shape[1]}")
    return np.stack(data,axis=-1).reshape(-1,len(names)), names


def main():
    out = ROOT / "outputs/Plan3/stage04_forest"
    out.mkdir(parents=True,exist_ok=True)
    grey = cv2.imread(str(ROOT / "sources/assets/FloorPlan3.png"),0)
    mask = cv2.imread(str(ROOT / "outputs/Plan3/stage01/04_Open21.png"),0)
    # Preliminary experiment at 50% image size, explicitly not a held-out evaluation.
    grey = cv2.resize(grey,None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA)
    mask = cv2.resize(mask,(grey.shape[1],grey.shape[0]),interpolation=cv2.INTER_NEAREST)>0
    X,names = features(grey)
    y = mask.ravel().astype(np.uint8)
    rng = np.random.default_rng(5203)
    pos = np.flatnonzero(y)
    near_ink = cv2.dilate((grey<225).astype(np.uint8),np.ones((17,17),np.uint8)).ravel()>0
    hard = np.flatnonzero((y==0)&near_ink)
    easy = np.flatnonzero((y==0)&~near_ink)
    idx = np.concatenate([rng.choice(pos,min(40000,len(pos)),replace=False),
                          rng.choice(hard,min(60000,len(hard)),replace=False),
                          rng.choice(easy,min(20000,len(easy)),replace=False)])
    start=time.perf_counter()
    forest=RandomForestClassifier(n_estimators=60,n_jobs=2,random_state=5203)
    forest.fit(X[idx],y[idx])
    elapsed=time.perf_counter()-start
    joblib.dump({"model":forest,"features":names,"selected":False},out / "Forest_Never_Selected.joblib",compress=3)
    probability=np.empty(len(X),dtype=np.float32)
    for begin in range(0,len(X),100000):
        probability[begin:begin+100000]=forest.predict_proba(X[begin:begin+100000])[:,1]
    cv2.imwrite(str(out / "Forest_Probability.png"),(probability.reshape(grey.shape)*255).astype(np.uint8))
    cv2.imwrite(str(out / "Forest_Mask_Never_Selected.png"),(probability.reshape(grey.shape)>.5).astype(np.uint8)*255)
    record={"selected":False,"selection_reason":"Labels copy the classical rules, including merges and artifacts.",
            "stage":"preliminary weak-label experiment; not final label-supervised pipeline extraction",
            "training_plan":"Plan3","test_plan":None,"validation_note":"No generalisation performance is claimed on the training drawing.",
            "random_seed":5203,"trees":60,"features":len(names),"training_pixels":len(idx),
            "training_seconds":elapsed,"image_resize_factor":.5,
            "feature_importance":dict(sorted(zip(names,map(float,forest.feature_importances_)),key=lambda t:-t[1]))}
    (out / "Forest_Report.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    rows=["# Retained random forest - never selected","",record["validation_note"],"",
          "The raw classical mask is weak supervision. This preliminary experiment is retained separately from label matching; it cannot resolve label or geometry flags.","",
          "| Feature | Importance |","|---|---:|"]
    rows += [f"| {k} | {v:.6f} |" for k,v in record["feature_importance"].items()]
    (out / "Feature_Importance.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    print(f"Forest retained, NEVER selected: {len(idx)} training pixels, 15 features, 60 trees, {elapsed:.2f} s")
    print(record["feature_importance"])


if __name__ == "__main__":
    main()
