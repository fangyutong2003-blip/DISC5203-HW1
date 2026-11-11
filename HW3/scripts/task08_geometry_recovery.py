"""Supplementary solid-symbol recovery; never overwrite the frozen classical pipeline."""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
from shapely.geometry import box,LineString,Point,mapping
from task08_review_packages import locator_label

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def components(mask):
    n,labels,stats,centres=cv2.connectedComponentsWithStats(mask,8)
    result=[]
    for i in range(1,n):
        x,y,w,h,area=map(int,stats[i])
        result.append({'component_id':i,'bbox_px':[x,y,w,h],
                       'centre_px':[x+(w-1)/2,y+(h-1)/2],
                       'area_px':area,'fill_fraction':area/(w*h),
                       'aspect_ratio':max(w,h)/min(w,h)})
    return result


def cluster(values,tolerance):
    groups=[]
    for value in sorted(values):
        if groups and abs(value-np.mean(groups[-1]))<=tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [float(np.mean(g)) for g in groups]


def interp_extrap(value,x,y):
    if value<x[0]:
        return float(y[0]+(value-x[0])*(y[1]-y[0])/(x[1]-x[0]))
    if value>x[-1]:
        return float(y[-1]+(value-x[-1])*(y[-1]-y[-2])/(x[-1]-x[-2]))
    return float(np.interp(value,x,y))


def finalise(plan,p,draft):
    cfg=p[plan]
    out=ROOT/'outputs'/plan/'geometry_recovery_r1'
    gx,gy=draft['measured_grid_px']['x'],draft['measured_grid_px']['y']
    mx,my=cfg['grid_x_m'],list(reversed(cfg['grid_y_m']))
    assert len(gx)==len(mx) and len(gy)==len(my),'Unresolved grid detection; do not invent axes'
    xf=np.polyfit(mx,gx,1);yf=np.polyfit(my,gy,1)
    def metric(px,py):
        return [interp_extrap(px,gx,mx),interp_extrap(py,gy,my)]
    def pixel(x,y):
        return [interp_extrap(x,mx,gx),interp_extrap(y,list(reversed(my)),list(reversed(gy)))]
    elements=[]
    if plan=='NewPlan':
        slots=[(0,c)for c in range(8)]+[(1,c)for c in (0,1,3,4,6,7)]+[(2,c)for c in range(8)]+[(3,c)for c in range(8)]
    else:
        # The visible square symbols occupy these grid positions; four wall positions are excluded.
        slots=[(r,c)for r in range(5)for c in range(5)if (r,c) not in ((0,2),(2,0),(2,4),(4,2))]
    for index,(row,col) in enumerate(slots,1):
        px,py=gx[col],gy[row]
        near=[v for v in draft['column_candidates'] if np.linalg.norm(np.array(v['centre_px'])-[px,py])<p['coordinate_cluster_tolerance_m']*max(draft['initial_px_per_m'].values())]
        label=f'C{index}' if plan=='NewPlan' else f'NC{index:02d}'
        joint=plan=='NewPlan' and label in ('C25','C28')
        label_only=plan=='NewPlan' and label in cfg['assumed_label_only_columns']
        assert near or joint or label_only,(label,'No symbol or declared inference')
        elements.append({'id':len(elements)+1,'labels':[label],'class':'column',
                         'centre_m':[mx[col],my[row]],'measured_grid_centre_px':[px,py],
                         'size_mm':cfg['column_size_mm'],
                         'provenance':{'position':'Printed dimension grid, located from measured column clusters',
                             'label':'Printed label at this grid position' if plan=='NewPlan' else 'Analyst-generated bookkeeping ID; not printed',
                             'size':'Printed shared C1:C30 schedule' if plan=='NewPlan' else 'Not supplied; no assumed column cross-section'},
                         'audit':{'visible_square_component_ids':[v['component_id']for v in near],
                                  'merged_wall_junction':joint,'label_only_grid_inference':label_only}})
    bars=draft['bar_candidates']
    if plan=='NewPlan':
        refs=load(ROOT/'outputs/NewPlan/independent_reference_r3/Reference.json')
        sizes={r['expected']['label']:list(map(int,r['expected']['size_mm'].split('x'))) for r in refs['records']}
        ocr=load(ROOT/'outputs/NewPlan/stage02/Dual_OCR.json')
        for h in ocr['label_hypotheses']:
            if h['label'] in ('T4','T8'):
                assert not h['size_disagreement']
                sizes[h['label']]=h['readings'][0]['size_mm']
        text={}
        for reading in ocr['raw_passes'].values():
            for item in reading['detections']:
                label=locator_label(item['text'])
                if label and (label not in text or item['confidence']>text[label]['confidence']):
                    text[label]=item
        labels=sorted(sizes)
        assert len(labels)==len(bars)==8
        costs=np.full((8,8),1e9)
        for i,label in enumerate(labels):
            points=np.asarray(text[label]['box_px'])
            centre=np.mean(points,axis=0)
            extent=np.ptp(points,axis=0)
            direction='x' if extent[0]>extent[1] else 'y'
            for j,bar in enumerate(bars):
                if bar['direction']==direction:
                    costs[i,j]=float(np.linalg.norm(np.array(bar['centre_px'])-centre))
        rows,cols=linear_sum_assignment(costs)
        pairs=[(labels[i],bars[j],sizes[labels[i]],float(costs[i,j]))for i,j in zip(rows,cols)]
        assignment={'pairs':[{'label':label,'candidate_id':bar['candidate_id'],'cost_px':cost,
                             'text_detection':text[label]}for label,bar,size,cost in pairs]}
        if not (out/'Assignment_Attempt_01.json').exists():
            write(out/'Assignment_Attempt_01.json',assignment)
        write(out/'Assignment_Audit.json',assignment)
        # A long label can be displaced along its wall; require a unique nearest
        # direction-compatible claim rather than an arbitrary centre-distance cap.
        assert all(abs(costs[i,j]-np.min(costs[i]))<1e-8 for i,j in zip(rows,cols))
    else:
        pairs=[(f'NW{i+1:02d}',bar,None,0.)for i,bar in enumerate(bars)]
        assert len(pairs)==4
    for label,bar,size,cost in pairs:
        px,py=bar['centre_px'];cx,cy=metric(px,py)
        raw_centre=[cx,cy]
        direction=bar['direction']
        if plan=='NIST':
            x,y,w,h=bar['bbox_px']
            ends=[metric(x-.5,py),metric(x+w-.5,py)] if direction=='x' else [metric(px,y-.5),metric(px,y+h-.5)]
            length=float(np.linalg.norm(np.array(ends[1])-ends[0]))
            thickness=cfg['assumed_wall_thickness_mm']/1000
            if direction=='x':
                cy=thickness/2 if cy<cfg['grid_height_m']/2 else cfg['grid_height_m']-thickness/2
            else:
                cx=thickness/2 if cx<cfg['grid_width_m']/2 else cfg['grid_width_m']-thickness/2
            size=[length*1000,thickness*1000]
        else:
            length=max(size)/1000;thickness=min(size)/1000
        elements.append({'id':len(elements)+1,'labels':[label],'class':'wall','centre_m':[cx,cy],
                         'size_mm':size,'angle_deg':0. if direction=='x' else 90.,'continuous':True,
                         'length_m':length,'thickness_m':thickness,
                         'provenance':{'position':'Calibrated directional-bar box centre; NIST normal coordinate inset to put assumed outer face on floor border' if plan=='NIST' else 'Piecewise dimension-grid transform of directional-bar box centre',
                                       'size':'Printed labelled dimensions; six checked flags plus existing dual OCR T4/T8' if plan=='NewPlan' else 'Length from schematic endpoints; thickness is course default 250 mm',
                                       'label':'Printed element label' if plan=='NewPlan' else 'Analyst-generated; not printed'},
                         'audit':{'candidate_id':bar['candidate_id'],'measured_bbox_px':bar['bbox_px'],
                                  'measured_centre_px':[px,py],'unadjusted_metric_centre_m':raw_centre,
                                  'label_match_cost_px':cost,'endpoint_uncertainty_m':2/min(draft['initial_px_per_m'].values())}})
    floor=box(*cfg['floor_bounds_m'])
    diagnostics=[]
    for element in elements:
        cx,cy=element['centre_m']
        if element['class']=='wall':
            L,t=element['length_m'],element['thickness_m']
            w,h=(L,t)if element['angle_deg']==0 else(t,L)
            axis=LineString([(cx-L/2,cy),(cx+L/2,cy)])if element['angle_deg']==0 else LineString([(cx,cy-L/2),(cx,cy+L/2)])
            element['axis_endpoints_m']=[list(c)for c in axis.coords]
            footprint=box(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
            # Independent source ink support of the adopted labelled axis.
            samples=[pixel(*axis.interpolate(s,normalized=True).coords[0])for s in np.linspace(0,1,101)]
            grey=cv2.imread(str(ROOT/cfg['source']),0)
            support=[]
            for x,y in samples:
                a,b=int(round(x)),int(round(y))
                patch=grey[max(0,b-2):b+3,max(0,a-2):a+3]
                support.append(bool(patch.size and np.any(patch<100)))
            element['audit']['sampled_axis_ink_support']=float(np.mean(support))
        else:
            axis=Point(cx,cy)
            size=element['size_mm']
            footprint=None if size is None else box(cx-size[0]/2000,cy-size[1]/2000,cx+size[0]/2000,cy+size[1]/2000)
        assert floor.buffer(1e-8).covers(axis),element['labels']
        diagnostics.append({'label':element['labels'][0],'axis_inside_floor':True,
                            'footprint_outside_floor_m2':None if footprint is None else footprint.difference(floor).area})
    calibration={'grid_px':{'x':gx,'y':gy},'grid_m':{'x':mx,'y':my},
                 'global_affine_px_per_m':{'x':float(xf[0]),'y':float(-yf[0])},
                 'global_affine_intercepts_px':{'x':float(xf[1]),'y':float(yf[1])},
                 'global_fit_residual_m':{'x':((np.array(gx)-np.polyval(xf,mx))/xf[0]).tolist(),
                                          'y':((np.array(gy)-np.polyval(yf,my))/abs(yf[0])).tolist()},
                 'adopted':'Monotone piecewise dimension-grid mapping, linear end extrapolation; no clamp/silent wall snapping',
                 'local_px_per_m':{'x':(np.diff(gx)/np.diff(mx)).tolist(),'y':(-np.diff(gy)/np.diff(my)).tolist()}}
    geometry={'plan':plan,'status':'Conditional supplementary engineering baseline; not promoted unchanged-pipeline extraction',
              'source':{'file':cfg['source'],'sha256':draft['source_sha256']},
              'origin':'A4 lower-left column-grid axis centre'if plan=='NewPlan'else'Lower-left printed footprint corner',
              'units':'m; section dimensions mm; positive y upward','calibration':calibration,
              'floor':{'bounds_m':cfg['floor_bounds_m'],'polygon':mapping(floor),'area_m2':floor.area,
                       'edge_interpretation':'Grid expanded by half printed 800 mm column width'if plan=='NewPlan'else'Printed 120 ft square footprint',
                       'openings':[],'openings_note':'None shown; assumed absent for this schematic exercise'},
              'elements':elements,'geometry_diagnostics':diagnostics,
              'unresolved_source_issues':['C17/C20 label-only supports; small footprint-edge mismatch retained']if plan=='NewPlan'else['21 visible square symbols versus 25 gravity columns in report text; unknown column sections; schematic lengths uncertain'],
              'model_promoted':False}
    write(out/'Elements_Conditional.json',geometry)
    write(out/'Calibration.json',calibration)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(13,8)if plan=='NewPlan'else(8,8))
    ax.imshow(cv2.cvtColor(cv2.imread(str(ROOT/cfg['source'])),cv2.COLOR_BGR2RGB))
    for element in elements:
        label=element['labels'][0]
        if element['class']=='wall':
            pts=np.array([pixel(*xy)for xy in element['axis_endpoints_m']])
            ax.plot(pts[:,0],pts[:,1],color='red',lw=1.4)
        cx,cy=pixel(*element['centre_m'])
        ax.plot(cx,cy,'+',color='blue',markersize=5)
        ax.text(cx+8,cy-8,label,color='blue',fontsize=7)
    coords=np.array([pixel(*xy)for xy in floor.exterior.coords])
    ax.plot(coords[:,0],coords[:,1],'--',color='orange',lw=1.2)
    ax.set_title(plan+' | Supplementary measured geometry; assumptions retained')
    ax.axis('off');fig.tight_layout();fig.savefig(out/'Geometry_Source_Overlay.png',dpi=160);plt.close(fig)
    print(plan,'conditional elements',len(elements),'floor area',floor.area,
          'min wall ink support',min(e['audit']['sampled_axis_ink_support']for e in elements if e['class']=='wall'),flush=True)


def recover(plan,p):
    cfg=p[plan]
    source=ROOT/cfg['source']
    out=ROOT/'outputs'/plan/'geometry_recovery_r1'
    out.mkdir(parents=True,exist_ok=True)
    grey=cv2.imread(str(source),0)
    lo,hi=cfg['initial_bottom_left_grid_px'],cfg['initial_top_right_grid_px']
    sx=(hi[0]-lo[0])/cfg['grid_width_m']
    sy=(lo[1]-hi[1])/cfg['grid_height_m']
    k=max(p['minimum_opening_px'],round(p['physical_opening_m']*min(sx,sy)))
    raw=(grey<p['threshold_lt']).astype(np.uint8)*255
    solid=cv2.morphologyEx(raw,cv2.MORPH_OPEN,np.ones((k,k),np.uint8))
    cv2.imwrite(str(out/'Solid_Threshold.png'),raw)
    cv2.imwrite(str(out/'Solid_Opening.png'),solid)
    all_components=components(solid)
    columns=[c for c in all_components if c['fill_fraction']>=p['column_fill_min']
             and c['aspect_ratio']<=p['column_aspect_max']
             and min(c['bbox_px'][2:])>=.35*min(sx,sy)
             and max(c['bbox_px'][2:])<=1.5*max(sx,sy)]
    gx=cluster([c['centre_px'][0] for c in columns],p['coordinate_cluster_tolerance_m']*sx)
    gy=cluster([c['centre_px'][1] for c in columns],p['coordinate_cluster_tolerance_m']*sy)
    bars=[]
    for direction,kernel in [('x',np.ones((1,max(2,round(sx*p['directional_opening_m']))),np.uint8)),
                             ('y',np.ones((max(2,round(sy*p['directional_opening_m'])),1),np.uint8))]:
        mask=cv2.morphologyEx(solid,cv2.MORPH_OPEN,kernel)
        cv2.imwrite(str(out/('Directional_'+direction+'.png')),mask)
        for c in components(mask):
            if c['aspect_ratio']>=p['bar_aspect_min'] and min(c['bbox_px'][2:])>=k:
                bars.append({**c,'direction':direction,'candidate_id':len(bars)+1})
    draft={'plan':plan,'source_sha256':sha(source),'parameters_sha256':sha(ROOT/'params_geometry_recovery_r1.json'),
           'opening_kernel_px':k,'initial_px_per_m':{'x':sx,'y':sy},
           'all_components':all_components,'column_candidates':columns,'bar_candidates':bars,
           'measured_grid_px':{'x':gx,'y':gy},
           'expected_grid_axes':{'x':len(cfg['grid_x_m']),'y':len(cfg['grid_y_m'])},
           'status':'Supplementary measurement only; no geometry promotion'}
    write(out/'Solid_Symbol_Measurements.json',draft)
    print(plan,'solid components',len(all_components),'square candidates',len(columns),
          'bars',len(bars),'grid',len(gx),len(gy),'kernel',k,flush=True)
    return draft


def main():
    params=load(ROOT/'params_geometry_recovery_r1.json')
    for plan in ('NewPlan','NIST'):
        draft=recover(plan,params)
        finalise(plan,params,draft)


if __name__=='__main__':
    main()
