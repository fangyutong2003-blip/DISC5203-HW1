"""Generate the reviewed Step 01 geometry and tributary-area deliverables.

The validated default is a rectilinear L1 partition with O1/O2 and S1 excluded.
An explicit Euclidean option is retained only as a non-submission diagnostic.
"""
from pathlib import Path
import argparse
import csv
import json, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from project_utils import default_font

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description="Generate the validated HW1 tributary-area model and Step 01 CSV files.")
parser.add_argument("--straight",action="store_true",help="Deprecated compatibility flag; the validated rectilinear method is now the default.")
parser.add_argument("--euclidean-diagnostic",action="store_true",help="Generate the non-submission Euclidean diagnostic only; do not write validated Step 01 CSV files.")
args=parser.parse_args()
if args.straight and args.euclidean_diagnostic:
    parser.error("--straight and --euclidean-diagnostic cannot be used together")
STRAIGHT=not args.euclidean_diagnostic
names=[f'C{i}' for i in range(1,10)]+[f'T{i}' for i in range(1,13)]
columns=[(7.55,15.90,.4),(.2,15.,.4),(.2,11.9,.4),(3.6,11.9,.4),
         (10.,11.9,.4),(.2,6.05,.4),(3.6,6.05,.45),(6.6,6.05,.4),(10.,6.05,.4)]
walls=[(5.75,18.95,2,.25),(2.45,17.2,.25,2),(1.70,14.95,2,.25),
       (4.70,11.85,3.05,.25),(5.75,10.35,.25,1.75),(4.70,10.35,2.10,.25),
       (6.55,7.20,.25,3.4),(4.70,7.20,2.10,.25),(0,0,.25,2),
       (2.45,0,2,.25),(5.75,0,2,.25),(9.95,0,.25,2)]
# Added short returns/end enlargements are approximate image-derived geometry.
returns={0:[(7.35,18.70,.40,.50)],1:[(2.45,18.80,.50,.40)],
         2:[(2.45,15.20,.25,.25)],3:[(7.50,12.10,.25,.25)],
         8:[(0,0,.50,.40)],9:[(3.35,0,.50,.50)],
         10:[(6.45,0,.40,.50)],11:[(9.70,0,.50,.40)]}
segments=[]
for i,(x,y,w) in enumerate(columns): segments.append((i,x,y,x,y))
for i,(x,y,w,h) in enumerate(walls):
    if w>h: segments.append((9+i,x,y+h/2,x+w,y+h/2))
    else: segments.append((9+i,x+w/2,y,x+w/2,y+h))
extra=[(0,7.55,18.70,7.55,19.075),(1,2.575,19.075,2.95,19.075),
       (2,2.575,15.075,2.575,15.45),(3,7.625,11.975,7.625,12.35),
       (8,.125,.125,.5,.125),(9,3.60,.125,3.60,.50),
       (10,6.65,.125,6.65,.50),(11,9.70,.125,10.075,.125)]
segments.extend((9+i,x,y,u,v) for i,x,y,u,v in extra)
slabs=[(0,0,10.2,12.1),(0,12.1,7.75,3.1),(2.45,15.2,5.3,4.),
       (3.75,19.2,2.65,.5),(0,15.2,2.45,1.),(7.75,13.8,.5,4.3),
       (7.75,12.1,2.45,.9),(1,-1.2,8.2,1.2)]
# Areas excluded from the ordinary 150 mm flat-slab allocation.
# O1/O2 are shaft voids. S1 is the stair/core enclosure bounded by T6-T8;
# its load must be represented separately rather than as ordinary flat slab.
openings=[('O1',4.70,10.60,1.05,1.25),('O2',6.00,10.60,.55,1.25),
          ('S1',4.70,7.45,1.85,2.90)]
excluded_area=sum(w*h for _,x,y,w,h in openings)
def partition(step):
    xs=(np.arange(round(10.2/step))+.5)*step
    ys=-1.2+(np.arange(round(20.9/step))+.5)*step
    X=xs[None,:]; Y=ys[:,None]
    mask=np.zeros((len(ys),len(xs)),bool)
    for x,y,w,h in slabs: mask|=(X>=x)&(X<x+w)&(Y>=y)&(Y<y+h)
    if STRAIGHT:
        for name,x,y,w,h in openings: mask&=~((X>=x)&(X<x+w)&(Y>=y)&(Y<y+h))
    best=np.full(mask.shape,np.inf); owner=np.full(mask.shape,-1,np.int16)
    for i,x,y,u,v in segments:
        dx=abs(X-np.clip(X,min(x,u),max(x,u)))
        dy=abs(Y-np.clip(Y,min(y,v),max(y,v)))
        dist=dx+dy if STRAIGHT else dx**2+dy**2
        win=dist<best
        owner[win]=i; best[win]=dist[win]
    owner[~mask]=-1
    totals=np.bincount(owner[mask],minlength=21)*step**2
    assert abs(totals.sum()-mask.sum()*step**2)<1e-7
    assert (owner[mask]>=0).all()
    return owner,mask,totals

coarse,_,a0=partition(.02)
owner,mask,areas=partition(.01)
target=186.615-(excluded_area if STRAIGHT else 0)
assert abs(areas.sum()-target)<.06
palette=[]
for i in range(21):
    c=colorsys.hsv_to_rgb((i*.61803398875)%1,.29,.97)
    palette.append(tuple(round(v*255) for v in c))
rgb=np.full((*owner.shape,3),255,np.uint8)
for i,c in enumerate(palette): rgb[owner==i]=c
boundary=np.zeros(owner.shape,bool)
boundary[:,1:] |= (owner[:,1:]!=owner[:,:-1]) & mask[:,1:]
boundary[1:,:] |= (owner[1:,:]!=owner[:-1,:]) & mask[1:,:]
rgb[boundary]=[60,70,83]
region=Image.fromarray(rgb[::-1]).resize((816,1672),Image.Resampling.LANCZOS)
im=Image.new('RGB',(1380,1940),'white'); im.paste(region,(90,130))
d=ImageDraw.Draw(im)
font=default_font(22)
small=default_font(18)
tiny=default_font(15)
def p(x,y):return (90+x*80,130+(19.7-y)*80)
def txt(x,y,text,fill='#172c43',f=small):
    d.text(p(x,y),text,font=f,fill=fill,anchor='mm',stroke_width=2,stroke_fill='white')
def shape(x,y,w,h):
    a=p(x,y+h);b=p(x+w,y)
    d.rectangle([a,b],fill='#4a5059',outline='#161c24',width=2)
    # Fine hatch fully clipped to this structural rectangle.
    for yy in range(int(a[1])+4,int(b[1]),7):
        d.line([(a[0]+1,yy),(b[0]-1,yy)],fill='#c0c7ce',width=1)
for x,y,w in columns: shape(x-w/2,y-w/2,w,w)
for i,(x,y,w,h) in enumerate(walls):
    shape(x,y,w,h)
    for rect in returns.get(i,[]): shape(*rect)
# Axes represented directly by the same segment data used for allocation.
for i,x,y,u,v in segments:
    if i<9:
        d.line([p(x-.3,y),p(x+.3,y)],fill='#bd2538',width=2)
        d.line([p(x,y-.3),p(x,y+.3)],fill='#bd2538',width=2)
    else:
        a=p(x,y);b=p(u,v);length=max(1,int(np.hypot(b[0]-a[0],b[1]-a[1])))
        for k in range(0,length,12):
            t=k/length;z=min((k+7)/length,1)
            d.line([(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])),
                    (a[0]+z*(b[0]-a[0]),a[1]+z*(b[1]-a[1]))],fill='#33d6be',width=2)
for i,(x,y,w) in enumerate(columns): txt(x,y+.52,names[i])
for i,(x,y,w,h) in enumerate(walls):
    if w>h: txt(x+w/2,y-.35 if y>1 else y+.80,names[9+i])
    else: txt(x+.62,y+h/2,names[9+i])
# Owner labels placed within each actual raster region, near its centroid.
for i in range(21):
    rr,cc=np.nonzero(owner==i)
    if not len(rr):continue
    midr=rr.mean();midc=cc.mean()
    k=np.argmin((rr-midr)**2+(cc-midc)**2)
    txt((cc[k]+.5)*.01,-1.2+(rr[k]+.5)*.01,'A('+names[i]+')',f=small)
# Draw openings / unresolved core explicitly.
for name,x,y,w,h in openings:
    a=p(x,y+h);b=p(x+w,y)
    d.rectangle([a,b],fill='white',outline='#c97b0d',width=3)
    if name!='S1':
        d.line([a,b],fill='#c97b0d',width=2)
        d.line([(a[0],b[1]),(b[0],a[1])],fill='#c97b0d',width=2)
txt(5.23,11.22,'VOID O1',f=tiny)
txt(6.28,11.22,'O2',f=tiny)
txt(5.63,8.90,'STAIR / CORE\nSEPARATE LOAD',f=tiny)
d.text((90,30),'Plan 3 | Closed Tributary-Area Regions',font=font,fill='#172c43')
d.text((90,70),('Rectilinear L1 allocation: horizontal, vertical and 45-degree boundaries' if STRAIGHT else 'Preliminary nearest-support geometric allocation'),font=small,fill='#526174')
d.text((950,160),'Region owner',font=font,fill='#172c43')
for i,n in enumerate(names):
    yy=215+i*47
    d.rectangle((950,yy,980,yy+25),fill=palette[i],outline='#768391')
    d.text((995,yy-2),n,font=small,fill='#172c43')
d.multiline_text((950,1255),'Dark hatch: wall / column\nCyan: wall geometric axis\nRed cross: column axis\nThin dark line: region boundary\nOrange: void / unresolved area',font=small,fill='#172c43',spacing=12)
d.multiline_text((950,1480),('ASSUMPTIONS\nO1/O2 deducted as voids\nS1 stair/core excluded from flat slab\nand requires a separate load model\nP10-P14 projections included\nColumn/wall footprints not deducted\nShort wall returns reconstructed\napproximately\n\nReturns with the same ID are grouped' if STRAIGHT else 'ASSUMPTIONS\nCentral special regions excluded\nP10-P14 projections included\nColumn/wall footprints not deducted\nShort wall returns approximate'),font=tiny,fill='#526174',spacing=9)
d.multiline_text((90,1840),'The coloured regions are closed, non-overlapping, and cover the assumed effective slab.\nThis is a reproducible geometric allocation, not a validated structural load-path model.\nRevise the wall fixation lines and voids if better source information becomes available.',font=small,fill='#526174',spacing=8)
im.save(ROOT/('FloorPlan3_tributary_regions_straight.png' if STRAIGHT else 'FloorPlan3_tributary_regions.png'))

# Separate line-only diagram in the style of the assignment example.
if STRAIGHT:
    R,C=owner.shape
    line_rgb=np.full((R,C,3),255,np.uint8)
    line_rgb[mask]=[248,248,246]
    rr=np.arange(R)[:,None]; cc=np.arange(C)[None,:]
    dash=((rr+cc)//18)%2==0
    line_rgb[boundary & dash]=[75,75,75]
    edge=np.zeros_like(mask)
    edge[:,1:] |= mask[:,1:] & ~mask[:,:-1]
    edge[:,:-1] |= mask[:,:-1] & ~mask[:,1:]
    edge[1:,:] |= mask[1:,:] & ~mask[:-1,:]
    edge[:-1,:] |= mask[:-1,:] & ~mask[1:,:]
    line_rgb[edge]=[35,35,35]
    base=Image.fromarray(line_rgb[::-1]).resize((816,1672),Image.Resampling.NEAREST)
    lm=Image.new('RGB',(1320,1900),'white'); lm.paste(base,(90,125))
    ld=ImageDraw.Draw(lm)
    def lp(x,y):return (90+x*80,125+(19.7-y)*80)
    def lshape(x,y,w,h):
        a=lp(x,y+h);b=lp(x+w,y)
        ld.rectangle([a,b],fill='#d6d6d6',outline='#222222',width=2)
        for off in range(-80,220,9):
            x0=max(a[0],a[0]+off); y0=max(a[1],b[1]-off)
            x1=min(b[0],a[0]+off+(b[1]-a[1])); y1=min(b[1],a[1]+off+(b[0]-a[0]))
            if x0<=x1 and y0<=y1: ld.line((x0,y0,x1,y1),fill='#777777',width=1)
    for x,y,w in columns:lshape(x-w/2,y-w/2,w,w)
    for i,(x,y,w,h) in enumerate(walls):
        lshape(x,y,w,h)
        for q in returns.get(i,[]):lshape(*q)
    for i,x,y,u,v in segments:
        a=lp(x,y);b=lp(u,v)
        if i<9:
            ld.line([lp(x-.27,y),lp(x+.27,y)],fill='#111111',width=3)
            ld.line([lp(x,y-.27),lp(x,y+.27)],fill='#111111',width=3)
        else:
            ld.line([a,b],fill='#111111',width=2)
    for i,(x,y,w) in enumerate(columns):
        ld.text(lp(x,y+.48),names[i],font=tiny,fill='#111111',anchor='mm',stroke_width=2,stroke_fill='white')
    for i,(x,y,w,h) in enumerate(walls):
        pos=(x+w/2,y-.30 if w>h else y+h/2)
        ld.text(lp(*pos),names[9+i],font=tiny,fill='#111111',anchor='mm',stroke_width=2,stroke_fill='white')
    for name,x,y,w,h in openings:
        a=lp(x,y+h);b=lp(x+w,y)
        ld.rectangle([a,b],fill='white',outline='#111111',width=2)
        if name!='S1':
            ld.line([a,b],fill='#111111',width=2);ld.line([(a[0],b[1]),(b[0],a[1])],fill='#111111',width=2)
        ld.text(((a[0]+b[0])//2,(a[1]+b[1])//2),('STAIR / CORE' if name=='S1' else name),font=tiny,fill='#111111',anchor='mm')
    ld.text((90,30),'Plan 3 | Support Axes and Tributary Boundaries',font=font,fill='#172c43')
    ld.text((90,70),'Dashed lines are closed midpoint / 45-degree boundaries; solid black lines are support axes.',font=small,fill='#526174')
    ld.multiline_text((945,180),'LEGEND\n\nHatched: wall / column\nSolid line: support axis\nDashed line: tributary boundary\nCrossed white area: void\n\nAll dashed boundaries close\nat another boundary, slab edge,\nor void edge.\n\nGeometry matches the area\ncalculation figure.',font=small,fill='#172c43',spacing=10)
    ld.multiline_text((90,1835),'Assumptions: O1/O2 are voids; S1 is stair/core with a separate load model; wall returns and P10 location are approximate.',font=tiny,fill='#526174')
    lm.save(ROOT/'FloorPlan3_tributary_boundaries.png')
payload={'method':('L1 distance to column centers and grouped finite wall-axis segments' if STRAIGHT else 'Euclidean distance to column centers and grouped finite wall-axis segments'),
         'status':'closed geometric partition; assumptions require instructor/user validation',
         'grid_m':.01,'gross_area_exact_m2':186.615,
         'excluded_from_flat_slab_m2':(excluded_area if STRAIGHT else 0),
         'effective_area_m2':target,'raster_area_m2':float(areas.sum()),
         'max_element_area_change_2cm_to_1cm_m2':float(abs(areas-a0).max()),
         'areas_m2':{n:round(float(a),4) for n,a in zip(names,areas)},
         'assumptions':[('O1/O2 deducted as voids; S1 stair/core excluded from ordinary flat slab and requires a separate load model.' if STRAIGHT else 'Unconfirmed central patches treated as slab for this drawing.'),
                        'Columns/walls footprints included in gross allocated area.',
                        'Approximate wall returns, support locations and P10 horizontal offset.',
                        'No stiffness, beam load routing or line-of-sight constraint.',
                        'Wall geometry centerlines not verified fixation lines from instructor example.']}

if STRAIGHT:
    coordinate_fields=["element_id","element_type","axis_segment","x1_m","y1_m","x2_m","y2_m","section_mm","status","notes"]
    coordinate_rows=[]
    column_sections=["400x400","400x400","400x400","400x400","400x400","400x400","450x450","400x400","400x400"]
    for i,(x,y,w) in enumerate(columns):
        coordinate_rows.append({"element_id":f"C{i+1}","element_type":"column","axis_segment":"centre","x1_m":x,"y1_m":y,"x2_m":x,"y2_m":y,"section_mm":column_sections[i],"status":"image-derived","notes":"Point support at section centre"})
    wall_sections=["2000x250","250x2000","2000x250","3050x250","250x1750","2100x250","250x3400","2100x250","250x2000","2000x250","2000x250","250x2000"]
    # The first 9 entries are columns and the next 12 are main wall axes.
    # Later entries reuse wall IDs for short returns and must not overwrite them.
    main_segments={i-9:(x,y,u,v) for i,x,y,u,v in segments[9:21]}
    return_segments={i:(x,y,u,v) for i,x,y,u,v in extra}
    for i in range(12):
        x,y,u,v=main_segments[i]
        coordinate_rows.append({"element_id":f"T{i+1}","element_type":"wall","axis_segment":"main","x1_m":x,"y1_m":y,"x2_m":u,"y2_m":v,"section_mm":wall_sections[i],"status":"image-derived","notes":("Horizontal" if y==v else "Vertical")+" geometric centreline"})
        if i in return_segments:
            x,y,u,v=return_segments[i]
            coordinate_rows.append({"element_id":f"T{i+1}","element_type":"wall","axis_segment":"return","x1_m":x,"y1_m":y,"x2_m":u,"y2_m":v,"section_mm":"approx. return","status":"image-derived","notes":"Short end return reconstructed from image"})
    with (ROOT/"Step_01B_Vertical_Element_Coordinates.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=coordinate_fields,lineterminator="\n")
        writer.writeheader()
        for row in coordinate_rows:
            writer.writerow({key:(f"{value:.3f}" if key in {"x1_m","y1_m","x2_m","y2_m"} else value) for key,value in row.items()})
    with (ROOT/"Step_01C_Tributary_Areas.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(["element_id","tributary_area_m2"])
        for name,area in zip(names,areas):
            writer.writerow([name,f"{area:.4f}"])
    payload["generated_files"]=["Step_01B_Vertical_Element_Coordinates.csv","Step_01C_Tributary_Areas.csv","FloorPlan3_tributary_regions_straight.png","FloorPlan3_tributary_boundaries.png"]
print(json.dumps(payload,ensure_ascii=False,indent=2))
