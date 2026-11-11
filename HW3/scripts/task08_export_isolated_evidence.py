"""Derive parsed reader outputs and minimal runtime metadata from actual isolated sessions."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def write(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',choices=['NewPlan','NIST'],required=True)
    parser.add_argument('--session-directory',type=Path,required=True)
    args=parser.parse_args()
    out=ROOT/'outputs'/args.plan/'reader_codex_isolated_v4'
    transcript=json.loads((out/'Raw_Tool_Transcript.json').read_text(encoding='utf-8'))
    flags=json.loads((ROOT/'outputs'/args.plan/'reader_package_v4/Reader_Manifest.json').read_text())['flags']
    assert len(transcript['turns'])==len(flags)
    parsed=[]
    for flag,turn in zip(flags,transcript['turns']):
        assert flag['flag_id']==turn['flag_id']
        assert flag['sha256']==turn['source_image_sha256']
        texts=[item['text'] for item in turn['input_items'] if item['type']=='text']
        assert texts[-1]=='Flag ID: '+flag['flag_id']+'\n\n'+flag['question']
        raw=turn['raw_response']
        start=raw.index('{')
        answer,end=json.JSONDecoder().raw_decode(raw[start:])
        assert answer['flag_id']==flag['flag_id']
        assert not raw[start+end:].strip()
        parsed.append(answer)
    write(out/'Parsed_Answers.json',parsed)
    agent_id=transcript['agent']['agent_id']
    paths=list(args.session_directory.glob('*'+agent_id+'.jsonl'))
    assert len(paths)==1
    path=paths[0]
    turns=[]
    tools=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        entry=json.loads(line)
        payload=entry.get('payload',{})
        if entry.get('type')=='turn_context':
            turns.append({k:payload[k] for k in ('turn_id','model','effort') if k in payload})
        if entry.get('type')=='response_item' and payload.get('type') in ('function_call','custom_tool_call'):
            tools.append(payload.get('name'))
    models=sorted({turn['model'] for turn in turns})
    assert len(turns)==len(flags),(len(turns),len(flags))
    assert not tools,'Reader violated no-tool control: '+str(tools)
    evidence={'agent_id':agent_id,'runtime_log_file':path.name,
              'runtime_log_sha256_at_capture':hashlib.sha256(path.read_bytes()).hexdigest(),
              'metadata_extraction_scope':'Only turn ID, model and effort fields plus tool-call names; no private reasoning or unrelated logs copied.',
              'turn_context_model_evidence':turns,'runtime_model_ids':models,
              'reader_tool_calls':tools,
              'identity_note':'Runtime model routing ID, not a separately certified weights snapshot. Agent self-report unknown is retained in the raw response.'}
    write(out/'Model_Runtime_Evidence.json',evidence)
    common=transcript['turns'][0]['input_items'][0]['text'].encode('utf-8')
    original=(ROOT/'prompts/Reader_Instructions.md').read_bytes()
    assert common==original,'Common instruction bytes differ'
    metadata={'run_date':'2026-11-11','interface':'Codex isolated native-image agent',
              'actual_runtime_model_ids':models,'model_identity_source':'Model_Runtime_Evidence.json',
              'fork_context':False,'one_fresh_session_per_plan':True,'one_flag_per_turn':True,
              'reference_or_other_reader_files_provided':False,
              'reader_tool_calls':tools,'common_instruction_sha256':hashlib.sha256(common).hexdigest(),
              'model_promoted':False,
              'parsed_answers_note':'JSON mechanically extracted from original completed-agent messages; all raw prefaces and reasons retained.',
              'harness_limitations':'Separate interface from Grok web. Additional no-tools/isolation control is recorded in actual first-turn input. Platform system prompts are not controlled by the student.',
              'full_plan_accuracy_claimed':False}
    write(out/'Run_Metadata.json',metadata)
    print(args.plan,'actual isolated responses exported;',len(parsed),'flags;',models,'; no tools used')


if __name__=='__main__':
    main()
