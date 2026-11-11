"""Run the matched conditional additional-plan models only after the hand/area gate."""
import hashlib
import json
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
from task04_opensees import solve,isolated_wall_limit
from task06_modify import modal
from task08_areas_and_hand import csv_write

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    validation=load(ROOT/'records/Task_08_Engineering_Validation.json')
    assert validation['passed']==validation['total']
    for plan in ('NewPlan','NIST'):
        out=ROOT/'outputs'/plan/'engineering_r1_refined'
        gate=load(out/'Conditional_Engineering_Gate.json')
        assert gate['conditional_engineering_ready'] and not gate['strict_pipeline_promoted']
        assert sha(out/'Hand_Analysis.json')==gate['hand_sha256']
        hand=load(out/'Hand_Analysis.json')
        assert sha(ROOT/hand['geometry_record'])==gate['geometry_sha256']
        walls=hand['walls'];p=hand['parameters'];cm=np.array(hand['mass']['CM_m'])
        units=[solve(walls,cm,p,v)for v in np.eye(3)]
        F=np.array([c['master_displacement_u_v_phi']for c in units]).T;K=np.linalg.inv(F)
        cr=np.array([cm[0]-F[2,1]/F[2,2],cm[1]+F[2,0]/F[2,2]])
        dx,dy=cr-cm;force=p['design_demonstration_force_kN']
        cases={name:solve(walls,cm,p,v)for name,v in {
            'design_x':[force,0,0],'design_y':[0,force,0],
            'unit_x_CR':[1,0,-dy],'unit_y_CR':[0,1,dx],
            'push_x_CR':[force,0,-dy*force],'turn_x':[0,0,dy*force],
            'push_y_CR':[0,force,dx*force],'turn_y':[0,0,-dx*force]}.items()}
        bending_F=np.array([solve(walls,cm,p,v,True)['master_displacement_u_v_phi']for v in np.eye(3)]).T
        limits=[isolated_wall_limit(walls[0],p,bending,load)
                for bending in (False,True)for load in ([1,0],[0,1])]
        modal_mass={'one_storey_mass_t':hand['mass']['mass_t'],
                    'polar_mass_moment_about_CM_t_m2':hand['mass']['polar_mass_t_m2']}
        eigen=modal(walls,cm,p,modal_mass)
        result={'plan':plan,'status':'Conditional matched diagnostic model; no unchanged-pipeline/full-source promotion',
                'model_promoted':False,'solver_version':ops.version(),
                'hand_input_sha256':sha(out/'Hand_Analysis.json'),
                'model':{'ndm':3,'ndf':6,'element_type':'ElasticTimoshenkoBeam','elements_per_wall':1,
                         'wall_elements':len(walls),'diaphragm_command':'rigidDiaphragm(3,1,*wall_top_nodes)',
                         'constraints':'Transformation','wall_top_fixity':[0,0,1,0,0,0],
                         'strong_weak_bending_included':True,'intrinsic_vertical_wall_J_m4':0.,
                         'columns_in_lateral_model':False,'section_limit_test_note':'Generic isolated section aligned with test global x strong and y weak, distinct from source wall orientation'},
                'CM_m':cm.tolist(),'solver_CR_m':cr.tolist(),'solver_eccentricity_m':float(np.linalg.norm(cr-cm)),
                'F_about_CM':F.tolist(),'K_about_CM':K.tolist(),'unit_cases':units,'cases':cases,
                'bending_only_F_about_CM':bending_F.tolist(),'section_limit_cases':limits,'modal':eigen}
        (out/'OpenSees_Result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
        J=np.array(hand['matched_rectangular_shear']['K_about_CR'])[2,2]
        rows=[]
        for direction in ('x','y'):
            T=dy*force if direction=='x'else-dx*force
            for wall,response in zip(walls,cases['design_'+direction]['walls']):
                ks,kw=wall['k_strong_shear_kN_m'],wall['k_weak_shear_kN_m']
                kx,ky=(ks,kw)if wall['angle_deg']==0 else(kw,ks)
                x,y=np.array(wall['centre_m'])-cr
                direct_x=kx/K[0,0]*force if direction=='x' else 0.
                direct_y=ky/K[1,1]*force if direction=='y' else 0.
                rows.append({'load_direction':direction,'wall':wall['label'],'assumed_force_kN':force,
                             'direct_fx_kN':direct_x,'direct_fy_kN':direct_y,
                             'turn_fx_kN':float(-kx*y*T/J),'turn_fy_kN':float(ky*x*T/J),
                             'model_total_fx_kN':response['resisting_demand_fx_kN'],
                             'model_total_fy_kN':response['resisting_demand_fy_kN']})
        csv_write(out/'Wall_Force_Push_and_Turn.csv',rows)
        print(plan,'actual OpenSees',ops.version(),'CR',cr.tolist(),'e',result['solver_eccentricity_m'],flush=True)


if __name__=='__main__':
    main()
