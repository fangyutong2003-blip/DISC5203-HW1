"""Conditional closed tributary regions, known gravity and analytical diaphragm model."""
import copy
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.linalg import eigh
from shapely.geometry import box,LineString,mapping
from shapely.ops import unary_union

from task03_centres import stiffness_case

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def csv_write(path,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def footprint(element):
    cx,cy=element['centre_m']
    if element['class']=='column':
        if element['size_mm'] is None:
            return None
        w,h=np.array(element['size_mm'])/1000
    else:
        L,t=element['length_m'],element['thickness_m']
        w,h=(L,t)if element['angle_deg']==0 else(t,L)
    return box(cx-w/2,cy-h/2,cx+w/2,cy+h/2)


def support_segments(elements,trim=True):
    columns=unary_union([g for e in elements if e['class']=='column' for g in [footprint(e)] if g is not None])
    result=[]
    for element in elements:
        if element['class']=='column':
            x,y=element['centre_m'];segments=[[x,y,x,y]]
        else:
            axis=LineString(element['axis_endpoints_m'])
            if trim and not columns.is_empty:
                axis=axis.difference(columns)
            lines=[axis]if axis.geom_type=='LineString'else list(axis.geoms)
            segments=[]
            for line in lines:
                if not line.is_empty and line.length>1e-9:
                    a,b=line.coords[0],line.coords[-1]
                    segments.append([*a,*b])
            assert segments,'Wall wholly absorbed by a column; require explicit composite support'
        result.append({'label':element['labels'][0],'segments_m':segments})
    return result


def edges(a,b,step):
    values=np.arange(a,b-1e-10,step)
    return np.r_[values,b]


def allocate(elements,bounds,step,trim=True):
    xe,ye=edges(bounds[0],bounds[2],step),edges(bounds[1],bounds[3],step)
    X=((xe[1:]+xe[:-1])/2)[None,:]
    Y=((ye[1:]+ye[:-1])/2)[:,None]
    best=np.full((len(ye)-1,len(xe)-1),np.inf)
    owner=np.full(best.shape,-1,np.int16)
    segments=support_segments(elements,trim)
    for index,support in enumerate(segments):
        d=np.full(best.shape,np.inf)
        for ax,ay,bx,by in support['segments_m']:
            trial=abs(X-np.clip(X,min(ax,bx),max(ax,bx)))+abs(Y-np.clip(Y,min(ay,by),max(ay,by)))
            d=np.minimum(d,trial)
        wins=d<best-1e-10
        owner[wins]=index;best[wins]=d[wins]
    weights=np.diff(ye)[:,None]*np.diff(xe)[None,:]
    area=np.bincount(owner.ravel(),weights=weights.ravel(),minlength=len(elements))
    assert np.all(owner>=0)
    return area,owner,xe,ye,segments


def polygonise(owner,xe,ye,count):
    active={};pieces=[[]for _ in range(count)]
    for row in range(owner.shape[0]+1):
        runs=set()
        if row<owner.shape[0]:
            line=owner[row]
            breaks=np.flatnonzero(np.r_[True,line[1:]!=line[:-1],True])
            runs={(int(line[a]),int(a),int(b))for a,b in zip(breaks[:-1],breaks[1:])}
        for key,start in list(active.items()):
            if key not in runs:
                who,a,b=key
                pieces[who].append(box(xe[a],ye[start],xe[b],ye[row]))
                del active[key]
        for key in runs:
            active.setdefault(key,row)
    return [unary_union(part)for part in pieces]


def walls_for_hand(elements,p):
    walls=[]
    for element in elements:
        if element['class']!='wall':
            continue
        L,t=element['length_m'],element['thickness_m'];H=p['height_m'];E=p['E_kN_m2'];G=E/(2*(1+p['nu']))
        A=L*t;Av=p['shear_factor']*A;Is=t*L**3/12;Iw=L*t**3/12
        kb=3*E*Is/H**3;kw=3*E*Iw/H**3
        walls.append({'label':element['labels'][0],'centre_m':element['centre_m'],'angle_deg':element['angle_deg'],
                      'length_m':L,'thickness_m':t,'A_m2':A,'Av_m2':Av,'I_strong_m4':Is,'I_weak_m4':Iw,
                      'k_strong_bending_kN_m':kb,'k_weak_bending_kN_m':kw,
                      'k_strong_shear_kN_m':1/(1/kb+H/(G*Av)),
                      'k_weak_shear_kN_m':1/(1/kw+H/(G*Av))})
    return walls


def mass_for(bounds,intensity=8.75):
    a,b,c,d=bounds;A=(c-a)*(d-b);M=A*intensity/9.81
    return {'area_m2':A,'CM_m':[(a+c)/2,(b+d)/2],'mass_t':M,
            'polar_mass_t_m2':M*((c-a)**2+(d-b)**2)/12,'intensity_kN_m2':intensity}


def modes(K,mass):
    eigenvalues,shapes=eigh(np.asarray(K),np.diag([mass['mass_t'],mass['mass_t'],mass['polar_mass_t_m2']]))
    return [{'mode':i+1,'period_s':float(2*np.pi/np.sqrt(value)),
             'rotational_mass_fraction':float(mass['polar_mass_t_m2']*shapes[2,i]**2)}for i,value in enumerate(eigenvalues)]


def run(plan,settings,refined=False):
    source=ROOT/'outputs'/plan/'geometry_recovery_r1/Elements_Conditional.json'
    geometry=load(source);elements=geometry['elements'];bounds=geometry['floor']['bounds_m']
    out=ROOT/'outputs'/plan/('engineering_r1_refined' if refined else 'engineering_r1');out.mkdir(parents=True,exist_ok=True)
    area,owner,xe,ye,segments=allocate(elements,bounds,settings['region_step_m'])
    coarse,*_=allocate(elements,bounds,settings['region_check_step_m'])
    untrimmed,*_=allocate(elements,bounds,settings['region_step_m'],False)
    polygons=polygonise(owner,xe,ye,len(elements))
    floor=box(*bounds);combined=unary_union(polygons)
    checks={'area_sum_m2':float(area.sum()),'polygon_area_sum_m2':sum(p.area for p in polygons),
            'floor_area_m2':floor.area,'gap_or_outside_m2':combined.symmetric_difference(floor).area,
            'overlap_m2':sum(p.area for p in polygons)-combined.area,
            'max_element_grid_change_m2':float(np.max(abs(area-coarse))),
            'minimum_region_area_m2':float(min(area)),
            'max_polygon_vs_raster_m2':max(abs(p.area-a)for p,a in zip(polygons,area))}
    assert abs(area.sum()-floor.area)<1e-7 and checks['gap_or_outside_m2']<1e-7 and abs(checks['overlap_m2'])<1e-7
    assert checks['max_polygon_vs_raster_m2']<1e-7
    assert min(area)>0,'Empty support region; retain as composite ambiguity rather than completed individual allocation'
    features={'type':'FeatureCollection','properties':{'method':'Closed raster L1 nearest point/finite trimmed axis; variable edge cells preserve exact domain',
               'step_m':settings['region_step_m'],'assumption_status':geometry['status']},
              'features':[{'type':'Feature','properties':{'id':e['labels'][0],'area_m2':float(a)},'geometry':mapping(poly)}for e,a,poly in zip(elements,area,polygons)]}
    write(out/'Closed_Tributary_Regions.geojson',features)
    write(out/'Region_Conservation.json',checks)
    write(out/'Gravity_Axis_Segments.json',{'trim_known_column_footprints':True,'supports':segments})
    prior_footprints=unary_union([])
    rows=[];levels=[];net_area=0.
    for e,a,ac,au in zip(elements,area,coarse,untrimmed):
        fp=footprint(e)
        net=None if fp is None else fp.difference(prior_footprints).area
        if fp is not None:
            prior_footprints=unary_union([prior_footprints,fp]);net_area+=net
        self_weight=None if net is None else net*3*25
        known_G=float(a*3.75+(self_weight or 0.));Q=float(a*5)
        row={'element_id':e['labels'][0],'element_type':e['class'],'area_m2':float(a),
             'coarse_area_m2':float(ac),'untrimmed_axis_area_m2':float(au),
             'G_slab_per_floor_kN':float(a*3.75),'Q_per_floor_kN':Q,
             'net_vertical_footprint_m2':net,'vertical_self_weight_per_floor_kN':self_weight,
             'G_known_per_floor_kN':known_G,'G_complete':self_weight is not None,
             'label_only_support':e.get('audit',{}).get('label_only_grid_inference',False)}
        rows.append(row)
        for count in range(1,6):
            levels.append({'element_id':row['element_id'],'floors_supported':count,'level':6-count,
                           'G_known_kN':known_G*count,'Q_kN':Q*count,'G_complete':row['G_complete']})
    assert abs(net_area-prior_footprints.area)<1e-8
    gravity={'scope':'Known slab and net vertical concrete only. NIST unknown column self-weight is null, so complete axial design totals are not claimed.',
             'G_slab_kN_m2':3.75,'Q_kN_m2':5.,'load_source':'Transferred HW1 exercise assumptions: 150 mm slab, 25 kN/m3 concrete, Q=5; not loads printed on these drawings',
             'G_known_per_floor_kN':sum(r['G_known_per_floor_kN']for r in rows),
             'Q_per_floor_kN':sum(r['Q_per_floor_kN']for r in rows),
             'known_net_vertical_footprint_m2':net_area,'known_vertical_self_weight_kN':net_area*75,
             'unknown_self_weight_ids':[r['element_id']for r in rows if not r['G_complete']],
             'joint_allocation':'Column footprints first, then remaining labelled wall footprints in ID order; union prevents overlap double counting',
             'five_storey_G_known_kN':sum(r['G_known_per_floor_kN']for r in rows)*5,
             'five_storey_Q_kN':sum(r['Q_per_floor_kN']for r in rows)*5}
    csv_write(out/'Tributary_and_Known_Loads.csv',rows)
    csv_write(out/'Known_Axial_Accumulation.csv',levels)
    write(out/'Known_Gravity_Totals.json',gravity)
    mass=mass_for(bounds)
    p=load(ROOT/'params_mechanics.json')
    p.update(plan=plan,selection_status=geometry['status'],element_record=source.relative_to(ROOT).as_posix())
    walls=walls_for_hand(elements,p)
    case=stiffness_case(walls,np.array(mass['CM_m']),True,True)
    bending=stiffness_case(walls,np.array(mass['CM_m']),False,True)
    strong=stiffness_case(walls,np.array(mass['CM_m']),True,False)
    sensitivities={}
    if plan=='NewPlan':
        alternate_mass=mass_for([0,0,46,18])
        sensitivities['grid_axis_floor_mass']={'mass':alternate_mass,'modes':modes(case['K_about_CM'],alternate_mass),
                                               'CR_m':case['CR_m'],'eccentricity_m':case['eccentricity_m']}
        keep=[e for e in elements if e['labels'][0] not in ('C17','C20')]
        altered,*_=allocate(keep,bounds,settings['region_step_m'])
        original={e['labels'][0]:a for e,a in zip(elements,area)}
        delta=[{'element_id':e['labels'][0],'area_without_label_only_columns_m2':float(a),
                'area_change_m2':float(a-original[e['labels'][0]]),'G_plus_Q_change_per_floor_kN':float((a-original[e['labels'][0]])*8.75)}for e,a in zip(keep,altered)]
        csv_write(out/'Label_Only_Column_Sensitivity.csv',delta)
        sensitivities['omit_C17_C20']={'area_sum_m2':float(sum(altered)),
            'omitted_baseline_areas_m2':{k:float(original[k])for k in ('C17','C20')},
            'max_other_support_area_increase_m2':max(r['area_change_m2']for r in delta),
            'CM_CR_change_m':0.,'reason':'Uniform mass prescribed independently; columns excluded from lateral model. Gravity redistribution remains significant.'}
    else:
        ideal=copy.deepcopy(walls)
        mid=mass['CM_m']
        for wall in ideal:
            if wall['angle_deg']==0:wall['centre_m'][0]=mid[0]
            else:wall['centre_m'][1]=mid[1]
        ideal_case=stiffness_case(ideal,np.array(mid),True,True)
        sensitivities['symmetric_idealisation']={'CR_m':ideal_case['CR_m'],'eccentricity_m':ideal_case['eccentricity_m'],
            'interpretation':'Equal opposing source bars centred tangentially. Measured schematic offsets are not verified real-building asymmetry.'}
    hand={'plan':plan,'status':geometry['status'],'model_promoted':False,
          'geometry_record':source.relative_to(ROOT).as_posix(),'mass':mass,'parameters':p,'walls':walls,
          'matched_rectangular_shear':case,'bending_only':bending,'strong_direction_only':strong,
          'analytical_modes':modes(case['K_about_CM'],mass),'sensitivities':sensitivities,
          'mass_note':'Uniform prescribed 8.75 kN/m2 floor mass; known vertical-member gravity weights are reported separately and excluded here, matching Plan 3 convention.',
          'lateral_note':'Labelled rectangular bars with strong/weak bending, shear, J=0; not coupled monolithic L-wall shells; columns provide no lateral stiffness.'}
    write(out/'Hand_Analysis.json',hand)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(13,6)if plan=='NewPlan'else(9,9))
    for i,(e,poly)in enumerate(zip(elements,polygons)):
        for piece in ([poly]if poly.geom_type=='Polygon'else poly.geoms):
            x,y=piece.exterior.xy
            ax.fill(x,y,color=plt.get_cmap('tab20')(i%20),alpha=.18)
            ax.plot(x,y,'--',color='gray',lw=.45)
        point=poly.representative_point()
        ax.text(point.x,point.y,e['labels'][0],fontsize=7,ha='center')
        fp=footprint(e)
        if fp is not None:
            ax.fill(*fp.exterior.xy,color='black',alpha=.65)
        else:
            ax.plot(*e['centre_m'],'ko',ms=3)
    ax.plot(*floor.exterior.xy,color='black',lw=1)
    ax.plot(*mass['CM_m'],'r+',ms=12,label='CM')
    ax.plot(*case['CR_m'],'bx',ms=8,label='CR')
    ax.set(aspect='equal',xlabel='x (m)',ylabel='y (m)',title=plan+' | Closed conditional L1 regions, walls and CM/CR')
    ax.legend();fig.tight_layout();fig.savefig(out/'Closed_Regions_and_Centres.png',dpi=160);plt.close(fig)
    print(plan,'regions',len(polygons),'area',round(floor.area,6),'coarse max change',round(checks['max_element_grid_change_m2'],4),
          'CM',mass['CM_m'],'CR',case['CR_m'],'e',case['eccentricity_m'],flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refined',action='store_true',help='Retain a separate 0.025 m run checked against 0.05 m; no image rule changes')
    args=parser.parse_args()
    settings=load(ROOT/'params_geometry_recovery_r1.json')
    if args.refined:
        settings['region_step_m']=.025
        settings['region_check_step_m']=.05
    for plan in ('NewPlan','NIST'):
        run(plan,settings,args.refined)


if __name__=='__main__':
    main()
