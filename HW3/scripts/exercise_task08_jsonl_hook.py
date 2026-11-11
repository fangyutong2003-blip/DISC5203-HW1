"""Exercise the actual installed pre-commit hook on a staged JSONL fixture."""
import json
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def main():
    fixture=ROOT/'HW3/records/Hook_Task08_Fixture.jsonl'
    valid='{"purpose":"Task 8 staged JSONL hook exercise","valid":true}\n'
    if fixture.exists() and fixture.read_text(encoding='utf-8')!=valid:
        raise ValueError('Existing fixture is not the expected exercise file; do not overwrite')
    env=os.environ.copy()
    env['HW3_PYTHON']=str(ROOT/'.venv_hw3/Scripts/python.exe')
    try:
        fixture.write_text('{}\n{\n',encoding='utf-8',newline='\n')
        subprocess.run(['git','add','--',str(fixture)],cwd=ROOT,check=True)
        bad=subprocess.run(['git','hook','run','pre-commit'],cwd=ROOT,env=env,capture_output=True,text=True)
    finally:
        fixture.write_text(valid,encoding='utf-8',newline='\n')
        subprocess.run(['git','add','--',str(fixture)],cwd=ROOT,check=True)
    good=subprocess.run(['git','hook','run','pre-commit'],cwd=ROOT,env=env,capture_output=True,text=True)
    log={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Actual installed Git hook against a staged JSONL fixture; fixture repaired and retained.',
         'bad_jsonl_exit':bad.returncode,'bad_jsonl_output':bad.stdout+bad.stderr,
         'valid_jsonl_exit':good.returncode,'valid_jsonl_output':good.stdout+good.stderr}
    (ROOT/'HW3/records/Task_08_Actual_Hook_Exercise.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(log,indent=2))
    if bad.returncode==0 or good.returncode!=0:
        raise SystemExit('Actual JSONL hook exercise failed')


if __name__=='__main__':
    main()
