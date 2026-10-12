"""Independent checks for the Task 8 plan-grid subframes and Task 12 table."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from hw2_beam_loads import SEGMENTS
from step08_grid_subframes import MODEL_DEFINITIONS, STOREY

ROOT=Path(__file__).resolve().parent


def rows(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    checks=[]
    def check(label,actual,expected,tol=1e-7):
        if isinstance(expected,str):
            passed=actual==expected
        else:
            passed=math.isclose(float(actual),float(expected),rel_tol=0,abs_tol=tol)
        checks.append(dict(check=label,expected=expected,actual=actual,tolerance=tol,status="PASS" if passed else "FAIL"))

    loads={r["beam_id"]:r for r in rows("Step_05_Beam_Line_Loads.csv")}
    reactions=rows("Step_08_Grid_Subframe_Reactions.csv")
    cross=rows("Step_12_HW1_Grid_Subframe_Cross_Check.csv")
    hw1={r["element_id"]:r for r in rows("Step_02_Element_Load_Summary.csv")}
    digest=hashlib.sha256((ROOT/"Step_05_Beam_Load_Profiles.csv").read_bytes()).hexdigest()
    for beam_name,definition in MODEL_DEFINITIONS.items():
        slug=beam_name.replace(" ","")
        result=json.loads((ROOT/f"Step_08_{slug}_Grid_Result.json").read_text())
        check(beam_name+" profile provenance",result["profile_source_sha256"],digest,"exact")
        expected_beam=sum(float(loads[b]["span_m"])*float(loads[b]["service_udl_total_load_equiv_kN_m"]) for b in definition["members"])
        check(beam_name+" included beam load",result["represented_beam_service_load_kN"],expected_beam)
        expected_self=sum(width*depth*STOREY*25 for label,x,y,width,depth,factor in definition["supports"])
        check(beam_name+" vertical member self-weight",result["vertical_member_self_weight_kN"],expected_self)
        check(beam_name+" applied load sum",result["applied_vertical_load_kN"],expected_beam+expected_self)
        check(beam_name+" vertical equilibrium",result["equilibrium_error_kN"],0,1e-5)
        check(beam_name+" positive sagging exists",result["peak_sagging_kNm"]>0,True,0)
        check(beam_name+" negative hogging exists",result["peak_hogging_kNm"]<0,True,0)
        selected=definition["selected"]
        selected_horizontal=all(SEGMENTS[b].horizontal for b in selected)
        perpendicular=any(SEGMENTS[b].horizontal!=selected_horizontal for b in definition["members"] if b not in selected)
        check(beam_name+" contains perpendicular bay members",perpendicular,True,0)
        response=rows(f"Step_08_{slug}_Selected_Response.csv")
        expected_length=sum(SEGMENTS[b].length for b in selected)
        check(beam_name+" response starts at zero",min(float(r["station_m"]) for r in response),0)
        check(beam_name+" response reaches full selected length",max(float(r["station_m"]) for r in response),expected_length)
        grouped=defaultdict(list)
        for row in response:
            local=float(row["local_station_m"])
            length=SEGMENTS[row["beam_id"]].length
            if 1e-8 < local < length-1e-8:
                grouped[(row["beam_id"],round(local,8))].append(float(row["bending_moment_kNm"]))
        worst=max(max(values)-min(values) for values in grouped.values())
        check(beam_name+" bending-moment continuity inside each span",worst,0,1e-4)
        model_reactions=[r for r in reactions if r["beam"]==beam_name]
        check(beam_name+" support count",len(model_reactions),len(definition["supports"]),0)
        check(beam_name+" positive total base reaction",sum(float(r["Rz_kN"]) for r in model_reactions),result["vertical_reaction_sum_kN"])
        for support in definition["selected_supports"]:
            item=next(r for r in cross if r["beam"]==beam_name and r["grid_point"]==support)
            hw1_expected=float(hw1[support]["total_G_per_floor_kN"])+float(hw1[support]["total_Q_per_floor_kN"])
            check(f"{beam_name} {support} HW1 source",float(item["HW1_one_floor_G_plus_Q_kN"]),hw1_expected)
            reaction=next(r for r in model_reactions if r["support"]==support)
            check(f"{beam_name} {support} reaction source",float(item["grid_subframe_base_reaction_kN"]),float(reaction["Rz_kN"]))

    with (ROOT/"Step_08_Grid_Subframe_Verification.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(checks[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(checks)
    failures=[r for r in checks if r["status"]!="PASS"]
    if failures:
        raise SystemExit(f"Step 08 verification failed: {failures}")
    print(f"Step 08 grid-subframe verification passed: {len(checks)}/{len(checks)}")


if __name__=="__main__":
    main()
