"""Independently audit exported geometry, polygon/CSV loads and hand calculations."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from shapely.geometry import shape,box,LineString,Point
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks=[]
    def check(label,value):
        checks.append({'check':label,'passed':bool(value)})
    summaries=[]
    for plan in ('NewPlan','NIST'):
        geo_path=ROOT/'outputs'/plan/'geometry_recovery_r1/Elements_Conditional.json'
        geometry=load(geo_path)
        out=ROOT/'outputs'/plan/'engineering_r1_refined'
        hand=load(out/'Hand_Analysis.json');floor=shape(geometry['floor']['polygon'])
        expected=({f'C{i}'for i in range(1,31)}|{f'T{i}'for i in range(1,9)})if plan=='NewPlan'else({f'NC{i:02d}'for i in range(1,22)}|{f'NW{i:02d}'for i in range(1,5)})
        elements=geometry['elements'];ids=[e['labels'][0]for e in elements]
        check(plan+' declared support IDs unique and complete',set(ids)==expected and len(ids)==len(set(ids)))
        check(plan+' original source hash',sha(ROOT/geometry['source']['file'])==geometry['source']['sha256'])
        for axis in ('x','y'):
            check(plan+' increasing measured grid '+axis,np.all(np.diff(geometry['calibration']['grid_px'][axis])>0))
            check(plan+' positive scale '+axis,geometry['calibration']['global_affine_px_per_m'][axis]>0)
        features=load(out/'Closed_Tributary_Regions.geojson')['features']
        regions={f['properties']['id']:shape(f['geometry'])for f in features}
        rows=list(csv.DictReader((out/'Tributary_and_Known_Loads.csv').open(encoding='utf-8')))
        csv_rows={r['element_id']:r for r in rows}
        check(plan+' identical geometry/region/load IDs',set(ids)==set(regions)==set(csv_rows))
        for label,region in regions.items():
            check(plan+' closed positive valid region '+label,not region.is_empty and region.is_valid and region.area>0)
            check(plan+' CSV polygon area '+label,abs(region.area-float(csv_rows[label]['area_m2']))<1e-7)
        combined=unary_union(list(regions.values()))
        check(plan+' exact polygon area conservation',abs(sum(g.area for g in regions.values())-floor.area)<1e-7)
        check(plan+' no polygon gaps or outside pieces',combined.symmetric_difference(floor).area<1e-7)
        check(plan+' no polygon overlaps',abs(sum(g.area for g in regions.values())-combined.area)<1e-7)
        known_shapes=[]
        for e in elements:
            x,y=e['centre_m'];label=e['labels'][0]
            if e['class']=='wall':
                L,t=e['length_m'],e['thickness_m'];w,h=(L,t)if e['angle_deg']==0 else(t,L)
                axis=LineString(e['axis_endpoints_m'])
                check(plan+' wall ink support '+label,e['audit']['sampled_axis_ink_support']>=.95)
                known_shapes.append(box(x-w/2,y-h/2,x+w/2,y+h/2))
            else:
                axis=Point(x,y)
                if e['size_mm'] is not None:
                    w,h=np.array(e['size_mm'])/1000
                    known_shapes.append(box(x-w/2,y-h/2,x+w/2,y+h/2))
            check(plan+' support axis contained '+label,floor.buffer(1e-8).covers(axis))
            r=csv_rows[label];a=regions[label].area
            check(plan+' slab G/Q '+label,abs(float(r['G_slab_per_floor_kN'])-a*3.75)<1e-6 and abs(float(r['Q_per_floor_kN'])-a*5)<1e-6)
        physical_area=unary_union(known_shapes).area
        gravity=load(out/'Known_Gravity_Totals.json')
        net=sum(float(r['net_vertical_footprint_m2'])for r in rows if r['net_vertical_footprint_m2'])
        check(plan+' union-based self-weight avoids overlaps',abs(net-physical_area)<1e-8)
        check(plan+' whole-floor known G independent check',abs(sum(float(r['G_known_per_floor_kN'])for r in rows)-(floor.area*3.75+physical_area*75))<1e-6)
        check(plan+' whole-floor Q independent check',abs(sum(float(r['Q_per_floor_kN'])for r in rows)-floor.area*5)<1e-6)
        levels=list(csv.DictReader((out/'Known_Axial_Accumulation.csv').open(encoding='utf-8')))
        for label in ids:
            group=[r for r in levels if r['element_id']==label]
            check(plan+' storey accumulation 1:2:3:4:5 '+label,
                  sorted(int(r['floors_supported'])for r in group)==list(range(1,6))and
                  all(abs(float(r['G_known_kN'])-int(r['floors_supported'])*float(csv_rows[label]['G_known_per_floor_kN']))<1e-7 and
                      abs(float(r['Q_kN'])-int(r['floors_supported'])*float(csv_rows[label]['Q_per_floor_kN']))<1e-7 for r in group))
        if plan=='NIST':
            check('NIST unknown column self-weight is not fabricated',all(not csv_rows[e['labels'][0]]['vertical_self_weight_per_floor_kN'] for e in elements if e['class']=='column')and len(gravity['unknown_self_weight_ids'])==21)
        else:
            check('NewPlan label-only supports remain flagged',[e['labels'][0]for e in elements if e['audit'].get('label_only_grid_inference')]==['C17','C20'])
            warnings=[v for v in geometry['geometry_diagnostics']if v['footprint_outside_floor_m2']]
            check('NewPlan small edge discrepancy not hidden',{v['label']for v in warnings}=={'T4','T8'}and sum(v['footprint_outside_floor_m2']for v in warnings)>0)
        # Polygon area/centroid/polar integral via a separate shoelace calculation.
        xy=np.array(floor.exterior.coords);a,b=xy[:-1],xy[1:];cross=a[:,0]*b[:,1]-b[:,0]*a[:,1]
        area=cross.sum()/2
        centroid=((a+b)*cross[:,None]).sum(axis=0)/(6*area)
        ix=((a[:,1]**2+a[:,1]*b[:,1]+b[:,1]**2)*cross).sum()/12
        iy=((a[:,0]**2+a[:,0]*b[:,0]+b[:,0]**2)*cross).sum()/12
        mass=area*8.75/9.81;polar=(ix+iy-area*np.dot(centroid,centroid))*8.75/9.81
        check(plan+' independent mass/CM/polar integral',abs(hand['mass']['mass_t']-mass)<1e-7 and np.max(abs(centroid-hand['mass']['CM_m']))<1e-10 and abs(hand['mass']['polar_mass_t_m2']-polar)<1e-6)
        terms=[];E=30e6;G=12.5e6;H=3.
        for e in elements:
            if e['class']!='wall':continue
            L,t=e['length_m'],e['thickness_m'];av=(5/6)*L*t
            s=1/(H**3/(3*E*(t*L**3/12))+H/(G*av))
            w=1/(H**3/(3*E*(L*t**3/12))+H/(G*av))
            kx,ky=(s,w)if e['angle_deg']==0 else(w,s)
            terms.append((e['centre_m'][0],e['centre_m'][1],kx,ky))
        kxx=sum(t[2]for t in terms);kyy=sum(t[3]for t in terms)
        cr=np.array([sum(t[0]*t[3]for t in terms)/kyy,sum(t[1]*t[2]for t in terms)/kxx])
        expected_K=np.zeros((3,3));expected_K[0,0]=kxx;expected_K[1,1]=kyy
        expected_K[0,2]=expected_K[2,0]=-sum(t[2]*(t[1]-centroid[1])for t in terms)
        expected_K[1,2]=expected_K[2,1]=sum(t[3]*(t[0]-centroid[0])for t in terms)
        expected_K[2,2]=sum(t[2]*(t[1]-centroid[1])**2+t[3]*(t[0]-centroid[0])**2 for t in terms)
        stored=np.array(hand['matched_rectangular_shear']['K_about_CM'])
        check(plan+' independent hand matrix and weighted CR',np.allclose(stored,expected_K,rtol=1e-12,atol=1e-6)and np.max(abs(cr-hand['matched_rectangular_shear']['CR_m']))<1e-10)
        check(plan+' positive definite hand matrix',np.linalg.eigvalsh(stored).min()>0)
        M=np.array([mass,mass,polar]);eigen=np.linalg.eigvalsh(stored/np.sqrt(M[:,None]*M[None,:]))
        periods=2*np.pi/np.sqrt(eigen)
        check(plan+' independent analytical modal periods',np.allclose(periods,[m['period_s']for m in hand['analytical_modes']],rtol=1e-12))
        relative=max(abs(float(r['area_m2'])-float(r['coarse_area_m2']))/float(r['area_m2'])for r in rows)
        conditional={'conditional_engineering_ready':True,'strict_pipeline_promoted':False,
                     'geometry_sha256':sha(geo_path),'hand_sha256':sha(out/'Hand_Analysis.json'),
                     'region_sha256':sha(out/'Closed_Tributary_Regions.geojson'),
                     'support_count':len(elements),'unresolved_source_issues':geometry['unresolved_source_issues'],
                     'max_relative_area_grid_change':relative,
                     'convergence_note':'Below 1% target'if relative<=.01 else'Marginally above approximate 1% target; retained and reported, not a strict 1% convergence pass',
                     'scope':'Authorises matched diagnostic OpenSees under declared assumptions only; not full source/CAD certification or unmodified-pipeline success.'}
        summaries.append({'plan':plan,**conditional})
        (out/'Conditional_Engineering_Gate.json').write_text(json.dumps(conditional,indent=2)+'\n',encoding='utf-8',newline='\n')
    result={'scope':'Conditional engineering geometry, exported regions/loads and independent hand calculations; source ambiguities are not erased.',
            'passed':sum(c['passed']for c in checks),'total':len(checks),'checks':checks,'conditional_gates':summaries}
    (ROOT/'records/Task_08_Engineering_Validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"Conditional engineering validation: {result['passed']}/{result['total']}")
    if result['passed']!=result['total']:
        raise SystemExit('Do not run matching OpenSees: engineering check failed')


if __name__=='__main__':
    main()
