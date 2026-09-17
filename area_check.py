from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
# Metres. Origin: bottom-left external corner of the main building.
# External dimensions govern; slab edge alignment is a provisional assumption.
outline = [(0, 0), (10.2, 0), (10.2, 12.1), (7.75, 12.1),
           (7.75, 19.2), (2.45, 19.2), (2.45, 15.2), (0, 15.2)]
def area(points):
    return abs(sum(x*y2-x2*y for (x,y),(x2,y2) in zip(points, points[1:]+points[:1])))/2

parts = [('Lower body', 10.2, 12.1), ('Middle body', 7.75, 3.1),
         ('Upper body', 5.3, 4.0), ('P10', 2.65, .5), ('P11', 2.45, 1.),
         ('P12', .5, 4.3), ('P13', 2.45, .9), ('P14', 8.2, 1.2)]
body = area(outline)
assert abs(body-sum(w*h for _,w,h in parts[:3])) < 1e-9
balconies = sum(w*h for _,w,h in parts[3:])
result = {'units':'m, m2', 'outline':outline,
          'parts':[{'id':n,'width':w,'height':h,'area':round(w*h,4)} for n,w,h in parts],
          'body_area':round(body,4),'external_slabs_area':round(balconies,4),
          'gross_area_before_openings':round(body+balconies,4),
          'assumptions':['Dimension labels are metres; structural section labels are millimetres.',
                         'Slab boundary follows the dimensioned external building edge.',
                         'P10-P14 are rectangular slab projections; diagonals are panel markers.',
                         'No deduction for unconfirmed central openings.',
                         'P10 horizontal offset is estimated for display only and does not affect area.']}
im = Image.new('RGB', (850, 1450), 'white')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 17)
def pt(x,y): return (90+x*62, 1320-y*62)
def rect(x,y,w,h,color): draw.rectangle([pt(x,y+h),pt(x+w,y)],fill=color,outline='#23364a',width=2)
def label(x,y,text): draw.multiline_text(pt(x,y),text,font=font,fill='#23364a',anchor='mm',align='center')
for x,y,w,h,color,label in [(0,0,10.2,12.1,'#dceafa','A: 10.20 x 12.10'),
                          (0,12.1,7.75,3.1,'#d5eee5','B: 7.75 x 3.10'),
                          (2.45,15.2,5.3,4,'#eee3f7','C: 5.30 x 4.00')]:
    rect(x,y,w,h,color)
    draw.multiline_text(pt(x+w/2,y+h/2),f'{label}\n{w*h:.3f} m²',font=font,fill='#23364a',anchor='mm',align='center')
for name,x,y,w,h in [('P10',3.75,19.2,2.65,.5),('P11',0,15.2,2.45,1),
                      ('P12',7.75,13.8,.5,4.3),('P13',7.75,12.1,2.45,.9),
                      ('P14',1,-1.2,8.2,1.2)]:
    rect(x,y,w,h,'#ffdfa6')
    draw.text(pt(x+w/2,y+h/2),name,font=small,fill='#23364a',anchor='mm')
for i,(x,y) in enumerate(outline):
    draw.text(pt(x,y),f'V{i+1}',font=small,fill='#23364a')
draw.multiline_text((425,38),'Floor Plan 3 | Preliminary gross floor area\n168.645 + 17.970 = 186.615 m²',font=font,fill='#23364a',anchor='mm',align='center')
draw.multiline_text((425,1420),'Dimensions in metres. Openings not deducted.\nP10 horizontal offset approximate; area uses labelled dimensions.',font=small,fill='#23364a',anchor='mm',align='center')
im.save(ROOT/'FloorPlan3_area.png')
print(json.dumps(result,ensure_ascii=False,indent=2))
