"""Score retained actual answers against frozen reference, with exposure limits."""
import hashlib
import copy
import math
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/Plan3"


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def conditioned_structure(manifest,refs):
    params=load(ROOT/"params_mechanics.json")
    base=load(OUT/"task1/Elements_Classical.json")
    def corrected(answers):
        geometry=copy.deepcopy(base)
        for f,a in zip(manifest["flags"],answers):
            e=next(e for e in geometry["elements"] if e["labels"]==[f["candidate_label"]])
            if not all(a[k]==refs[f["flag_id"]]["expected"][k] for k in f["asked_fields"]):continue
            if "size_mm" in f["asked_fields"]:e["size_mm"]=list(map(int,a["size_mm"].split("x")))
            if "continuous" in f["asked_fields"]:e["continuous"]=a["continuous"]
        return geometry
    expected=[refs[f["flag_id"]]["expected"] for f in manifest["flags"]]
    geometries={"flag_conditioned_reference":corrected(expected),
                "GPT-6 contextual":corrected(load(OUT/"reader_A_task1/Raw_Answers.json")),
                "Grok 4.5 student-reported":corrected(load(OUT/"reader_B_grok/Raw_Answers.json"))}
    def cr(geometry):
        kx_sum=ky_sum=kx_y=ky_x=0.
        for e in geometry["elements"]:
            if e["class"]!="wall":continue
            L=max(e["size_mm"])/1000;t=min(e["size_mm"])/1000;E=params["E_kN_m2"];H=params["height_m"]
            G=E/(2*(1+params["nu"]));Av=params["shear_factor"]*L*t
            strong=1/(H**3/(3*E*(t*L**3/12))+H/(G*Av))
            weak=1/(H**3/(3*E*(L*t**3/12))+H/(G*Av))
            kx,ky=(strong,weak) if e["angle_deg"]==0 else (weak,strong)
            kx_sum+=kx;ky_sum+=ky;kx_y+=kx*e["centre_m"][1];ky_x+=ky*e["centre_m"][0]
        return [ky_x/ky_sum,kx_y/kx_sum]
    ref=cr(geometries["flag_conditioned_reference"])
    result=[]
    for name,g in geometries.items():
        centre=cr(g)
        signature=[{k:e.get(k) for k in ("labels","class","centre_m","size_mm","angle_deg","continuous")} for e in g["elements"]]
        result.append({"record":name,"CR_m":centre,"shift_from_flag_conditioned_reference_m":math.dist(centre,ref),
                       "mechanical_geometry_sha256":hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()})
    return {"scope":"Conditional on the shared unqueried classical geometry and accepted answers; not error relative to an independently surveyed full plan.","rows":result}


def main():
    package=OUT/"reader_package_v1"
    manifest=load(package/"Flag_Manifest.json")
    ref_path=OUT/"independent_reference/Reference.json"
    if hashlib.sha256(ref_path.read_bytes()).hexdigest()!=manifest["reference_sha256"]:
        raise ValueError("Frozen reference hash mismatch")
    refs={r["flag_id"]:r for r in load(ref_path)["records"]}
    reports=[]
    for name,folder in (("GPT-6 contextual Task 1 reader","reader_A_task1"),("Grok 4.5 (student-confirmed)","reader_B_grok")):
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
            "remaining":["Full-session evidence and exact backend version beyond chatbot self-description", "Isolated first-reader run for fair comparison", "Document or align the execution harness"]}
    if (OUT/"task3/Analytical_Result.json").exists():
        report["conditional_structural_consequences"]=conditioned_structure(manifest,refs)
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
             "The student confirmed Grok 4.5 and supplied a screenshot on 2026-11-10. The screenshot corroborates P3-F05 and the chatbot's self-description; the UI selector shows Fast rather than an exact backend version. The full five-question website transcript remains unavailable. The five pasted JSON objects are preserved as received, without correcting them. The two original execution environments differ. Reader A had prior draft/answer-related engineering context. These limitations prevent presenting the table as a fully controlled experiment. See [screenshot evidence description](../../../records/Grok_Screenshot_Evidence.md).","",
             "All queried fields are identical, so these five corrections alone introduce no geometry difference between the readers. No winner or promotion has been manufactured.","",
             "## Per-flag Grok outcomes","","| Flag | Resolved | Broken | Size error (mm) |","|---|---|---|---:|"]
    for f in reports[1]["flags"]:
        rows.append(f"| {f['flag_id']} | {f['resolved']} | {f['broken']} | {f['max_dimension_error_mm'] if f['max_dimension_error_mm'] is not None else 'N/A'} |")
    rows += ["","Raw records: [Grok answers](../reader_B_grok/Raw_Answers.json), [Grok metadata](../reader_B_grok/Run_Metadata.json), [Reader A answers](../reader_A_task1/Raw_Answers.json)."]
    if "conditional_structural_consequences" in report:
        cs=report["conditional_structural_consequences"]
        rows += ["","## Conditional structural consequences","",cs["scope"],"",
                 "Each record applies the accepted queried fields to a copy of the same classical geometry. Weighted wall-stiffness CR is computed separately for each copy using the Task 3 rectangular, shear-inclusive wall convention. Thus this calculation measures the consequence of the flagged fields, not full-plan extraction truth.","",
                 "| Record | CR x (m) | CR y (m) | Shift from conditional reference (m) |","|---|---:|---:|---:|"]
        rows += [f"| {v['record']} | {v['CR_m'][0]:.6f} | {v['CR_m'][1]:.6f} | {v['shift_from_flag_conditioned_reference_m']:.6f} |" for v in cs["rows"]]
    (target/"Comparison.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    print(json.dumps({"readers":[{k:r[k] for k in ('reader','resolved','broken','mean_confidence')} for r in reports],"verdict":report["verdict"]},indent=2))


if __name__=="__main__":main()
