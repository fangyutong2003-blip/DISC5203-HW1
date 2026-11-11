"""Independently check saved solver matrices, reactions, kinematics and modal limits."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    checks=[];summaries=[]
    def check(name,value,error=None):
        item={'check':name,'passed':bool(value)}
        if error is not None:item['error']=float(error)
        checks.append(item)
    for plan in ('NewPlan','NIST'):
        out=ROOT/'outputs'/plan/'engineering_r1_refined'
        h=load(out/'Hand_Analysis.json');r=load(out/'OpenSees_Result.json')
        cm=np.array(r['CM_m']);F=np.array(r['F_about_CM']);K=np.array(r['K_about_CM'])
        expectedF=np.array(h['matched_rectangular_shear']['F_about_CM'])
        err=np.max(abs(F-expectedF))/np.max(abs(expectedF))
        check(plan+' hand/model flexibility',err<1e-9,err)
        crerr=np.max(abs(np.array(r['solver_CR_m'])-h['matched_rectangular_shear']['CR_m']))
        check(plan+' independent hand/model CR',crerr<1e-8,crerr)
        check(plan+' symmetric flexibility',np.max(abs(F-F.T))/np.max(abs(F))<1e-11)
        check(plan+' inverse and positive stiffness',np.max(abs(K@F-np.eye(3)))<1e-10 and min(np.linalg.eigvalsh(K))>0)
        check(plan+' explicit rigidDiaphragm Transformation model',r['model']['constraints']=='Transformation' and r['model']['diaphragm_command'].startswith('rigidDiaphragm(3,1,'))
        check(plan+' cantilever section and fixities',r['model']['wall_top_fixity']==[0,0,1,0,0,0] and r['model']['intrinsic_vertical_wall_J_m4']==0 and r['model']['strong_weak_bending_included'])
        check(plan+' matched wall count',r['model']['wall_elements']==len(h['walls'])==(8 if plan=='NewPlan' else 4))
        check(plan+' original hand input hash',hashlib.sha256((out/'Hand_Analysis.json').read_bytes()).hexdigest()==r['hand_input_sha256'])
        all_cases={f'unit_{i}':c for i,c in enumerate(r['unit_cases'])}|r['cases']
        for name,case in all_cases.items():
            q=np.array(case['master_displacement_u_v_phi']);loadvec=np.array(case['load_at_CM_Px_Py_Mz'])
            reaction=np.zeros(3);kinematic=0.
            for wall in case['walls']:
                R=wall['base_reaction_global'];dx,dy=np.array(wall['centre_m'])-cm
                reaction+=np.array([R[0],R[1],R[5]+dx*R[1]-dy*R[0]])
                disp=wall['top_displacement_global']
                kinematic=max(kinematic,abs(disp[0]-(q[0]-dy*q[2])),abs(disp[1]-(q[1]+dx*q[2])),abs(disp[5]-q[2]))
            check(plan+' '+name+' converged/equilibrium',case['solver_exit']==0 and np.max(abs(reaction+loadvec))<1e-6,np.max(abs(reaction+loadvec)))
            check(plan+' '+name+' rigid-plane kinematics',kinematic<1e-11,kinematic)
            check(plan+' '+name+' q=F P',np.max(abs(q-F@loadvec))<1e-11)
        for direction in ('x','y'):
            check(plan+' '+direction+' load through CR gives zero rotation',abs(r['cases']['unit_'+direction+'_CR']['master_displacement_u_v_phi'][2])<1e-12)
            direct=r['cases']['design_'+direction];push=r['cases']['push_'+direction+'_CR'];turn=r['cases']['turn_'+direction]
            error=np.max(abs(np.array(direct['master_displacement_u_v_phi'])-np.array(push['master_displacement_u_v_phi'])-np.array(turn['master_displacement_u_v_phi'])))
            check(plan+' '+direction+' push/turn displacement decomposition',error<1e-11,error)
            error=max(np.max(abs(np.array(a['base_reaction_global'])-np.array(b['base_reaction_global'])-np.array(c['base_reaction_global'])))for a,b,c in zip(direct['walls'],push['walls'],turn['walls']))
            check(plan+' '+direction+' push/turn wall-force decomposition',error<1e-6,error)
        bending=np.array(r['bending_only_F_about_CM']);expected=np.array(h['bending_only']['F_about_CM'])
        check(plan+' bending-only limit',np.max(abs(bending-expected))/np.max(abs(expected))<1e-9)
        for case in r['section_limit_cases']:
            section=h['walls'][0]
            axis='strong'if case['load_xy'][0]else'weak'
            kind='bending'if case['bending_only']else'shear'
            displacement=case['ux_m']if axis=='strong'else case['uy_m']
            expected=1/section[f'k_{axis}_{kind}_kN_m']
            check(plan+' isolated '+axis+' '+kind+' section limit',abs(displacement-expected)/abs(expected)<1e-9)
        M=np.diag([h['mass']['mass_t'],h['mass']['mass_t'],h['mass']['polar_mass_t_m2']])
        for hand_mode,solver_mode in zip(h['analytical_modes'],r['modal']['opensees_modes']):
            check(plan+' modal period '+str(hand_mode['mode']),abs(hand_mode['period_s']-solver_mode['period_s'])/hand_mode['period_s']<1e-9)
            v=np.array(solver_mode['master_shape_u_v_phi']);lam=solver_mode['omega_squared_rad2_s2']
            residual=np.linalg.norm(np.array(h['matched_rectangular_shear']['K_about_CM'])@v-lam*M@v)/(np.linalg.norm(K)*np.linalg.norm(v))
            check(plan+' modal eigenvector '+str(hand_mode['mode']),residual<1e-10,residual)
        forces=list(csv.DictReader((out/'Wall_Force_Push_and_Turn.csv').open(encoding='utf-8')))
        for row in forces:
            error=max(abs(float(row['direct_fx_kN'])+float(row['turn_fx_kN'])-float(row['model_total_fx_kN'])),
                      abs(float(row['direct_fy_kN'])+float(row['turn_fy_kN'])-float(row['model_total_fy_kN'])))
            check(plan+' independent CR force shares '+row['load_direction']+' '+row['wall'],error<1e-7,error)
        summaries.append({'plan':plan,'max_relative_F_error':float(err),'max_CR_coordinate_error_m':float(crerr),
                          'CR_m':r['solver_CR_m'],'eccentricity_m':r['solver_eccentricity_m'],
                          'periods_s':[m['period_s']for m in r['modal']['opensees_modes']]})
    record={'scope':'Actual matched single-floor diagnostic solver checks under conditional geometry assumptions, not source validation or a full multi-storey design.',
            'passed':sum(c['passed']for c in checks),'total':len(checks),'checks':checks,'summaries':summaries}
    (ROOT/'records/Task_08_OpenSees_Validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"Task 8 actual OpenSees checks: {record['passed']}/{record['total']}")
    if record['passed']!=record['total']:
        print([c for c in checks if not c['passed']])
        raise SystemExit('OpenSees verification failed')


if __name__=='__main__':
    main()
