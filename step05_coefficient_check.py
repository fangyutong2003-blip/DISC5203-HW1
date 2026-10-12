"""Reconcile area-route and HKConcrete Table 6.7 line loads.

Only clean four-edge rectangular two-way panels are checked. Irregular, split,
one-way, cantilever and core panels remain outside the coefficient-table scope.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
N_SERVICE=8.75  # slab G+Q only, kN/m2
ALPHAS=[1.0,1.1,1.2,1.3,1.4,1.5,1.75,2.0]
ONE_SHORT_VX_C=[.36,.39,.42,.44,.45,.47,.50,.52]
ONE_LONG_VX_C=[.36,.40,.44,.47,.49,.51,.55,.59]
ONE_LONG_VX_S=[.24,.27,.29,.31,.32,.34,.36,.38]

PANELS={
    "P2": dict(lx=3.10,ly=3.60,case="one short edge discontinuous",edges=[
        ("top C","vx C",3.60,["D04","W_T3"]),("bottom C","vx C",3.60,["D08"]),
        ("left S","vy S",3.10,["D05"]),("right C","vy C",3.10,["D06"])]),
    "P3": dict(lx=3.60,ly=6.05,case="one long edge discontinuous",edges=[
        ("left S","vx S",6.05,["D11"]),("right C","vx C",6.05,["D12"]),
        ("bottom C","vy C",3.60,["D16"]),("top C","vy C",3.60,["D08"])]),
    "P7": dict(lx=3.60,ly=6.05,case="one long edge discontinuous",edges=[
        ("left S","vx S",6.05,["D19"]),("right C","vx C",6.05,["D20"]),
        ("bottom C","vy C",3.60,["D23"]),("top C","vy C",3.60,["D16"])]),
    "P9": dict(lx=3.60,ly=6.05,case="one long edge discontinuous",edges=[
        ("right S","vx S",6.05,["D22"]),("left C","vx C",6.05,["D21"]),
        ("bottom C","vy C",3.60,["D25"]),("top C","vy C",3.60,["D18"])]),
}


def interpolate(values,alpha):
    for a,b,va,vb in zip(ALPHAS,ALPHAS[1:],values,values[1:]):
        if a<=alpha<=b:
            return va+(vb-va)*(alpha-a)/(b-a)
    raise ValueError(alpha)


def beta(case,edge,alpha):
    if case=="one short edge discontinuous":
        if edge=="vx C": return interpolate(ONE_SHORT_VX_C,alpha)
        if edge=="vy C": return .36
        if edge=="vy S": return .24
    if case=="one long edge discontinuous":
        if edge=="vx C": return interpolate(ONE_LONG_VX_C,alpha)
        if edge=="vx S": return interpolate(ONE_LONG_VX_S,alpha)
        if edge=="vy C": return .36
    raise ValueError((case,edge))


def main():
    with (ROOT/"Step_04_Beam_Tributary_Area_Contributions.csv").open(encoding="utf-8-sig") as stream:
        contributions=list(csv.DictReader(stream))
    area={(r["panel_id"],r["support_id"]):float(r["tributary_area_m2"]) for r in contributions}
    rows=[]; summaries=[]
    for panel_id,panel in PANELS.items():
        alpha=panel["ly"]/panel["lx"]
        coefficient_force=0;area_force=0
        for edge,coefficient_key,length,supports in panel["edges"]:
            tributary=sum(area[(panel_id,s)] for s in supports)
            b=beta(panel["case"],coefficient_key,alpha)
            coefficient_q=.75*b*N_SERVICE*panel["lx"]
            area_q=N_SERVICE*tributary/length
            coefficient_force+=coefficient_q*length
            area_force+=area_q*length
            rows.append(dict(panel_id=panel_id,panel_case=panel["case"],alpha=alpha,
                edge=edge,supports=";".join(supports),edge_length_m=length,beta_v=b,
                coefficient_route_slab_service_kN_m=coefficient_q,
                area_route_slab_service_kN_m=area_q,
                difference_percent=100*(coefficient_q-area_q)/area_q,
                note="Table route is an independent approximate check; beam stem self-weight excluded."))
        panel_load=N_SERVICE*panel["lx"]*panel["ly"]
        summaries.append(dict(panel_id=panel_id,alpha=alpha,panel_slab_service_load_kN=panel_load,
            coefficient_route_edge_force_sum_kN=coefficient_force,
            area_route_edge_force_sum_kN=area_force,
            coefficient_closure_percent=100*coefficient_force/panel_load,
            area_closure_percent=100*area_force/panel_load))
    write("Step_05_Coefficient_Area_Reconciliation.csv",rows)
    write("Step_05_Coefficient_Area_Panel_Closure.csv",summaries)
    report(rows,summaries)
    print(f"Coefficient-area reconciliation written for {len(PANELS)} rectangular panels")


def write(name,rows):
    with (ROOT/name).open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)


def report(rows,summaries):
    text=["# Step 05 - Coefficient-Route versus Area-Route Check", "",
      "This independent check applies HKConcrete 2013 Table 6.7 only to clean rectangular, four-edge, two-way panels P2, P3, P7 and P9. The coefficient-route equivalent slab line load is q = 0.75 beta_v n l_x, where n=8.75 kN/m2, l_x is the short span and alpha=l_y/l_x. Beam-stem self-weight is excluded from both routes.", "",
      "The table values are linearly interpolated in alpha. beta_vx applies to edges of length l_y; beta_vy applies to edges of length l_x. The official source is the Hong Kong Buildings Department Code of Practice for Structural Use of Concrete 2013 (2020 Edition), Table 6.7: https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/CoP_SUC2013e.pdf", "",
      "| Panel | Edge | Supports | beta_v | Coefficient q (kN/m) | Area q (kN/m) | Difference |", "|---|---|---|---:|---:|---:|---:|"]
    text += [f"| {r['panel_id']} | {r['edge']} | {r['supports']} | {r['beta_v']:.4f} | {r['coefficient_route_slab_service_kN_m']:.4f} | {r['area_route_slab_service_kN_m']:.4f} | {r['difference_percent']:+.1f}% |" for r in rows]
    text += ["", "## Panel force closure", "", "| Panel | alpha | Panel load (kN) | Coefficient edge sum (kN) | Area edge sum (kN) | Coefficient closure | Area closure |", "|---|---:|---:|---:|---:|---:|---:|"]
    text += [f"| {r['panel_id']} | {r['alpha']:.4f} | {r['panel_slab_service_load_kN']:.4f} | {r['coefficient_route_edge_force_sum_kN']:.4f} | {r['area_route_edge_force_sum_kN']:.4f} | {r['coefficient_closure_percent']:.1f}% | {r['area_closure_percent']:.1f}% |" for r in summaries]
    text += ["", "The area route closes exactly by construction. Rounded code coefficients are approximate and are used here as a scale check, not to overwrite the closed polygons. Irregular P1/P5, one-way P4/P6/P8, openings, split core supports and cantilevers are outside this table check; applying Table 6.7 to them would imply unsupported assumptions."]
    (ROOT/"Step_05_Coefficient_Area_Reconciliation.md").write_text("\n".join(text)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
