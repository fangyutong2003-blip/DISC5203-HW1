from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from project_utils import default_font

ROOT = Path(__file__).resolve().parent
im = Image.new('RGB', (1050, 1480), 'white')
d = ImageDraw.Draw(im)
font = default_font(20)
small = default_font(16)
def p(x,y): return (140+x*64, 1320-y*64)
def box(x0,y0,x1,y1,fill,outline='#405366',width=2):
    d.rectangle([p(x0,y1),p(x1,y0)],fill=fill,outline=outline,width=width)
def text(x,y,s,color='#23364a',size=font):
    d.multiline_text(p(x,y),s,font=size,fill=color,anchor='mm',align='center')
for x in range(11): d.line([p(x,-1.3),p(x,20)], fill='#e6eaf0')
for y in range(-1,21): d.line([p(-.3,y),p(10.5,y)], fill='#e6eaf0')
box(0,15.2,2.45,19.2,'#fae0e0')
box(7.75,12.1,10.2,19.2,'#fae0e0')
body=[(0,0),(10.2,0),(10.2,12.1),(7.75,12.1),(7.75,19.2),(2.45,19.2),(2.45,15.2),(0,15.2)]
d.polygon([p(*v) for v in body],fill='#e3edf8',outline='#23364a',width=3)
for name,x,y,w,h in [('P10*',3.75,19.2,2.65,.5),('P11',0,15.2,2.45,1),('P12',7.75,13.8,.5,4.3),('P13',7.75,12.1,2.45,.9),('P14',1,-1.2,8.2,1.2)]:
    box(x,y,x+w,y+h,'#ffe1a3')
    text(x+w/2,y+h/2,name,size=small)
text(1.2,17.8,'R1\nExterior recess')
text(9.1,17.8,'R2\nExterior recess')
# Raster-derived locations only, not verified opening boundaries.
box(4.70,10.62,5.74,11.86,'#edcdf1','#854290',3)
text(5.22,11.25,'H1?',size=small)
box(4.70,7.52,6.52,10.36,'#edcdf1','#854290',3)
text(5.61,8.94,'H2?\nUnconfirmed',size=small)
for i,(x,y) in enumerate(body,1):
    q=p(x,y)
    d.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill='#23364a')
    d.text((q[0]+5,q[1]+5),f'V{i} ({x:g}, {y:g})',font=small,fill='#23364a')
d.line([p(0,0),p(11.8,0)],fill='#173b66',width=3)
d.line([p(0,0),p(0,20.2)],fill='#173b66',width=3)
for x,y in [(11.8,0),(0,20.2)]:
    q=p(x,y)
    vertices=[q,(q[0]-12,q[1]-6),(q[0]-12,q[1]+6)] if x else [q,(q[0]-6,q[1]+12),(q[0]+6,q[1]+12)]
    d.polygon(vertices,fill='#173b66')
text(11.6,.4,'x (m)')
text(-.8,20,'y (m)')
text(5.1,20.45,'Floor Plan 3 | Coordinates & opening review')
d.multiline_text((525,1430),'Blue: main footprint | Yellow: external slab | Red: exterior recess\nPurple: candidate opening, NOT confirmed; position estimated from image\n*P10 horizontal offset estimated. Origin excludes the lower projection.',font=small,fill='#23364a',anchor='mm',align='center')
im.save(ROOT/'FloorPlan3_coordinates.png')
# Inspection-only crop, preserving the original image.
source = Image.open(ROOT/'FloorPlan3.png')
source.crop((950,1320,1430,2260)).save(ROOT/'FloorPlan3_core_detail.png')
