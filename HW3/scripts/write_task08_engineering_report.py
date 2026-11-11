"""Generate the current conditional engineering report and three-plan comparison."""
import csv
import json
from pathlib import Path

import numpy as np
from shapely.geometry import shape
from task08_areas_and_hand import footprint

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def csv_write(path,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def main():
    base=load(ROOT/'outputs/Plan3/task3/Analytical_Result.json')
    prior=base['cases'][base['adopted_case']]
    comparison=[{'plan':'Plan3','mass_area_m2':base['mass']['equivalent_mass_area_m2'],
                 'mass_per_floor_t':base['mass']['one_storey_mass_t'],
                 'CM_x_m':base['mass']['CM_m'][0],'CM_y_m':base['mass']['CM_m'][1],
                 'CR_x_m':prior['CR_m'][0],'CR_y_m':prior['CR_m'][1],
                 'eccentricity_m':prior['eccentricity_m'],
                 'T1_s':base['modes'][0]['period_s'],'T2_s':base['modes'][1]['period_s'],'T3_s':base['modes'][2]['period_s'],
                 'status':'Retained provisional common-geometry baseline; original reader exposure limits remain'}]
    all_data={}
    for plan in ('NewPlan','NIST'):
        out=ROOT/'outputs'/plan/'engineering_r1_refined'
        h=load(out/'Hand_Analysis.json');r=load(out/'OpenSees_Result.json');g=load(ROOT/h['geometry_record'])
        gravity=load(out/'Known_Gravity_Totals.json');uncertainty=load(out/'Source_Uncertainty_Cases.json')
        gate=load(out/'Conditional_Engineering_Gate.json')
        all_data[plan]=(h,r,g,gravity,uncertainty,gate)
        comparison.append({'plan':plan,'mass_area_m2':h['mass']['area_m2'],'mass_per_floor_t':h['mass']['mass_t'],
                           'CM_x_m':h['mass']['CM_m'][0],'CM_y_m':h['mass']['CM_m'][1],
                           'CR_x_m':r['solver_CR_m'][0],'CR_y_m':r['solver_CR_m'][1],
                           'eccentricity_m':r['solver_eccentricity_m'],
                           **{f'T{i+1}_s':m['period_s']for i,m in enumerate(r['modal']['opensees_modes'])},
                           'status':'Supplementary conditional engineering model; original frozen pipeline not promoted'})
        coords=[]
        for e in g['elements']:
            size=e['size_mm']
            if e['class']=='wall':
                w,th=e['length_m']*1000,e['thickness_m']*1000
                a,b=(w,th)if e['angle_deg']==0 else(th,w)
            else:
                a,b=size if size is not None else(None,None)
            coords.append({'element_id':e['labels'][0],'type':e['class'],'x_m':e['centre_m'][0],'y_m':e['centre_m'][1],
                           'size_x_mm':a,'size_y_mm':b,'angle_deg':e.get('angle_deg'),
                           'label_only_grid_inference':e['audit'].get('label_only_grid_inference',False),
                           'size_provenance':e['provenance']['size']})
        csv_write(out/'Coordinates_and_Size_Provenance.csv',coords)
    target=ROOT/'outputs/Task08';target.mkdir(exist_ok=True)
    csv_write(target/'Three_Plan_Comparison.csv',comparison)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    for plan,(h,r,g,gravity,uncertainty,gate)in all_data.items():
        out=ROOT/'outputs'/plan/'engineering_r1_refined'
        regions=load(out/'Closed_Tributary_Regions.geojson')['features']
        lookup={f['properties']['id']:shape(f['geometry'])for f in regions}
        fig,ax=plt.subplots(figsize=(13,6)if plan=='NewPlan'else(9,9))
        assumed_handle=point_handle=False
        for i,e in enumerate(g['elements']):
            label=e['labels'][0];poly=lookup[label]
            for piece in ([poly]if poly.geom_type=='Polygon'else poly.geoms):
                ax.fill(*piece.exterior.xy,color=plt.get_cmap('tab20')(i%20),alpha=.18)
                ax.plot(*piece.exterior.xy,'--',color='gray',lw=.55)
            point=poly.representative_point();tx,ty=point.x,point.y
            if np.linalg.norm(np.array([tx,ty])-h['mass']['CM_m'])<1:ty+=.8
            assumed=e['audit'].get('label_only_grid_inference',False)
            ax.text(tx,ty,label,fontsize=7,ha='center',color='#c64b00'if assumed else'black')
            fp=footprint(e)
            if assumed:
                a,b,c,d=fp.bounds
                ax.add_patch(Rectangle((a,b),c-a,d-b,facecolor='none',edgecolor='#e6550d',hatch='///',lw=1.2,
                    label='Label-only column assumption'if not assumed_handle else None));assumed_handle=True
            elif fp is not None:
                ax.fill(*fp.exterior.xy,color='black',alpha=.65)
            else:
                ax.plot(*e['centre_m'],'ko',ms=3,label='Column point; size unknown'if not point_handle else None);point_handle=True
        floor=shape(g['floor']['polygon']);ax.plot(*floor.exterior.xy,color='black',lw=1)
        ax.plot(*h['mass']['CM_m'],'r+',ms=12,label='CM')
        ax.plot(*r['solver_CR_m'],'bx',ms=8,label='CR')
        ax.set(aspect='equal',xlabel='x (m)',ylabel='y (m)',title=plan+' | Closed conditional regions; source assumptions visible')
        ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),fontsize=8)
        if plan=='NIST':ax.text(.02,.02,'CM and CR coincide at plot scale',transform=ax.transAxes,fontsize=8)
        fig.tight_layout();fig.savefig(out/'Reviewed_Closed_Regions_and_Centres.png',dpi=160,bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,5))
    names=[r['plan']for r in comparison];x=np.arange(3)
    axes[0].bar(names,[r['mass_per_floor_t']for r in comparison],color=['#8c8c8c','#2171b5','#238b45'])
    axes[0].set(ylabel='Prescribed mass per floor (t)',title='Uniform-mass exercise convention')
    axes[1].bar(names,[r['eccentricity_m']for r in comparison],color=['#8c8c8c','#2171b5','#238b45'])
    for i,r in enumerate(comparison):axes[1].text(i,r['eccentricity_m']+.025,f"{r['eccentricity_m']:.4f}",ha='center')
    axes[1].set(ylabel='e (m)',title='NIST millimetres are not source precision');axes[1].set_ylim(0,1.8)
    for i in range(3):axes[2].bar(x+(i-1)*.23,[r[f'T{i+1}_s']for r in comparison],width=.23,label=f'Mode {i+1}')
    axes[2].set(xticks=x,xticklabels=names,ylabel='Period (s)',title='Single-floor 3-DOF model, not building periods');axes[2].legend()
    fig.suptitle('Three-plan comparison | retained baseline and supplementary conditional models')
    fig.text(.5,.02,'Source ambiguities, missing gravity sections and post-response reference revisions remain disclosed.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,.93));fig.savefig(target/'Three_Plan_Comparison.png',dpi=160);plt.close(fig)
    engineering=load(ROOT/'records/Task_08_Engineering_Validation.json')
    solver=load(ROOT/'records/Task_08_OpenSees_Validation.json')
    text=['# Task 8 - Conditional geometry, closed areas and matched OpenSees comparison','',
          'Student: Fangyutong, 21353319. Date: 2026-11-11.','',
          '**Status:** the two additional plans now have complete conditional support schedules, closed tributary polygons, known gravity schedules, hand CM/K/CR and actual matched OpenSees runs. These are explicitly assumption-dependent engineering baselines. The original unchanged image pipeline failed and is not retroactively promoted. Source ambiguities and cross-harness/reference timing limits remain. This is not a claim that all HW3 rubric requirements are satisfied.','',
          '## Workflow and provenance','',
          'The prospective [geometry brief](records/Task_08_Geometry_Recovery_Brief_R1.md) and [parameter file](params_geometry_recovery_r1.json) were committed as `445eef6`. The new deterministic solid-symbol route is separate from the frozen hatching pipeline. It preserves all components, labelled bar assignments, measured grids, global-fit residuals, piecewise calibration and source overlays. A rejected label-centre guard is retained in [the attempt record](records/Task_08_Geometry_Assignment_Attempt.md); the masks and eight actual nearest-bar claims were unchanged.','',
          'Commit `0d7c45b` retained geometry before area calculations. Commit `f368008` retained the initial closed-region and hand results before numerical refinement. Commit `d66f7a1` froze refined regions, independent hand checks and conditional gates **before** the OpenSees runs. Original V4 inputs, failed classical masks, forests and earlier R2/R3 reader scores remain preserved.','',
          'The [two-reader R3 comparison](outputs/Task08/reader_comparison_r3/Comparison.md) is a tie on ten supplemented questions. Codex gpt-6.1-sol is runtime-evidenced; Grok 4.5 is student-reported. R2 source measurements and the human T3 review were post-response revisions, not blind pre-response truth. No accuracy winner or fully promoted unchanged-pipeline extraction is invented.','',
          '## Coordinate and source interpretations','',
          '- **NewPlan:** origin A4 column-grid centre; x right and y up. Dimensioned axes x=0/6/12/20/26/34/40/46 m, y=0/6/12/18 m. Printed sizes: C1:C30=800x800 mm; T1/T2/T3/T5/T6/T7=3500x400 mm; T4/T8=2000x300 mm. The main assumed outer-column-face slab bounds are [-0.4,46.4] x [-0.4,18.4] m. The grid-axis 828 m2 rectangle is a separate sensitivity.','- **NewPlan source ambiguity:** 26 standalone square bodies and two merged column/wall junctions are visible. C17/C20 are printed labels without clear filled square bodies, retained as grid-inferred supports; their omission sensitivity is exported. This is not a successful detection of two missing symbols. T4/T8 nominal rectangles protrude 13.636 mm beyond the assumed lower slab edge (0.054545 m2 combined); support axes are inside, and the small face discrepancy is not clipped away.','- **NIST:** origin lower-left footprint corner. The printed 120 ft square is 36.576 x 36.576 m, with 30 ft (9.144 m) bays. The visible model has 21 column points and four walls; adjacent source text describes 25 gravity columns. The four-column discrepancy and unknown column sections remain unresolved. NC/NW identifiers are analyst bookkeeping, not printed labels.','- **NIST wall geometry:** lengths are measured from schematic bars. Thickness 250 mm is the course default, not a pixel-derived or printed section. Perimeter outside faces are assumed on the footprint border; centre axes are inset by half that thickness. Raw ink centres and uncertainty are retained. Unknown columns have no invented footprint or self-weight.','- Neither extra drawing shows an opening/stair zone; their absence is a modelling assumption. Plan 3 O1/O2/S1 are not copied to the new plans.','',
          'NIST source: Elsibaie et al. (2025), [NIST TN 2351, Figure 2](https://doi.org/10.6028/NIST.TN.2351), printed page 9. Republished courtesy of the National Institute of Standards and Technology. This is a research archetype, not an identified surveyed building.','']
    for plan,(h,r,g,gravity,uncertainty,gate)in all_data.items():
        path=f'outputs/{plan}/engineering_r1_refined'
        text += ['### '+plan+' geometry and closed-area record','',
                 f"![{plan} original-source overlay](outputs/{plan}/geometry_recovery_r1/Geometry_Source_Overlay.png)",'',
                 f"![{plan} closed conditional tributary regions]({path}/Reviewed_Closed_Regions_and_Centres.png)",'',
                 f"[Coordinates and section provenance]({path}/Coordinates_and_Size_Provenance.csv), [calibration](outputs/{plan}/geometry_recovery_r1/Calibration.json), [geometry](outputs/{plan}/geometry_recovery_r1/Elements_Conditional.json), [closed GeoJSON]({path}/Closed_Tributary_Regions.geojson), [area/load schedule]({path}/Tributary_and_Known_Loads.csv).",'',
                 f"The declared floor area is {h['mass']['area_m2']:.6f} m2. All {len(g['elements'])} support IDs appear in the geometry, area and known-load records. L1 nearest finite-axis/point regions are closed, valid and non-overlapping. Known column footprints are removed from gravity wall-axis segments at joints; full labelled wall axes remain in the lateral model. Both conventions and the untrimmed-axis sensitivity are retained.",'',
                 f"The adopted 0.025 m area grid was checked against 0.05 m; maximum relative per-support change is {100*gate['max_relative_area_grid_change']:.3f}%. " + ('This is below the approximate 1% target.' if gate['max_relative_area_grid_change']<=.01 else 'This is marginally above the approximate 1% target and is explicitly retained as an exception, not reported as a strict 1% pass.'),
                 'The domain closes to numerical tolerance even though individual allocations are discretised. Source topology/size uncertainty is separate from mesh convergence.','']
    text += ['## Gravity and floor-mass convention','',
             'The transferred HW1 exercise assumptions are G_slab=0.150*25=3.75 kN/m2, Q=5.0 kN/m2, H=3 m and five-storey gravity accumulation. These are assumptions for the comparison, not loads printed on either new drawing. No unspecified beams, finishes, foundations or earthquake demand are added. ULS factors remain unconfirmed in the retained project configuration; no new complete axial design certification is made.','',
             'Known vertical self-weight uses the union of section footprints, allocated to columns before remaining labelled walls to avoid overlap double counting. This is joint bookkeeping, not an indeterminate-junction force solution. NIST column self-weights remain null; all its gravity totals below are **known-only**, not complete totals.','',
             '| Plan | Slab area (m2) | Known net vertical section (m2) | Known vertical weight / storey (kN) | G known / floor (kN) | Q / floor (kN) |','|---|---:|---:|---:|---:|---:|']
    for plan,(h,r,g,v,u,gate)in all_data.items():
        text.append(f"| {plan} | {h['mass']['area_m2']:.3f} | {v['known_net_vertical_footprint_m2']:.6f} | {v['known_vertical_self_weight_kN']:.3f} | {v['G_known_per_floor_kN']:.3f} | {v['Q_per_floor_kN']:.3f} |")
    text += ['',
             'The exported [NewPlan accumulation](outputs/NewPlan/engineering_r1_refined/Known_Axial_Accumulation.csv) and [NIST known-only accumulation](outputs/NIST/engineering_r1_refined/Known_Axial_Accumulation.csv) follow 1:2:3:4:5. The prescribed lateral floor mass is separately (8.75/g)*floor area, in tonnes. Vertical-element weights are **not** silently added to this mass, matching the retained Plan 3 exercise convention.','',
             '## Hand calculation before the matching solver','',
             'E=30e6 kN/m2, nu=0.2, G=12.5e6 kN/m2, H=3 m, Av=(5/6)Lt. For each labelled rectangular wall: I_s=tL^3/12, I_w=Lt^3/12; k_b=3EI/H^3 and k_s=1/[H^3/(3EI)+H/(GAv)]. Both in-plane rectangular bending axes are retained; columns supply no lateral stiffness and intrinsic vertical-wall J is zero. Joined L bars are not treated as a detailed monolithic shell or full-building frame.','',
             'For wall offsets dx,dy from CM, K is assembled from kx*[1,0,-dy]^T*[1,0,-dy] and ky*[0,1,dx]^T*[0,1,dx]. Kxphi=-sum(kx*dy), Kyphi=sum(ky*dx), Kphiphi=sum(kx*dy^2+ky*dx^2). Thus xr=xm+Kyphi/Kyy and yr=ym-Kxphi/Kxx. With F=inv(K), xr=xm-Fphiy/Fphiphi, yr=ym+Fphix/Fphiphi. These flexibility ratios have units m; stiffness ratios with a rotational denominator cannot be added as coordinates.','',
             'Translation block units are kN/m, translation-rotation entries kN, rotational entry kN m; angles are radians. Mass and polar mass are t and t m2.','']
    for plan,(h,r,g,v,u,gate)in all_data.items():
        text += ['### '+plan+' K about CM','', '```text',np.array2string(np.array(h['matched_rectangular_shear']['K_about_CM']),precision=6,suppress_small=True),'```','',
                 f"[Hand matrices, wall stiffnesses, mass integrals and cases](outputs/{plan}/engineering_r1_refined/Hand_Analysis.json). CM=({h['mass']['CM_m'][0]:.6f},{h['mass']['CM_m'][1]:.6f}) m; CR=({r['solver_CR_m'][0]:.6f},{r['solver_CR_m'][1]:.6f}) m; e={r['solver_eccentricity_m']:.6f} m.",'']
    text += ['## Actual OpenSees verification','',
             'OpenSees 3.8.0 was actually run using one ElasticTimoshenkoBeam cantilever per wall, explicit rigidDiaphragm(3,1,*wall_top_nodes) and Transformation constraints. Bases are fixed; tops have [0,0,1,0,0,0] fixity. Three unit loads recover F and K. Assumed 100 kN x/y demonstration forces, loads through CR, separate push/turn cases, bending-only limits and isolated section limits were run and saved. The generic fullGenLapack speed warning occurred; all requested static/eigen cases returned valid results.','',
             'The actual modal calculation has one floor master with prescribed mass and polar inertia. Its periods are **single-floor 3-DOF diagnostics**, not the periods of a full five-storey building or the original multi-storey NIST archetype. Five-storey gravity accumulation is a separate bookkeeping calculation.','',
             f"Independent geometry/area/load/hand checks pass {engineering['passed']}/{engineering['total']}; actual solver checks pass {solver['passed']}/{solver['total']}. The largest relative hand/model flexibility error is {max(s['max_relative_F_error']for s in solver['summaries']):.3g}; the largest CR-coordinate difference is {max(s['max_CR_coordinate_error_m']for s in solver['summaries']):.3g} m. Those numerical agreements validate the matched assumptions, not the source drawing interpretation.",'',
             '[Engineering validation](records/Task_08_Engineering_Validation.json), [solver validation](records/Task_08_OpenSees_Validation.json). Raw unit loads, reactions, master/slave displacements and eigenvalues are in [NewPlan results](outputs/NewPlan/engineering_r1_refined/OpenSees_Result.json) and [NIST results](outputs/NIST/engineering_r1_refined/OpenSees_Result.json). Direct/torsional wall shares are exported in each folder as Wall_Force_Push_and_Turn.csv.','',
             '## Three-plan comparison','',
             'All rows use the same 3 m, uncracked-material, strong/weak/shear rectangular-wall convention and prescribed 8.75 kN/m2 uniform mass. Origins differ: compare eccentricity and layout rather than raw coordinate magnitudes. Plan 3 mass area includes the separately treated stair-equivalent mass; its ordinary slab tributary area is 179.25 m2.','',
             '| Plan | Effective mass area (m2) | Mass / floor (t) | CM x,y (m) | CR x,y (m) | e (m) | T1 / T2 / T3 (s) |','|---|---:|---:|---|---|---:|---|']
    for row in comparison:
        text.append(f"| {row['plan']} | {row['mass_area_m2']:.3f} | {row['mass_per_floor_t']:.3f} | {row['CM_x_m']:.4f}, {row['CM_y_m']:.4f} | {row['CR_x_m']:.4f}, {row['CR_y_m']:.4f} | {row['eccentricity_m']:.4f} | {row['T1_s']:.5f} / {row['T2_s']:.5f} / {row['T3_s']:.5f} |")
    text += ['', '![Three-plan conditional comparison](outputs/Task08/Three_Plan_Comparison.png)','',
             'NewPlan is nearly symmetric left/right but has unequal upper/lower horizontal wall lengths; its CR lies above CM. Plan 3 retains larger eccentricity from its irregular mass/wall arrangement. The nominal NIST layout is nearly symmetric: the measured millimetre-scale e must not be treated as established physical precision. Modal ordering also differs: the torsion-dominant conditional mode is mode 2 for NewPlan and mode 3 for NIST, rather than a universal mode number.','',
             '## Sensitivities and limits that change interpretation','']
    h,r,g,v,u,gate=all_data['NewPlan']
    omitted=h['sensitivities']['omit_C17_C20'];alternate=h['sensitivities']['grid_axis_floor_mass']
    text += [f"- NewPlan grid-axis slab area 828 m2 gives {alternate['mass']['mass_t']:.3f} t/floor instead of {h['mass']['mass_t']:.3f} t. CM and CR do not change under this symmetric edge change, but the actual coupled periods change to "+', '.join(f"{m['period_s']:.5f}"for m in alternate['modes'])+' s.',
             f"- Omitting C17/C20 reallocates {sum(omitted['omitted_baseline_areas_m2'].values()):.3f} m2. The largest other-support area increase is {omitted['max_other_support_area_increase_m2']:.3f} m2, or {omitted['max_other_support_area_increase_m2']*8.75:.3f} kN service slab load/floor ({omitted['max_other_support_area_increase_m2']*8.75*5:.3f} kN over five floors). CM/CR stay unchanged **only because** mass is prescribed independently and columns are excluded from lateral stiffness. This is not a claim that missed columns are harmless.",
             f"- Global-affine instead of piecewise calibration moves NewPlan CR by {u['global_affine_instead_of_piecewise']['CR_shift_m']:.4f} m. Both routes and residuals are retained; image scaling is not CAD certainty."]
    h,r,g,v,u,gate=all_data['NIST']
    text += [f"- The ideal symmetric NIST sensitivity gives e={h['sensitivities']['symmetric_idealisation']['eccentricity_m']:.3g} m. The measured e={r['solver_eccentricity_m']:.6f} m is below the source endpoint precision.",
             f"- A deterministic extreme-box sensitivity moves each schematic endpoint by +/-2 pixels, allowing each wall length +/-4 pixels with fixed centres/thickness/mass. Among the 16 independent sign combinations, maximum e is {u['independent_endpoint_extreme_cases']['maximum_eccentricity_m']:.3f} m. This is **not** a probability or confidence interval; it demonstrates why a tiny baseline e cannot be certified without real wall dimensions. It also does not assert that the source building is asymmetric.",
             '- NIST unknown column sections and the 21-symbol/25-column discrepancy prevent complete gravity certification. Wall lengths/thickness and floor-edge conventions are explicit assumptions/measurements, not a drawing-issued design schedule.',
             '- Rectangular-bar, no-column-lateral, uncracked, single-floor models omit monolithic L-wall coupling, cracking, full-height interaction and real earthquake demands. Matching hand and solver does not remove these limits.','',
             '[NewPlan source sensitivities](outputs/NewPlan/engineering_r1_refined/Source_Uncertainty_Cases.json), [NIST endpoint cases](outputs/NIST/engineering_r1_refined/Source_Uncertainty_Cases.json), [column-omission gravity sensitivity](outputs/NewPlan/engineering_r1_refined/Label_Only_Column_Sensitivity.csv).','',
             '## Reproduce and review','',
             'All source/reader evidence is retained. Numerical workflow, from repository root with HW3 requirements installed:','',
             '```powershell','python HW3/scripts/task08_geometry_recovery.py','python HW3/scripts/task08_areas_and_hand.py',
             'python HW3/scripts/task08_areas_and_hand.py --refined','python HW3/scripts/verify_task08_engineering.py',
             'python HW3/scripts/task08_opensees.py','python HW3/scripts/verify_task08_opensees.py',
             'python HW3/scripts/task08_source_sensitivity.py','python HW3/scripts/write_task08_engineering_report.py','```','',
             'Review geometry/source assumptions first, then exported closed regions and gravity, then the hand matrices, then actual solver checks. The original fixed-rule generalisation failure and experimental limitations remain part of the submission; do not describe the conditional recovery as a fully successful unchanged, blind, end-to-end promoted extraction.','']
    (ROOT/'HW3_Task_08_Conditional_Engineering_Report.md').write_text('\n'.join(text),encoding='utf-8',newline='\n')
    print('Generated coordinate CSVs, three-plan table/figure and English conditional engineering report')


if __name__=='__main__':
    main()
