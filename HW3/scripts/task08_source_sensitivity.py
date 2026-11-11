"""Retain calibration and endpoint uncertainty cases without changing matched baseline files."""
import copy
import itertools
import json
from pathlib import Path

import numpy as np
from task03_centres import stiffness_case
from task08_areas_and_hand import walls_for_hand

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    for plan in ('NewPlan','NIST'):
        out=ROOT/'outputs'/plan/'engineering_r1_refined'
        h=load(out/'Hand_Analysis.json');g=load(ROOT/h['geometry_record'])
        alternate=copy.deepcopy(g['elements']);cal=g['calibration']
        for element in alternate:
            if element['class']!='wall':continue
            px,py=element['audit']['measured_centre_px']
            point=[(px-cal['global_affine_intercepts_px']['x'])/cal['global_affine_px_per_m']['x'],
                   (cal['global_affine_intercepts_px']['y']-py)/cal['global_affine_px_per_m']['y']]
            if plan=='NIST':
                if element['angle_deg']==0:point[1]=element['centre_m'][1]
                else:point[0]=element['centre_m'][0]
            element['centre_m']=point
        alternative=stiffness_case(walls_for_hand(alternate,h['parameters']),np.array(h['mass']['CM_m']),True,True)
        result={'scope':'Analytical source-uncertainty sensitivities, not additional OpenSees runs or a statistical confidence interval.',
                'global_affine_instead_of_piecewise':{'CR_m':alternative['CR_m'],'eccentricity_m':alternative['eccentricity_m'],
                    'CR_shift_m':float(np.linalg.norm(np.array(alternative['CR_m'])-h['matched_rectangular_shear']['CR_m']))}}
        if plan=='NIST':
            walls=[e for e in g['elements']if e['class']=='wall'];cases=[]
            for signs in itertools.product((-1,1),repeat=4):
                items=copy.deepcopy(walls)
                for element,sign in zip(items,signs):
                    element['length_m']+=sign*2*element['audit']['endpoint_uncertainty_m']
                    assert element['length_m']>0
                case=stiffness_case(walls_for_hand(items,h['parameters']),np.array(h['mass']['CM_m']),True,True)
                cases.append({'length_signs':list(signs),'lengths_m':[e['length_m']for e in items],
                              'CR_m':case['CR_m'],'eccentricity_m':case['eccentricity_m']})
            result['independent_endpoint_extreme_cases']={
                'definition':'Each endpoint +/-2 source pixels. Opposite endpoint motions give each whole length +/-4 pixels; centres, thickness, mass and floor border convention fixed.',
                'statistical_interpretation':'None; deterministic extreme-box sensitivity, not probability or confidence interval.',
                'maximum_eccentricity_m':max(c['eccentricity_m']for c in cases),'cases':cases}
        (out/'Source_Uncertainty_Cases.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(plan,'global/piecewise CR shift',result['global_affine_instead_of_piecewise']['CR_shift_m'],
              'endpoint box max e',result.get('independent_endpoint_extreme_cases',{}).get('maximum_eccentricity_m'))


if __name__=='__main__':
    main()
