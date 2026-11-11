"""Verify reader evidence, frozen references and adversarial no-regression behaviour."""
import copy
import hashlib
import json
from pathlib import Path

from task08_compare_readers import score,local_gate

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks=[]

    def check(name,condition):
        checks.append({'check':name,'passed':bool(condition)})

    comparison=load(ROOT/'outputs/Task08/reader_comparison/Comparison.json')
    for plan in ('NewPlan','NIST'):
        root=ROOT/'outputs'/plan
        frozen=load(root/'reader_package_v4/Flag_Manifest.json')
        public=load(root/'reader_package_v4/Reader_Manifest.json')
        flags=public['flags']
        check(plan+' original reference unchanged',sha(root/'independent_reference_v4/Reference.json')==frozen['reference_sha256'])
        r2=load(root/'independent_reference_r2/Reference.json')
        r2_manifest=load(root/'independent_reference_r2/Reference_Manifest.json')
        check(plan+' R2 frozen bytes',sha(root/'independent_reference_r2/Reference.json')==r2_manifest['reference_sha256'])
        check(plan+' R2 uses frozen original source',r2['source_sha256']==sha(ROOT/r2['source_file'])==frozen['source_sha256'])
        check(plan+' R2 code/protocol hashes',sha(ROOT/'scripts/task08_reference_r2.py')==r2_manifest['code_sha256'] and sha(ROOT/'records/Task_08_Reference_R2_Protocol.md')==r2_manifest['protocol_sha256'])
        reader=root/'reader_codex_isolated_v4'
        transcript=load(reader/'Raw_Tool_Transcript.json')
        answers=load(reader/'Parsed_Answers.json')
        metadata=load(reader/'Run_Metadata.json')
        runtime=load(reader/'Model_Runtime_Evidence.json')
        check(plan+' fresh session no history fork',transcript['fork_context'] is False and metadata['fork_context'] is False)
        check(plan+' isolated session closed',transcript['closed'] is True)
        check(plan+' actual runtime model evidenced',runtime['runtime_model_ids']==['gpt-6.1-sol'] and all(t['model']=='gpt-6.1-sol' for t in runtime['turn_context_model_evidence']))
        check(plan+' one runtime turn per flag',len(runtime['turn_context_model_evidence'])==len(flags))
        check(plan+' no tool or file consultation',runtime['reader_tool_calls']==[] and metadata['reader_tool_calls']==[])
        check(plan+' exact common instructions',(ROOT/'prompts/Reader_Instructions.md').read_text()==transcript['turns'][0]['input_items'][0]['text'])
        for index,(flag,turn,answer) in enumerate(zip(flags,transcript['turns'],answers)):
            actual=(root/'reader_package_v4'/flag['crop'])
            check(flag['flag_id']+' source/crop hash unchanged',sha(actual)==flag['sha256']==turn['source_image_sha256'])
            expected_text='Flag ID: '+flag['flag_id']+'\n\n'+flag['question']
            items=turn['input_items']
            check(flag['flag_id']+' exact question and order',turn['flag_id']==flag['flag_id']==answer['flag_id'] and items[-2]=={'type':'text','text':expected_text})
            check(flag['flag_id']+' native image only',items[-1]['type']=='local_image' and Path(items[-1]['path']).resolve()==actual.resolve() and len(items)==(4 if index==0 else 2))
            raw=turn['raw_response']
            extracted,_=json.JSONDecoder().raw_decode(raw[raw.index('{'):])
            check(flag['flag_id']+' parsed answer equals raw output',extracted==answer)
        actual_score=score(flags,answers,r2)
        check(plan+' confidence does not manufacture winner',comparison['plans'][0 if plan=='NewPlan' else 1]['reference_comparisons'][-1]['verdict']=='tie')
        resolved=[f['flag_id'] for f in actual_score['flags'] if f['outcome']=='resolved']
        check(plan+' has scorable flag for adversarial gate check',bool(resolved))
        bad=copy.deepcopy(answers)
        j=next(i for i,f in enumerate(flags) if f['flag_id']==resolved[0])
        if 'continuous' in flags[j]['asked_fields']:
            bad[j]['continuous']=not bad[j]['continuous']
        else:
            bad[j]['size_mm']='9999x9999'
        bad_score=score(flags,bad,r2)
        check(plan+' wrong high-confidence flag rejected by no-regression gate',bad_score['incorrect']==1 and not local_gate(bad_score,actual_score)['local_scorable_gate_pass'])
        low=copy.deepcopy(answers)
        low[j]['confidence']=.1
        low_score=score(flags,low,r2)
        check(plan+' low confidence cannot resolve or preserve cleared flag',low_score['low_confidence_or_abstained']==1 and not local_gate(low_score,actual_score)['local_scorable_gate_pass'])
        duplicate=copy.deepcopy(answers)
        duplicate[0]['flag_id']=duplicate[1]['flag_id']
        rejected=False
        try:
            score(flags,duplicate,r2)
        except AssertionError:
            rejected=True
        check(plan+' duplicated IDs rejected',rejected)
        check(plan+' no final model promotion',comparison['plans'][0 if plan=='NewPlan' else 1]['model_promoted'] is None and metadata['model_promoted'] is False)
    check('Unresolved T3 remains unscorable even with model consensus',next(f for f in comparison['plans'][0]['reference_comparisons'][-1]['readers']['Codex_gpt_6_1_sol_isolated']['flags'] if f['flag_id']=='NP-F03')['outcome']=='unscorable_reference')
    check('Two independent Codex sessions',load(ROOT/'outputs/NewPlan/reader_codex_isolated_v4/Raw_Tool_Transcript.json')['agent']['agent_id']!=load(ROOT/'outputs/NIST/reader_codex_isolated_v4/Raw_Tool_Transcript.json')['agent']['agent_id'])
    for item in comparison['input_hashes']:
        check('Actual response input hash '+item['file'],sha(ROOT/item['file'])==item['sha256'])
    record={'scope':'Workflow/evidence integrity and adversarial flag gate; not full geometry or engineering validation.',
            'passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks}
    target=ROOT/'records/Task_08_Workflow_Validation.json'
    target.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"Task 8 workflow: {record['passed']}/{record['total']}")
    if record['passed']!=record['total']:
        raise SystemExit('Workflow validation failed')


if __name__=='__main__':
    main()
