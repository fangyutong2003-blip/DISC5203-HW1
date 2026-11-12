"""Ingest the actual paused-run Plan 3 reader and score retained data without rerunning a model."""
import argparse
import base64
import copy
import hashlib
import io
import json
from pathlib import Path

from PIL import Image
from task08_compare_readers import score,local_gate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/Plan3/reader_A_isolated_final'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def ingest(path):
    package=ROOT/'outputs/Plan3/reader_package_v1'
    manifest=load(package/'Flag_Manifest.json');inputs=[];answers=[];contexts=[];tools=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        entry=json.loads(line);p=entry.get('payload',{})
        if entry.get('type')=='turn_context':
            contexts.append({k:p[k]for k in ('model','effort','turn_id')if k in p})
        if entry.get('type')=='response_item' and p.get('type') in ('function_call','custom_tool_call'):
            tools.append(p.get('name'))
        if entry.get('type')=='response_item' and p.get('type')=='message':
            if p.get('role')=='user':
                texts=[c.get('text','')for c in p.get('content',[])if c.get('type')=='input_text']
                if any('Flag ID:'in text for text in texts):
                    image=next(c for c in p['content']if c['type']=='input_image')
                    url=image.get('image_url','')
                    assert url.startswith('data:')
                    data=base64.b64decode(url.split(',',1)[1]);decoded=Image.open(io.BytesIO(data)).convert('RGB')
                    index=len(inputs);flag=manifest['flags'][index]
                    source=Image.open(package/flag['crop']).convert('RGB')
                    assert decoded.size==source.size and decoded.tobytes()==source.tobytes()
                    assert sha(package/flag['crop'])==flag['sha256']
                    assert 'Flag ID: '+flag['flag_id']+'\n\n'+flag['question'] in texts
                    inputs.append({'flag_id':flag['flag_id'],'actual_text_items':texts,
                                   'crop_file':flag['crop'],'source_image_sha256':flag['sha256'],
                                   'serialized_image_sha256':hashlib.sha256(data).hexdigest(),
                                   'decoded_pixels_identical_to_frozen_crop':True})
            elif p.get('role')=='assistant' and (p.get('phase')=='final_answer' or p.get('channel')=='final'):
                raw='\n'.join(c.get('text','')for c in p.get('content',[])if c.get('type')=='output_text')
                answers.append({'timestamp_utc':entry.get('timestamp'),'raw_response':raw})
    assert len(inputs)==len(answers)==len(contexts)==5 and not tools
    assert inputs[0]['actual_text_items'][0]==(package/'Reader_Instructions.md').read_text()
    parsed=[]
    for flag,response in zip(manifest['flags'],answers):
        text=response['raw_response'];start=text.index('{');obj,end=json.JSONDecoder().raw_decode(text[start:])
        assert obj['flag_id']==flag['flag_id'] and not text[start+end:].strip()
        parsed.append(obj)
    OUT.mkdir(parents=True,exist_ok=True)
    write(OUT/'Raw_Transcript.json',{'actual_model_run_date':'2026-11-11','evidence_ingested_date':'2026-11-12',
        'agent_id':'01a1cabc-a3a8-70a1-b701-57b09240c064','fork_context':False,
        'run_note':'Run completed before the student paused; genuine final answers recovered from its local runtime log. No inference was rerun or backdated.',
        'inputs':inputs,'outputs':answers})
    write(OUT/'Raw_Answers.json',parsed)
    write(OUT/'Runtime_Metadata.json',{'runtime_log_file':path.name,'runtime_log_sha256_at_capture':sha(path),
        'turn_context_model_evidence':contexts,'runtime_model_ids':sorted({c['model']for c in contexts}),
        'reader_tool_calls':tools,'extracted_metadata_scope':'Only public final answers, supplied user prompts/images and model/turn metadata; no private reasoning exported.',
        'harness_limit':'Isolated native interface differs from student-operated Grok web; shared inputs do not establish an identical harness.',
        'actual_run_date':'2026-11-11','ingestion_date':'2026-11-12'})


def signature(geometry):
    keys=('id','labels','class','centre_m','size_mm','angle_deg','continuous')
    return [{k:e.get(k)for k in keys}for e in geometry['elements']]


def evaluate():
    package=ROOT/'outputs/Plan3/reader_package_v1';manifest=load(package/'Flag_Manifest.json')
    ref=ROOT/'outputs/Plan3/independent_reference/Reference.json'
    assert sha(ref)==manifest['reference_sha256']
    reference=load(ref);a=load(OUT/'Raw_Answers.json');b=load(ROOT/'outputs/Plan3/reader_B_grok/Raw_Answers.json')
    sa,sb=score(manifest['flags'],a,reference),score(manifest['flags'],b,reference)
    original=ROOT/'outputs/Plan3/task1/Elements_Classical.json';base=load(original)
    used=load(ROOT/'outputs/Plan3/task1/Elements_After_Reader_A.json')
    applied={}
    for name,answers,scored in [('Codex_isolated',a,sa),('Grok_student_reported',b,sb)]:
        geom=copy.deepcopy(base)
        for flag,answer,result in zip(manifest['flags'],answers,scored['flags']):
            if result['outcome']!='resolved':continue
            element=next(e for e in geom['elements']if e['labels']==[flag['candidate_label']])
            if 'size_mm'in flag['asked_fields']:element['size_mm']=list(map(int,answer['size_mm'].split('x')))
            if 'continuous'in flag['asked_fields']:element['continuous']=answer['continuous']
            element['audit'].setdefault('reader_resolution',[]).append({'flag_id':answer['flag_id'],
                'source':'corrected by '+name,'confidence':answer['confidence'],'accepted_fields':flag['asked_fields']})
        assert all(x['centre_m']==y['centre_m']for x,y in zip(base['elements'],geom['elements']))
        assert signature(geom)==signature(used),'Do not silently reuse calculations if geometry differs'
        write(OUT/('Elements_After_'+name+'.json'),geom)
        applied[name]={'mechanical_signature_matches_existing_baseline':True,'vertices_moved':False}
    meta=load(OUT/'Runtime_Metadata.json')
    report={'status':'Final isolated Plan 3 corroboration; original contextual run retained',
            'model_A':meta['runtime_model_ids'],'model_B':'Grok 4.5, student-reported; exact backend unverified',
            'reference_sha256':sha(ref),'original_geometry_sha256':sha(original),
            'reader_results':{'Codex_isolated':sa,'Grok_student_reported':sb},
            'local_gates':{'Codex':local_gate(sa,sb),'Grok':local_gate(sb,sa)},
            'applied_copies':applied,'winner':None,'verdict':'Tie on all five reference questions; no superiority-based winner. Both applied mechanical geometries match the retained numerical baseline.',
            'limitations':['Different native/web interfaces, not an identical harness','Grok website transcript/backend not independently authenticated','Later isolated run corroborates but does not make the original contextual run blind'],
            'baseline_calculations_changed':False}
    write(OUT/'Comparison_and_Application.json',report)
    lines=['# Task 2 - Final isolated Plan 3 corroboration','',
           'Native model run: 2026-11-11. Evidence recovered and ingested: 2026-11-12. The reader completed all five flags before the pause. No model response was invented or relabelled as a new run.','',
           '| Reader | Resolved | Incorrect | Unscorable |','|---|---:|---:|---:|',
           f"| gpt-6.1-sol, runtime-evidenced isolated native run | {sa['resolved']} | {sa['incorrect']} | {sa['unscorable_reference']} |",
           f"| Grok 4.5, student-reported web replies | {sb['resolved']} | {sb['incorrect']} | {sb['unscorable_reference']} |",'',
           report['verdict'],'',
           'Each reader was applied independently to a copy of the classical JSON. No coordinate moved. Labels/sizes/continuity match the exact mechanical signature already used for hand/OpenSees/modification calculations, so this corroboration introduces zero conditional CR shift. This is not full-plan ground truth.','',
           'The old contextual GPT-6 reading is retained as earlier process evidence. The new reader received only frozen crops/questions/common instructions and a no-tools control, one image per turn, with no history fork or reader tool calls. Runtime logs confirm gpt-6.1-sol; the raw version-unknown preface is retained. All delivered image pixels match the frozen crops.','',
           'The web/native interfaces and system environments still differ. Grok identity remains student-reported and no full website transcript is fabricated. The identical-harness requirement is therefore a disclosed deviation, not a box marked fully satisfied.','',
           '[Raw model JSON](Raw_Answers.json), [actual input/output transcript](Raw_Transcript.json), [runtime evidence](Runtime_Metadata.json), [comparison and applied-copy audit](Comparison_and_Application.json).','']
    (OUT/'Report.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Plan3 final cold comparison:',sa['resolved'],sb['resolved'],'of 5; all centres and existing mechanical geometries unchanged')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-log',type=Path)
    args=parser.parse_args()
    if args.runtime_log:ingest(args.runtime_log)
    evaluate()


if __name__=='__main__':
    main()
