"""Build a declared post-response reference from source pixels, never reader answers."""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def longest_false(values):
    longest=run=0
    for value in values:
        run=0 if value else run+1
        longest=max(longest,run)
    return longest


def build(plan, source, engine):
    out=ROOT/'outputs'/plan/'independent_reference_r2'
    package=ROOT/'outputs'/plan/'reader_package_v4'
    old=ROOT/'outputs'/plan/'independent_reference_v4/Reference.json'
    flags=load(package/'Flag_Manifest.json')
    assert sha(source)==flags['source_sha256']
    if (out/'Reference_Manifest.json').exists():
        frozen=load(out/'Reference_Manifest.json')
        assert sha(out/'Reference.json')==frozen['reference_sha256']
        assert sha(source)==frozen['source_sha256']
        print(plan,'R2 frozen reference verified; no overwrite',flush=True)
        return
    out.mkdir(parents=True,exist_ok=True)
    image=cv2.imread(str(source))
    records=[]
    for flag in flags['flags']:
        fid=flag['flag_id']
        x0,y0,x1,y1=flag['crop_bbox_px']
        crop=image[y0:y1,x0:x1]
        expected={'label':None,'size_mm':None,'continuous':None}
        record={'flag_id':fid,'expected':expected,'reference_resolved':False,
                'unmarked_source_crop_pixels_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),
                'asked_fields':flag['asked_fields']}
        if 'size_mm' in flag['asked_fields']:
            label=flag['candidate_label_private']
            binary=(cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)>180).astype(np.uint8)*255
            reads=[]
            raw_passes=[]
            for angle in (0,90,180,270):
                rotated=np.rot90(binary,angle//90).copy()
                path=out/f'{fid}_Threshold180_Rotation{angle}.png'
                cv2.imwrite(str(path),rotated)
                result,timing=engine(rotated)
                raw=[]
                for box,text,confidence in result or []:
                    raw.append({'box_px':np.asarray(box).tolist(),'text':text,'confidence':float(confidence)})
                    normalized=text.upper().replace(' ','').replace('\u00d7','X')
                    for match in re.finditer(re.escape(label)+r'(\d{3,4})X(\d{3,4})(?!\d)',normalized):
                        size=[int(match[1]),int(match[2])]
                        if confidence>=.85 and min(size)>0:
                            reads.append({'size_mm':'x'.join(map(str,size)),'rotation_deg':angle,'confidence':float(confidence)})
                raw_passes.append({'rotation_deg':angle,'detections':raw,'elapsed_seconds':list(map(float,timing)),
                                   'input_file':path.name,'input_sha256':sha(path)})
            unique=sorted({r['size_mm'] for r in reads})
            if len(unique)==1:
                expected.update(label=label,size_mm=unique[0])
                record['reference_resolved']=True
            record.update(route='Threshold180 OCR at four fixed rotations; exact queried label',
                          raw_passes=raw_passes,admissible_readings=reads,unique_sizes=unique,
                          reason='One unique high-confidence size' if len(unique)==1 else 'Absent or conflicting high-confidence size; unresolved')
        else:
            a,b,c,d=flag['query_bbox_px']
            trim=min(8,min(c-a,d-b)//4)
            interior=image[b+trim:d-trim,a+trim:c-trim]
            record.update(route='Geometric quarter-thickness trim; multi-threshold raw axial occupancy',
                          queried_bbox_px=[a,b,c,d],trim_px=trim,
                          trimmed_bbox_px=[a+trim,b+trim,c-trim,d-trim],measurements=[])
            if interior.size:
                grey=cv2.cvtColor(interior,cv2.COLOR_BGR2GRAY)
                axis=0 if flag['direction_private']=='x' else 1
                for threshold in (160,180,200):
                    ink=grey<threshold
                    occupancy=np.mean(ink,axis=axis)
                    supported=occupancy>.15
                    record['measurements'].append({'threshold':threshold,
                        'axis_ink_fraction':occupancy.tolist(),'supported_stations':supported.tolist(),
                        'support_fraction':float(np.mean(supported)),
                        'longest_unsupported_run_px':longest_false(supported)})
                if all(m['support_fraction']>=.95 for m in record['measurements']):
                    expected['continuous']=True
                    record['reference_resolved']=True
            record['reason']='Visible continuity robust at all three thresholds' if record['reference_resolved'] else 'Insufficient raw support; unresolved rather than inferred gap'
        records.append(record)
        print(plan,fid,'resolved',record['reference_resolved'],flush=True)
    result={'created_utc':datetime.now(timezone.utc).isoformat(),
            'reference_revision':'R2 post-response audit; V4 unchanged',
            'protocol':'records/Task_08_Reference_R2_Protocol.md',
            'timing_disclosure':'Prepared after receiving Grok answers; not a pre-response blind reference. Program reads source images and private query metadata only, no response files.',
            'independence_limits':'Alternative classical measurement shares OCR engine/query locations. Not independent human/CAD truth; continuity does not establish a section size or global geometry.',
            'plan':plan,'source_file':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source),
            'original_reference_sha256':sha(old),'records':records}
    write(out/'Reference.json',result)
    manifest={'frozen_utc':datetime.now(timezone.utc).isoformat(),
              'reference_sha256':sha(out/'Reference.json'),'source_sha256':sha(source),
              'old_reference_sha256':sha(old),'code_sha256':sha(Path(__file__)),
              'protocol_sha256':sha(ROOT/'records/Task_08_Reference_R2_Protocol.md'),
              'execution_git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),
              'resolved':sum(r['reference_resolved'] for r in records),'total':len(records)}
    write(out/'Reference_Manifest.json',manifest)


def main():
    freeze=load(ROOT/'records/Task_08_Input_Freeze.json')
    engine=RapidOCR()
    for item in freeze['inputs']:
        build(item['plan'],ROOT/item['file'],engine)


if __name__=='__main__':
    main()
