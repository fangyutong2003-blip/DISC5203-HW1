"""Score retained actual answers against frozen reference, with exposure limits."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/Plan3"


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def main():
    package=OUT/"reader_package_v1"
    manifest=load(package/"Flag_Manifest.json")
    ref_path=OUT/"independent_reference/Reference.json"
    if hashlib.sha256(ref_path.read_bytes()).hexdigest()!=manifest["reference_sha256"]:
        raise ValueError("Frozen reference hash mismatch")
    refs={r["flag_id"]:r for r in load(ref_path)["records"]}
    reports=[]
    for name,folder in (("GPT-6 contextual Task 1 reader","reader_A_task1"),("Grok (version pending)","reader_B_grok")):
        raw=load(OUT/folder/"Raw_Answers.json")
        assert [a["flag_id"] for a in raw]==[f["flag_id"] for f in manifest["flags"]]
        flags=[]
        for f,a in zip(manifest["flags"],raw):
            assert 0<=a["confidence"]<=1
            r=refs[f["flag_id"]]
            agrees=r["reference_resolved"] and all(a[k]==r["expected"][k] for k in f["asked_fields"])
            above=a["confidence"]>manifest["confidence_threshold"]
            substantive=all(a[k] is not None for k in f["asked_fields"])
            size_error=None
            if "size_mm" in f["asked_fields"] and a["size_mm"] is not None:
                expected=list(map(int,r["expected"]["size_mm"].split("x")))
                observed=list(map(int,a["size_mm"].split("x")))
                size_error=max(abs(x-y) for x,y in zip(expected,observed))
            flags.append({"flag_id":f["flag_id"],"resolved":above and agrees,
                          "broken":above and substantive and not agrees,
                          "confidence":a["confidence"],"max_dimension_error_mm":size_error})
        reports.append({"reader":name,"resolved":sum(f["resolved"] for f in flags),
                        "broken":sum(f["broken"] for f in flags),"total":len(flags),
                        "mean_confidence":sum(a["confidence"] for a in raw)/len(raw),"flags":flags})
    same=all(all(a[k]==b[k] for k in f["asked_fields"]) for f,a,b in zip(manifest["flags"],
                load(OUT/"reader_A_task1/Raw_Answers.json"),load(OUT/"reader_B_grok/Raw_Answers.json")))
    report={"status":"Provisional scoring of received records; Task 2 evidence not yet complete",
            "reference_sha256":manifest["reference_sha256"],"readers":reports,
            "asked_field_outputs_identical":same,"model_promoted":None,
            "verdict":"Tie on the five asked-field answers; no accuracy winner is established. Self-reported confidence is not a tiebreaker.",
            "remaining":["Exact Grok version and website/session evidence", "Isolated first-reader run for fair comparison", "Document or align the execution harness", "Structural consequences relative to reference after Task 3 mechanics exists"]}
    target=OUT/"task2_received"
    target.mkdir(parents=True,exist_ok=True)
    (target/"Comparison.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    rows=["# Task 2 - Provisional comparison of received answers","",report["status"],"",
          "| Reader | Resolved | Broken | Mean confidence | Printed-size error (mm) |",
          "|---|---:|---:|---:|---:|"]
    for r in reports:
        errors=[f["max_dimension_error_mm"] for f in r["flags"] if f["max_dimension_error_mm"] is not None]
        rows.append(f"| {r['reader']} | {r['resolved']}/{r['total']} | {r['broken']} | {r['mean_confidence']:.3f} | {max(errors) if errors else 'N/A'} |")
    rows += ["",report["verdict"],"",
             "Grok identity is user-reported; no exact version or website screenshot has been supplied. The five JSON objects are preserved as received, without correcting them. The two original execution environments differ. Reader A was an engineering session with prior draft/answer-related context, not an isolated reader. These limitations prevent presenting this table as a fully controlled experiment.","",
             "All queried fields are identical, so these five corrections alone introduce no geometry difference between the readers. No numerical CR or reference-relative structural error is claimed before the mechanics calculation. No winner or promotion has been manufactured.","",
             "## Per-flag Grok outcomes","","| Flag | Resolved | Broken | Size error (mm) |","|---|---|---|---:|"]
    for f in reports[1]["flags"]:
        rows.append(f"| {f['flag_id']} | {f['resolved']} | {f['broken']} | {f['max_dimension_error_mm'] if f['max_dimension_error_mm'] is not None else 'N/A'} |")
    rows += ["","Raw records: [Grok answers](../reader_B_grok/Raw_Answers.json), [Grok metadata](../reader_B_grok/Run_Metadata.json), [Reader A answers](../reader_A_task1/Raw_Answers.json)."]
    (target/"Comparison.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    print(json.dumps({"readers":[{k:r[k] for k in ('reader','resolved','broken','mean_confidence')} for r in reports],"verdict":report["verdict"]},indent=2))


if __name__=="__main__":main()
