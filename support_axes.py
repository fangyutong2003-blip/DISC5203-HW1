"""Engineering schematic, not a final tributary-area partition.
Positions approximated from Plan 3 and cross-checked against nominal dimensions.
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont
import math

from project_utils import default_font
ROOT=Path(__file__).resolve().parent
REVISED='--revised' in sys.argv
im=Image.new('RGB',(1200,1800),'white'); d=ImageDraw.Draw(im)
f=default_font(21)
s=default_font(17)
def p(x,y): return (170+73*x,1550-73*y)
def line(a,b,color,width=3,dash=False):
    a=p(*a); b=p(*b)
    if not dash: d.line([a,b],fill=color,width=width); return
    length=math.dist(a,b)
    for k in range(0,int(length),15):
        t=k/length; u=min((k+9)/length,1)
        d.line([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),
                (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)],fill=color,width=width)
def label(x,y,t,color='#283743',font=s): d.multiline_text(p(x,y),t,font=font,fill=color,anchor='mm',align='center')
def rect(x,y,w,h,fill): d.rectangle([p(x,y+h),p(x+w,y)],fill=fill,outline='#667580',width=2)
body=[(0,0),(10.2,0),(10.2,12.1),(7.75,12.1),(7.75,19.2),(2.45,19.2),(2.45,15.2),(0,15.2)]
d.polygon([p(*v) for v in body],fill='#f4f7fa',outline='#667580',width=3)
for name,x,y,w,h in [('P10',3.75,19.2,2.65,.5),('P11',0,15.2,2.45,1),('P12',7.75,13.8,.5,4.3),('P13',7.75,12.1,2.45,.9),('P14',1,-1.2,8.2,1.2)]:
    rect(x,y,w,h,'#fff2d7'); label(x+w/2,y+h/2,name)
# Approximate section rectangles in metres; center lines are geometric axes.
walls=[('T1',5.75,18.95,2,.25),('T2',2.45,17.2,.25,2),
       ('T3',1.70,14.95,2,.25),('T4',4.70,11.85,3.05,.25),
       ('T5',5.75,10.35,.25,1.75),('T6',4.70,10.35,2.10,.25),
       ('T7',6.55,7.20,.25,3.4),('T8',4.70,7.20,2.10,.25),
       ('T9',0,0,.25,2),('T10',2.45,0,2,.25),
       ('T11',5.75,0,2,.25),('T12',9.95,0,.25,2)]
for name,x,y,w,h in walls:
    rect(x,y,w,h,'#b8c2cc')
    cx=x+w/2; cy=y+h/2
    if w>h:
        line((x-.15,cy),(x+w+.15,cy),'#1c9254',4,True)
        line((cx,cy-.35),(cx,cy+.35),'#1c9254',3)
        label(cx,cy+.4,name)
    else:
        line((cx,y-.15),(cx,y+h+.15),'#1c9254',4,True)
        line((cx-.35,cy),(cx+.35,cy),'#1c9254',3)
        label(cx+.55,cy,name)
if REVISED:
    # Short returns/end enlargements visible in the source. These are approximate
    # tracings, not additional independently identified structural members.
    returns=[(2.45,18.80,.50,.40),(7.35,18.70,.40,.50),
             (2.45,15.20,.25,.25),(7.50,12.10,.25,.25),
             (0,0,.50,.40),(3.35,0,.50,.50),
             (6.45,0,.40,.50),(9.70,0,.50,.40)]
    for x,y,w,h in returns: rect(x,y,w,h,'#b8c2cc')
    # Restore local geometric axes on the added short returns.
    for a,b in [((2.575,18.80),(2.575,19.30)),((2.40,19.075),(3.05,19.075)),
                ((7.55,18.60),(7.55,19.30)),((2.575,14.90),(2.575,15.55)),
                ((7.625,11.75),(7.625,12.45)),((-.1,.125),(.60,.125)),
                ((3.60,-.10),(3.60,.60)),((6.65,-.10),(6.65,.60)),
                ((9.60,.125),(10.30,.125))]:
        line(a,b,'#1c9254',3,True)
cols=[('C1',7.55,15.90,.4),('C2',.2,15.,.4),('C3',.2,11.9,.4),
      ('C4',3.6,11.9,.4),('C5',10.,11.9,.4),('C6',.2,6.05,.4),
      ('C7',3.6,6.05,.45),('C8',6.6,6.05,.4),('C9',10.,6.05,.4)]
for name,x,y,w in cols:
    rect(x-w/2,y-w/2,w,w,'#b8c2cc')
    line((x-.47,y),(x+.47,y),'#c33535',4)
    line((x,y-.47),(x,y+.47),'#c33535',4)
    label(x,y+.67,name,'#a21c27')
# Construction segments join support centers. Midlines are local demonstrations.
for a,b in [((.2,6.05),(3.6,6.05)),((3.6,6.05),(6.6,6.05)),((6.6,6.05),(10,6.05)),((.2,11.9),(.2,6.05)),((.2,15),(.2,11.9))]:
    line(a,b,'#a9b2bc',2,True)
for x,t in [(1.9,'M1'),(5.1,'M2'),(8.3,'M3')]:
    line((x,4.65),(x,6.95),'#266ed0',4,True)
    label(x,4.35,f'{t}: x={x:.2f}','#266ed0')
for y,t in [(8.975,'M4'),(13.45,'M5')]:
    line((0,y),(1.35,y),'#266ed0',4,True)
    label(1.35,y+.35,f'{t}: y={y:.3f}','#266ed0')
# Visible orthogonal wall junctions; use clear inside corners for local 45° rays.
# Rays are deliberately short: endpoints are not validated partition intersections.
for a,b in [((6.55,10.35),(5.65,9.45)),((6.55,7.45),(5.65,8.35))]:
    line(a,b,'#b34baa',4,True)
    label(b[0],b[1]+.23,'45°','#b34baa')
if REVISED:
    # Corner candidates correspond to the user's sketch. Equal dx/dy enforces
    # 45 degrees. Open circles mean endpoints await other boundary intersections.
    rays=[('K1',(2.95,18.80),(3.75,18.00)),
          ('K2',(7.35,18.70),(6.55,17.90)),
          ('K3',(2.70,15.20),(3.50,16.00)),
          ('K4',(7.50,12.35),(6.70,13.15)),
          ('K5',(.50,.40),(1.40,1.30)),
          ('K6',(3.35,.50),(2.45,1.40)),
          ('K7',(3.85,.50),(4.75,1.40)),
          ('K8',(6.45,.50),(5.55,1.40)),
          ('K9',(6.85,.50),(7.75,1.40)),
          ('K10',(9.70,.40),(8.80,1.30))]
    for name,a,b in rays:
        assert abs(abs(a[0]-b[0])-abs(a[1]-b[1]))<1e-8
        line(a,b,'#b34baa',4,True)
        q=p(*b); d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill='white',outline='#b34baa',width=2)
        label(b[0],b[1]+.22,name,'#b34baa')
    # Retain the user's two crossed areas as questions, not confirmed holes.
    for x0,y0,x1,y1 in [(4.70,10.60,5.75,11.85),(6.,10.60,6.80,11.85)]:
        line((x0,y0),(x1,y1),'#d88a15',2,True)
        line((x0,y1),(x1,y0),'#d88a15',2,True)
        label((x0+x1)/2,(y0+y1)/2,'?','#a86508',f)
label(5.1,20.25,'Plan 3 | Support axes & local bisectors',font=f)
label(5.1,19.92,'PRELIMINARY SCHEMATIC — NOT A CLOSED TRIBUTARY PARTITION')
d.multiline_text((600,1720),'Red crosses: column axes   |   Green: geometric wall axes\nBlue dashed: local midpoint boundaries   |   Purple: conditional 45° corner rays\nCore rays apply ONLY if a slab exists on this side of the walls.\nCoordinates approximate. Wall fixation lines / openings still require validation.\nDashed endpoints do not define final influence areas.',font=s,fill='#283743',anchor='mm',align='center')
if REVISED:
    d.rectangle((20,1660,1180,1795),fill='white')
    d.multiline_text((600,1728),'REVISION: short wall returns restored approximately; K1-K10 added\nRed: column axes | Green: geometric wall axes | Blue: local midpoint segments\nPurple: candidate 45° rays; hollow endpoints are NOT solved intersections\nOrange ?: your possible openings, unconfirmed. Core rays are conditional.\nNot for load calculation yet: fixation lines, return geometry and closure need checking.',font=s,fill='#283743',anchor='mm',align='center')
im.save(ROOT/('FloorPlan3_support_axes_v2.png' if REVISED else 'FloorPlan3_support_axes.png'))
