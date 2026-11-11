"""Freeze a human source-reading supplement without rewriting earlier references."""
import copy
import hashlib
import json
import re
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def main():
    out=ROOT/'outputs/NewPlan/independent_reference_r3'
    parent=ROOT/'outputs/NewPlan/independent_reference_r2/Reference.json'
    receipt_path=ROOT/'outputs/NewPlan/human_reference_request/Student_Reading_2026-11-11.json'
    receipt=load(receipt_path)
    assert sha(ROOT/receipt['source_image_file'])==receipt['source_image_sha256']
    match=re.fullmatch(r'(T\d+)\s+(\d+)[Xx](\d+)',receipt['raw_user_text'])
    assert match
    reading={'label':match[1],'size_mm':match[2]+'x'+match[3]}
    assert reading==receipt['normalized_reading']
    if (out/'Reference_Manifest.json').exists():
        manifest=load(out/'Reference_Manifest.json')
        assert sha(out/'Reference.json')==manifest['reference_sha256']
        assert sha(parent)==manifest['parent_reference_sha256']
        assert sha(receipt_path)==manifest['human_receipt_sha256']
        print('Frozen R3 reference and human receipt verified; no overwrite')
        return
    prior=load(parent)
    reference=copy.deepcopy(prior)
    item=next(r for r in reference['records'] if r['flag_id']=='NP-F03')
    assert item['reference_resolved'] is False
    item['previous_R2_expected']=copy.deepcopy(item['expected'])
    item['previous_R2_reference_resolved']=False
    item['expected'].update(reading)
    item['reference_resolved']=True
    item['reason']='Student direct source reading supplements the unresolved OCR identifier; not model consensus.'
    item['human_source_reading']={'receipt':receipt_path.relative_to(ROOT).as_posix(),
                                  'receipt_sha256':sha(receipt_path),'raw_user_text':receipt['raw_user_text'],
                                  'timing':receipt['timing_disclosure'],'confidence':None}
    reference.update(reference_revision='R3 non-blind student source-reading supplement to R2',
                     created_utc=datetime.now(timezone.utc).isoformat(),
                     timing_disclosure='R2 source-only measurements retained; NP-F03 supplemented by the student after both readers. No pre-response blind-reference claim.',
                     parent_reference_sha256=sha(parent))
    out.mkdir(parents=True,exist_ok=True)
    write(out/'Reference.json',reference)
    write(out/'Reference_Manifest.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),
          'reference_sha256':sha(out/'Reference.json'),'parent_reference_sha256':sha(parent),
          'human_receipt_sha256':sha(receipt_path),'code_sha256':sha(Path(__file__)),
          'protocol_sha256':sha(ROOT/'records/Task_08_Human_Reference_R3_Protocol.md'),
          'execution_git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),
          'resolved':sum(r['reference_resolved'] for r in reference['records']),'total':len(reference['records'])})
    assert all(a==b for a,b in zip(prior['records'],reference['records']) if a['flag_id']!='NP-F03')
    print('R3 frozen: six NewPlan reference flags resolved; V4 and R2 unchanged')


if __name__=='__main__':
    main()
