"""Score actual isolated and user-pasted readers against both retained reference revisions."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELDS={'flag_id','label','size_mm','continuous','confidence','reason'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def score(flags,answers,reference,threshold=.8):
    assert [a['flag_id'] for a in answers]==[f['flag_id'] for f in flags]
    refs={r['flag_id']:r for r in reference['records']}
    rows=[]
    for flag,answer in zip(flags,answers):
        assert set(answer)==FIELDS
        confidence=answer['confidence']
        assert type(confidence) in (int,float) and math.isfinite(confidence) and 0<=confidence<=1
        assert answer['continuous'] is None or type(answer['continuous']) is bool
        assert answer['label'] is None or isinstance(answer['label'],str)
        assert answer['size_mm'] is None or isinstance(answer['size_mm'],str)
        assert isinstance(answer['reason'],str) and answer['reason'].strip()
        assert all(answer[k] is None for k in ('label','size_mm','continuous') if k not in flag['asked_fields'])
        ref=refs[flag['flag_id']]
        if not ref['reference_resolved']:
            outcome='unscorable_reference'
        elif confidence<threshold or any(answer[k] is None for k in flag['asked_fields']):
            outcome='low_confidence_or_abstained'
        elif all(answer[k]==ref['expected'][k] for k in flag['asked_fields']):
            outcome='resolved'
        else:
            outcome='incorrect'
        rows.append({'flag_id':flag['flag_id'],'outcome':outcome,'confidence':confidence,
                     'asked_fields':flag['asked_fields']})
    counts={k:sum(r['outcome']==k for r in rows) for k in ('resolved','incorrect','low_confidence_or_abstained','unscorable_reference')}
    return {**counts,'total':len(rows),'flags':rows}


def local_gate(candidate,other):
    resolved={f['flag_id'] for f in candidate['flags'] if f['outcome']=='resolved'}
    protected={f['flag_id'] for f in other['flags'] if f['outcome']=='resolved'}
    return {'no_incorrect_on_scorable_flags':candidate['incorrect']==0,
            'preserves_other_reader_resolved_flags':protected<=resolved,
            'local_scorable_gate_pass':candidate['incorrect']==0 and protected<=resolved}


def main():
    results=[]
    input_hashes=[]
    for plan in ('NewPlan','NIST'):
        output=ROOT/'outputs'/plan
        private=load(output/'reader_package_v4/Flag_Manifest.json')
        flags=load(output/'reader_package_v4/Reader_Manifest.json')['flags']
        a_path=output/'reader_codex_isolated_v4/Parsed_Answers.json'
        answers_a=load(a_path)
        metadata=load(output/'reader_codex_isolated_v4/Run_Metadata.json')
        assert metadata['actual_runtime_model_ids']==['gpt-6.1-sol']
        assert metadata['fork_context'] is False and not metadata['reader_tool_calls']
        if plan=='NewPlan':
            b_paths=[output/'reader_grok_received_v4/Raw_User_Messages.jsonl']
            answers_b=[json.loads(line) for line in b_paths[0].read_text(encoding='utf-8').splitlines()]
        else:
            b_paths=[output/f'reader_grok_received_v4/Followup_NI-F{i:02d}.json' for i in range(1,5)]
            answers_b=[load(path) for path in b_paths]
        for path in [a_path]+b_paths:
            input_hashes.append({'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path)})
        revisions=[]
        for name,directory in (('V4_original_pre_response','independent_reference_v4'),('R2_post_response_sensitivity','independent_reference_r2')):
            path=output/directory/'Reference.json'
            reference=load(path)
            expected_sha=private['reference_sha256'] if directory.endswith('v4') else load(output/directory/'Reference_Manifest.json')['reference_sha256']
            assert sha(path)==expected_sha
            a=score(flags,answers_a,reference,private['confidence_threshold'])
            b=score(flags,answers_b,reference,private['confidence_threshold'])
            revisions.append({'revision':name,'reference_sha256':sha(path),
                              'readers':{'Codex_gpt_6_1_sol_isolated':a,'Grok_4_5_student_reported':b},
                              'local_gates':{'Codex':local_gate(a,b),'Grok':local_gate(b,a)},
                              'verdict':'tie' if a['resolved']==b['resolved'] and a['incorrect']==b['incorrect'] else 'unequal flag scores; inspect full gate before any choice'})
        results.append({'plan':plan,'reference_comparisons':revisions,
                        'asked_field_answers_identical':all(all(a[k]==b[k] for k in f['asked_fields']) for f,a,b in zip(flags,answers_a,answers_b)),
                        'full_plan_geometry_complete':False,'model_promoted':None,
                        'geometry_gate':'Blocked: frozen pipeline has no accepted complete element set or scale. Local flag agreement does not create missing geometry.'})
        bars=load(output/'stage03/Bar_Label_Matches.json')
        results[-1]['geometry_evidence']={
            'source_record':'stage03/Bar_Label_Matches.json',
            'record_sha256':sha(output/'stage03/Bar_Label_Matches.json'),
            'accepted_main_pipeline_claims':len(bars['matches']),
            'scale_seed_px_per_m':bars['scale_seed_px_per_m'],
            'unmatched_labels':bars['unmatched_labels'],
            'unclaimed_candidates':len(bars['unclaimed_candidates'])}
    result={'status':'Actual additional-plan reader comparison; no full-plan geometry promotion',
            'Codex_identity':'gpt-6.1-sol, runtime turn_context evidence; exact weights snapshot not certified',
            'Grok_identity':'Grok 4.5, student-reported; backend snapshot unverified',
            'NIST_Grok_response_route':'Original abbreviated replies retained; complete confidence/reasons are later follow-ups.',
            'harness':'Same V4 crops/questions/order/common instructions; separate interfaces and additional Codex no-tools control. Not an identical harness or randomized blinded cross-service trial.',
            'reference_timing':'V4 reference frozen before user replies. R2 protocol frozen before computation/scoring but after Grok replies; report it as sensitivity, not a replacement pre-response truth.',
            'confidence_threshold':.8,'input_hashes':input_hashes,'plans':results,
            'overall_verdict':'No accuracy winner on scorable flags. Unresolved flags remain unscorable; no model promoted.',
            'missing_human_reference':['NewPlan NP-F03'],
            'downstream_status':'Additional-plan full geometry, tributary/gravity audit, CM/CR and matched OpenSees remain pending.'}
    target=ROOT/'outputs/Task08/reader_comparison'
    target.mkdir(parents=True,exist_ok=True)
    write(target/'Comparison.json',result)
    lines=['# Task 8 - Actual two-reader comparison','',result['status'],'',
           '| Plan | Reference | Reader | Resolved | Incorrect | Abstained/low confidence | Unscorable reference |',
           '|---|---|---|---:|---:|---:|---:|']
    for plan in results:
        for revision in plan['reference_comparisons']:
            for reader,counts in revision['readers'].items():
                lines.append(f"| {plan['plan']} | {revision['revision']} | {reader} | {counts['resolved']} | {counts['incorrect']} | {counts['low_confidence_or_abstained']} | {counts['unscorable_reference']} |")
    lines+=['',result['overall_verdict'],'',result['harness'],'',result['reference_timing'],'',
            'The actual isolated-reader model is supported by retained runtime model metadata, not by its unknown self-report. Grok identity remains student-reported; no further screenshot proof is fabricated or required from the student.','',
            'NewPlan NP-F03 is not marked incorrect or correct against an unresolved reference, even when both models agree. A direct student source reading has been requested and is still pending.','',
            'Both local no-regression checks pass on the scorable subset. Full-plan promotion fails because no complete geometry and scale pass the geometry gate. Neither a tie nor high confidence creates a winner.','',
            result['downstream_status'],'']
    (target/'Comparison.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print(json.dumps({'verdict':result['overall_verdict'],'plans':[{ 'plan':p['plan'],'latest_counts':p['reference_comparisons'][-1]['readers']} for p in results]},indent=2))


if __name__=='__main__':
    main()
