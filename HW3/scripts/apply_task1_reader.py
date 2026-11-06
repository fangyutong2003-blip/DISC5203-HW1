"""Validate Task 1 reader answers and apply only permitted fields to a copy."""
import copy
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads(path.read_text(encoding="utf-8"))


def main():
    task=ROOT/"outputs/Plan3/task1"
    run=ROOT/"outputs/Plan3/reader_A_task1"
    package=ROOT/"outputs/Plan3/reader_package_v1"
    manifest=read(package/"Flag_Manifest.json")
    reference_path=ROOT/"outputs/Plan3/independent_reference/Reference.json"
    assert hashlib.sha256(reference_path.read_bytes()).hexdigest()==manifest["reference_sha256"]
    references={r["flag_id"]:r for r in read(reference_path)["records"]}
    answers=read(run/"Raw_Answers.json")
    ids=[a["flag_id"] for a in answers]
    assert ids==[f["flag_id"] for f in manifest["flags"]]
    original=task/"Elements_Classical.json"
    before=original.read_bytes()
    geometry=read(original)
    updated=copy.deepcopy(geometry)
    logs=[]
    for flag,a in zip(manifest["flags"],answers):
        reference=references[flag["flag_id"]]
        fields=flag["asked_fields"]
        agrees=reference["reference_resolved"] and all(a[k]==reference["expected"][k] for k in fields)
        accepted=a["confidence"]>manifest["confidence_threshold"] and agrees
        e=next(e for e in updated["elements"] if e["labels"]==[flag["candidate_label"]])
        if accepted:
            if "continuous" in fields:e["continuous"]=a["continuous"]
            if "size_mm" in fields:e["size_mm"]=list(map(int,a["size_mm"].split("x")))
            e["audit"].setdefault("reader_resolution",[]).append({"flag_id":a["flag_id"],"source":"corrected by GPT-6 (Codex session)","confidence":a["confidence"],"accepted_fields":fields})
        logs.append({"flag_id":a["flag_id"],"reference_agreement":agrees,"accepted":accepted,
                     "geometry_vertices_moved":False,"asked_fields":fields})
    (task/"Elements_After_Reader_A.json").write_text(json.dumps(updated,indent=2),encoding="utf-8")
    assert original.read_bytes()==before
    for a,b in zip(geometry["elements"],updated["elements"]):assert a["centre_m"]==b["centre_m"]
    log={"status":"Task 1 single-reader candidate, not Task 2 winner",
         "original_sha256":hashlib.sha256(before).hexdigest(),"original_preserved":True,
         "accepted":sum(l["accepted"] for l in logs),"total":len(logs),"actions":logs}
    (run/"Application_Log.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
    metadata={"recorded_utc":datetime.now(timezone.utc).isoformat(),"model":"GPT-6, system-reported Codex session identity",
              "image_capability":"Native local image-viewing tool, five actual frozen crops inspected in flag order.",
              "collection_method":"Assistant-authored structured answers after native image inspection; not an external API call.",
              "context_limit":"This engineering session previously saw the draft crops and OCR/historical audit. This is a real Task 1 reading but not a blinded controlled Task 2 run. A fresh isolated first-reader session should be collected alongside DP for the formal two-model comparison.",
              "confidence_note":"Self-reported judgement; not calibrated probability.",
              "prompt_sha256":manifest["prompt_sha256"],"reference_sha256":manifest["reference_sha256"],
              "answers_sha256":hashlib.sha256((run/"Raw_Answers.json").read_bytes()).hexdigest(),
              "model_promoted":False}
    (run/"Run_Metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print("Task 1 answers accepted on copy:",log["accepted"],"/",len(logs),"; original and all centres unchanged")


if __name__=="__main__":main()
