"""Retain new-plan uncertainties and freeze identical reader inputs, without promotion."""
import hashlib
import argparse
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locator_label(text):
    """Resolve query-location ambiguity without accepting a geometry or reader answer."""
    text = text.upper().replace(' ', '').replace('\u00d7', 'X')
    match = re.fullmatch(r'T(\d+)X(\d{3,4})', text)
    if not match:
        return None
    possibilities = []
    for cut in (1, 2):
        left = match[1][cut:]
        if len(left) not in (3, 4):
            continue
        a,b = int(left),int(match[2])
        if min(a,b) >= 100 and max(a,b) / min(a,b) >= 3:
            possibilities.append('T'+match[1][:cut])
    return possibilities[0] if len(possibilities) == 1 else None


def prepare(plan, engine, version):
    output = ROOT / 'outputs' / plan
    package = output / ('reader_package_' + version)
    reference_dir = output / ('independent_reference_' + version)
    if (package / 'Flag_Manifest.json').exists():
        old = json.loads((package / 'Flag_Manifest.json').read_text())
        assert sha(reference_dir / 'Reference.json') == old['reference_sha256']
        assert sha(ROOT / 'prompts/Reader_Instructions.md') == old['common_instruction_sha256']
        for flag in old['flags']:
            assert sha(package / flag['crop']) == flag['sha256']
        print(plan, version, 'frozen reference/crop/instruction hashes verified; no overwrite', flush=True)
        return
    package.mkdir(parents=True, exist_ok=True)
    reference_dir.mkdir(parents=True, exist_ok=True)
    freeze = json.loads((ROOT / 'records/Task_08_Input_Freeze.json').read_text())
    source = ROOT / next(x['file'] for x in freeze['inputs'] if x['plan'] == plan)
    image = cv2.imread(str(source))
    flags = []
    if plan == 'NewPlan':
        ocr = json.loads((output / 'stage02/Dual_OCR.json').read_text())
        parsed = {x['label'] for x in ocr['label_hypotheses']}
        for item in ocr['raw_passes']['original']['detections']:
            # This locates unparsed text for review; it does NOT repair the frozen parser.
            text = item['text'].upper().replace(' ', '')
            located_label = locator_label(text)
            schedule = text.startswith('C1:C30=')
            if not schedule and (not located_label or located_label in parsed):
                continue
            label = 'C1:C30' if schedule else located_label
            box = np.array(item['box_px'])
            x0, y0 = np.floor(box.min(axis=0)).astype(int)
            x1, y1 = np.ceil(box.max(axis=0)).astype(int)
            anchor = [max(16, int(x0) - 20), int((y0+y1)/2)]
            flags.append({'candidate_label_private': label,
                          'target_text_bbox_px': [int(x0),int(y0),int(x1),int(y1)],
                          'flag': 'unparsed_shared_size_schedule' if schedule else 'raw_OCR_text_not_parsed',
                          'anchor_px': anchor,
                          'crop_centre_px': [int((x0+x1)/2), int((y0+y1)/2)],
                          'asked_fields': ['label', 'size_mm'],
                          'question': 'What element label (or label range) and size string are printed immediately to the right of the red cross? Answer label and size_mm; keep continuous null.',
                          'source_detection_id': item['detection_id']})
        flags.sort(key=lambda x: x['candidate_label_private'])
    else:
        # Agent-selected query locations, measured on the unannotated source render.
        # These boxes locate questions only and are NOT accepted wall geometry.
        for name, box, direction in [
            ('top', [259, 44, 350, 53], 'x'),
            ('bottom', [255, 498, 348, 507], 'x'),
            ('left', [70, 229, 79, 322], 'y'),
            ('right', [523, 229, 532, 322], 'y'),
        ]:
            x0,y0,x1,y1 = box
            flags.append({'location_private': name, 'query_bbox_px': box,
                          'direction_private': direction,
                          'flag': 'no_classical_component_at_visible_wall_location',
                          'anchor_px': [int((x0+x1)/2), int((y0+y1)/2)],
                          'crop_centre_px': [int((x0+x1)/2), int((y0+y1)/2)],
                          'asked_fields': ['continuous'],
                          'question': 'Is the concrete wall through the red cross continuous along its axis, or is there a genuine gap? Answer continuous only; keep label and size_mm null.'})
    references = []
    public_flags = []
    rejected_queries = []
    admitted_flags = []
    for flag in flags:
        cx,cy = flag['crop_centre_px']
        x0,y0 = max(0,cx-440),max(0,cy-440)
        x1,y1 = min(image.shape[1],cx+440),min(image.shape[0],cy+440)
        ax,ay = flag['anchor_px']
        box = flag.get('target_text_bbox_px')
        if not (x0 <= ax < x1 and y0 <= ay < y1) or (box and not (x0 <= box[0] and y0 <= box[1] and box[2] <= x1 and box[3] <= y1)):
            rejected_queries.append({**flag,'reason':'Fixed 880 px crop cannot contain target and cross; no resized workaround or reader score'})
        else:
            admitted_flags.append(flag)
    flags = admitted_flags
    for index, flag in enumerate(flags, 1):
        flag_id = f'{"NP" if plan == "NewPlan" else "NI"}-F{index:02d}'
        cx,cy = flag['crop_centre_px']
        half = 440
        x0,y0 = max(0,cx-half),max(0,cy-half)
        x1,y1 = min(image.shape[1],cx+half),min(image.shape[0],cy+half)
        original = image[y0:y1,x0:x1].copy()
        binary = (cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)>180).astype(np.uint8)*255
        ref_input = reference_dir / (flag_id + '_Reference_Input.png')
        cv2.imwrite(str(ref_input), binary)
        expected = {'label': None, 'size_mm': None, 'continuous': None}
        ref = {'flag_id': flag_id, 'expected': expected, 'reference_resolved': False,
               'source_unmarked_crop_sha256': hashlib.sha256(original.tobytes()).hexdigest(),
               'threshold': 180, 'independent_ocr': [], 'raw_ink_axial_support': None}
        if 'size_mm' in flag['asked_fields']:
            result,_ = engine(binary)
            raw = [{'box_px':np.asarray(box).tolist(), 'text':text, 'confidence':float(conf)}
                   for box,text,conf in (result or [])]
            ref['independent_ocr'] = raw
            label = flag['candidate_label_private']
            readings = []
            for item in raw:
                normalized = item['text'].upper().replace(' ','').replace('\u00d7','X')
                pattern = re.escape(label) + ('=?' if ':' in label else '') + r'(\d{3,4})(?:MM)?X(\d{3,4})(?:MM)?'
                match = re.search(pattern, normalized)
                if match and item['confidence'] >= .85:
                    readings.append(match[1]+'x'+match[2])
            values = sorted(set(readings))
            if len(values) == 1:
                expected.update(label=label, size_mm=values[0])
                ref['reference_resolved'] = True
            ref['reason'] = 'Unique high-confidence independent OCR reading' if len(values)==1 else 'No unique high-confidence reference; do not score or promote'
        else:
            a,b,c,d = flag['query_bbox_px']
            trim = 8
            interior = image[b+trim:d-trim,a+trim:c-trim]
            ref['interior_trim_px'] = trim
            if interior.size:
                ink = cv2.cvtColor(interior,cv2.COLOR_BGR2GRAY)<180
                along = np.mean(ink,axis=0 if flag['direction_private']=='x' else 1)
                support = float(np.mean(along>.15))
                ref['raw_ink_axial_support'] = support
                if support >= .95:
                    expected['continuous'] = True
                    ref['reference_resolved'] = True
                ref['reason'] = 'Fixed raw-ink axial occupancy reference'
            else:
                ref['reason'] = 'Fixed 8 px reference trim leaves no interior in the thin schematic symbol; unchanged route unresolved'
        references.append(ref)
        marked = original.copy()
        ax,ay = flag['anchor_px']
        cv2.drawMarker(marked,(ax-x0,ay-y0),(0,0,255),cv2.MARKER_CROSS,30,2)
        filename = flag_id+'.png'
        cv2.imwrite(str(package/filename), marked)
        flag.update(flag_id=flag_id,crop=filename,crop_bbox_px=[x0,y0,x1,y1],sha256=sha(package/filename))
        public_flags.append({k:flag[k] for k in ('flag_id','crop','sha256','question','asked_fields')})
    reference = {'created_utc':datetime.now(timezone.utc).isoformat(),
                 'route':'Same alternative threshold-180 OCR / trim-8 raw-ink occupancy route as Plan 3; no VLM answers.',
                 'independence_limits':'Shares OCR engine and query locations; this is an alternative classical reference, not independent human/CAD ground truth. NewPlan range syntax is parsed only in this reference, never added to main extraction.',
                 'records':references}
    write_json(reference_dir/'Reference.json',reference)
    instruction = ROOT/'prompts/Reader_Instructions.md'
    (package/'Reader_Instructions.md').write_bytes(instruction.read_bytes())
    write_json(package/'Reader_Manifest.json',{'plan':plan,'flags':public_flags})
    private = {'status':'FROZEN reader inputs; reference may be unresolved; no promotion',
               'plan':plan,'source_sha256':sha(source),'frozen_utc':reference['created_utc'],
               'reference_sha256':sha(reference_dir/'Reference.json'),
               'common_instruction_sha256':sha(instruction),'confidence_threshold':.8,
               'model_runs':[],'flags':flags,
               'rejected_queries':rejected_queries,
               'note':'Evaluator metadata only. Send Reader_Manifest.json, Questions.md, instructions and PNGs to readers; exclude this private manifest and reference.'}
    write_json(package/'Flag_Manifest.json',private)
    lines=['# Frozen image-reader questions','',
           'Use Reader_Instructions.md unchanged for both models. Submit one image and its question in the order below. Do not send evaluator metadata or reference answers.','']
    for flag in public_flags:
        lines += ['## '+flag['flag_id'],'',flag['question'],'',f"![{flag['flag_id']}]({flag['crop']})",'']
    (package/'Questions.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    zip_path = ROOT / f'HW3_Task_08_{plan}_Reader_Package_{version.upper()}.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in ['Reader_Instructions.md','Reader_Manifest.json','Questions.md']+[f['crop'] for f in public_flags]:
            archive.write(package/name,arcname=name)
    print(plan, len(flags), 'frozen flags;',sum(r['reference_resolved'] for r in references),'reference-resolved; reader runs pending',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', choices=['v3'], default='v3')
    args = parser.parse_args()
    engine = RapidOCR()
    for plan in ('NewPlan','NIST'):
        prepare(plan, engine, args.revision)


if __name__ == '__main__':
    main()
