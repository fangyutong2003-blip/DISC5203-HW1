"""Bundle only frozen public reader inputs and matching copy-ready questions."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    destination = args.destination.resolve()
    archive_path = destination.with_suffix('.zip')
    if destination.exists() or archive_path.exists():
        raise FileExistsError('Handoff destination already exists; choose a new revision')
    sources = [('01_NewPlan', 'NewPlan'), ('02_NIST', 'NIST')]
    inputs = {}
    instructions = (ROOT/'prompts/Reader_Instructions.md').read_bytes()
    inputs['00_Send_First.md'] = instructions
    guide = '''# Grok image-reader handoff - frozen V4 inputs

This folder contains only public reader inputs and user setup instructions. No reference answers, other-reader outputs or structural calculation reports are included.

1. Select an image-capable model. Save a screenshot showing the actual UI model selection. A model's self-description alone does not verify the backend version; record an unavailable identifier as unknown.
2. Open a fresh chat for NewPlan and a separate fresh chat for NIST. At the start of each chat, paste the complete contents of 00_Send_First.md unchanged.
3. In 01_NewPlan, send NP-F01.png with NP-F01_Question.txt. Wait for its answer, then continue in ascending order through NP-F06.
4. In 02_NIST, send NI-F01.png with NI-F01_Question.txt. Wait for its answer, then continue through NI-F04.
5. Attach the actual PNG, not a screenshot of the folder or a text filename. The ZIP is for transport; extract it locally and send the images individually.
6. Save each original JSON answer without correction, plus screenshots or a conversation export showing the submitted images/questions and answers. Do not silently retry, repair or replace an answer; retain any retry separately.
7. Return the ten raw JSON answers, the UI model screenshot and available conversation evidence to the coursework agent. Record the actual run date and interface used.

Do not send this setup guide, Package_Manifest.json, independent references, calculation reports or another reader's answers as extra model context. Each *_Question.txt supplies the exact flag ID and frozen question. Use this same input package for either reader when collecting comparable runs.
'''
    inputs['README_For_Student.md'] = guide.encode('utf-8')
    records = []
    for folder, plan in sources:
        package = ROOT/'outputs'/plan/'reader_package_v4'
        manifest = json.loads((package/'Reader_Manifest.json').read_text(encoding='utf-8'))
        assert (package/'Reader_Instructions.md').read_bytes() == instructions
        for flag in manifest['flags']:
            data = (package/flag['crop']).read_bytes()
            assert sha(data) == flag['sha256'], flag['flag_id']
            relative = folder+'/'+flag['crop']
            question_file = folder+'/'+flag['flag_id']+'_Question.txt'
            question = 'Flag ID: '+flag['flag_id']+'\n\n'+flag['question']+'\n'
            inputs[relative] = data
            inputs[question_file] = question.encode('utf-8')
            records.append({'plan':plan,'flag_id':flag['flag_id'],
                            'image':relative,'image_sha256':sha(data),
                            'question_file':question_file,
                            'frozen_question':flag['question']})
    assert len(records) == 10
    record = {'purpose':'Public frozen V4 reader handoff; not a model-run record',
              'prepared_date':'2026-11-11',
              'common_instructions_sha256':sha(instructions),
              'flags':records,
              'files':[{'file':name,'sha256':sha(data)} for name,data in sorted(inputs.items())]}
    inputs['Package_Manifest.json'] = (json.dumps(record,indent=2)+'\n').encode('utf-8')
    destination.mkdir(parents=True)
    for relative,data in inputs.items():
        target = destination/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED) as archive:
        for relative,data in sorted(inputs.items()):
            archive.writestr(relative,data)
    with zipfile.ZipFile(archive_path) as archive:
        assert set(archive.namelist()) == set(inputs)
        assert all(archive.read(name)==data==(destination/name).read_bytes()
                   for name,data in inputs.items())
    # Exact allowlist ensures no evaluator metadata or expected answers leak.
    assert len(inputs)==23
    print(json.dumps({'folder':str(destination),'zip':str(archive_path),
                      'images':10,'matching_question_files':10,
                      'all_23_files_verified':True,
                      'zip_sha256':sha(archive_path.read_bytes())},indent=2))


if __name__ == '__main__':
    main()
