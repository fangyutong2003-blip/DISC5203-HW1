"""Score unchanged actual reader outputs against the separately frozen human supplement."""
import json
from pathlib import Path

from task08_compare_readers import load,sha,write,score,local_gate

ROOT=Path(__file__).resolve().parents[1]


def main():
    prior=load(ROOT/'outputs/Task08/reader_comparison/Comparison.json')
    for item in prior['input_hashes']:
        assert sha(ROOT/item['file'])==item['sha256'],'Reader replies must remain unchanged'
    rows=[]
    for plan,directory in (('NewPlan','independent_reference_r3'),('NIST','independent_reference_r2')):
        out=ROOT/'outputs'/plan
        ref_path=out/directory/'Reference.json'
        manifest=load(out/directory/'Reference_Manifest.json')
        assert sha(ref_path)==manifest['reference_sha256']
        reference=load(ref_path)
        flags=load(out/'reader_package_v4/Reader_Manifest.json')['flags']
        a=load(out/'reader_codex_isolated_v4/Parsed_Answers.json')
        b=([load(out/f'reader_grok_received_v4/Followup_NI-F{i:02d}.json') for i in range(1,5)]
           if plan=='NIST' else [json.loads(line) for line in (out/'reader_grok_received_v4/Raw_User_Messages.jsonl').read_text().splitlines()])
        if plan=='NewPlan':
            parent=out/'independent_reference_r2/Reference.json'
            receipt=ROOT/'outputs/NewPlan/human_reference_request/Student_Reading_2026-11-11.json'
            assert sha(parent)==manifest['parent_reference_sha256']
            assert sha(receipt)==manifest['human_receipt_sha256']
            previous=load(parent)
            assert all(x==y for x,y in zip(previous['records'],reference['records']) if x['flag_id']!='NP-F03')
        sa,sb=score(flags,a,reference),score(flags,b,reference)
        rows.append({'plan':plan,'reference_revision':directory,'reference_sha256':sha(ref_path),
                     'readers':{'Codex_gpt_6_1_sol_isolated':sa,'Grok_4_5_student_reported':sb},
                     'local_gates':{'Codex':local_gate(sa,sb),'Grok':local_gate(sb,sa)},
                     'verdict':'tie' if sa['resolved']==sb['resolved'] and sa['incorrect']==sb['incorrect'] else 'inspect differing scores',
                     'full_plan_geometry_complete':False,'model_promoted':None})
    result={'reference_status':'NewPlan R3 non-blind student source review; NIST R2 post-response pixel audit. Original V4/R2 files and scores retained.',
            'human_raw_reply':'T3 3500X400','human_scope':'Printed identifier and size only, not coordinates or student-signed prediction.',
            'reader_inputs_and_outputs_unchanged':True,'input_hashes':prior['input_hashes'],
            'harness_limitations':prior['harness'],'Grok_identity':prior['Grok_identity'],
            'plans':rows,'missing_human_reference':[],
            'overall_verdict':'Both readers agree with all ten supplemented reference flags; tie, no accuracy winner or full-plan promotion.',
            'next_gate':'Complete metric geometry, both-axis scale, dimensions/assumptions and closed-region area conservation before downstream CM/CR/OpenSees.'}
    target=ROOT/'outputs/Task08/reader_comparison_r3'
    target.mkdir(parents=True,exist_ok=True)
    write(target/'Comparison.json',result)
    lines=['# Task 8 - Human-supplemented comparison R3','',result['reference_status'],'',
           '| Plan | Reader | Resolved | Incorrect | Unscorable |','|---|---|---:|---:|---:|']
    for row in rows:
        for name,s in row['readers'].items():
            lines.append(f"| {row['plan']} | {name} | {s['resolved']} | {s['incorrect']} | {s['unscorable_reference']} |")
    lines+=['',result['overall_verdict'],'',result['harness_limitations'],'',
            'The student personally confirmed T3 3500X400 after model answers; this is not a blind pre-response reference. No other R2 flag, raw answer or frozen V4 image was changed. Earlier 9-scorable and original V4 comparisons remain historical evidence.','',result['next_gate'],'']
    (target/'Comparison.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    total={name:sum(row['readers'][name]['resolved'] for row in rows) for name in rows[0]['readers']}
    assert all(count==10 for count in total.values())
    assert all(row['verdict']=='tie' and row['model_promoted'] is None for row in rows)
    print('PASS: unchanged actual replies, frozen R3 source chain, unchanged other reference flags and local gates')
    print(total)


if __name__=='__main__':
    main()
