"""Audit retained results in a disposable extracted copy, without invoking Git."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = '''import runpy, subprocess, sys
from pathlib import Path
original = subprocess.Popen
class GuardedPopen(original):
    def __init__(self, args, *a, **kw):
        command = args[0] if isinstance(args, (list, tuple)) else str(args).split()[0]
        if str(command).replace(chr(92), '/').rsplit('/', 1)[-1].lower() in ('git', 'git.exe'):
            raise RuntimeError('Git deliberately unavailable during submission audit')
        super().__init__(args, *a, **kw)
subprocess.Popen = GuardedPopen
target = sys.argv[1]
sys.path.insert(0, str(Path(target).resolve().parent))
sys.argv = sys.argv[1:]
runpy.run_path(target, run_name='__main__')
'''


def static_audit():
    errors = []
    files = []
    for directory, children, names in os.walk(ROOT):
        children[:] = [d for d in children if d not in {'.git', 'tmp', '__pycache__', 'Git_Evidence'} and not d.startswith('.venv')]
        files += [Path(directory)/n for n in names]
    text_count = links = 0
    for path in files:
        if path.suffix.lower() not in {'.md', '.py', '.json', '.geojson', '.jsonl', '.csv', '.txt', '.sh'}:
            continue
        relative = path.relative_to(ROOT).as_posix()
        try:
            value = path.read_text(encoding='utf-8-sig')
            text_count += 1
            if re.search(r'[\u3400-\u9fff]', value):
                errors.append(relative+': CJK text in current authored file')
            if path.suffix in {'.json', '.geojson'}:
                json.loads(value)
            elif path.suffix == '.jsonl':
                for line in value.splitlines():
                    if line.strip(): json.loads(line)
            elif path.suffix == '.py':
                ast.parse(value, filename=relative)
            elif path.suffix == '.md':
                for match in re.finditer(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', value):
                    url = match.group(1).strip().split(' "', 1)[0].strip('<>')
                    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', url) or url.startswith('#'):
                        continue
                    target = unquote(url.split('#', 1)[0])
                    if target:
                        links += 1
                        if not (path.parent/target).exists(): errors.append(relative+': missing link '+target)
        except (UnicodeError, ValueError, SyntaxError) as exc:
            errors.append(relative+': '+str(exc))
    return {'text_files': text_count, 'local_links': links, 'errors': errors, 'passed': not errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'SUBMISSION_VALIDATION.json')
    args = parser.parse_args()
    commands = [
        ('Legacy frozen bytes', ['HW3/scripts/restore_legacy_frozen_bytes.py']),
        ('Task 1', ['HW3/scripts/verify_task1.py']),
        ('Task 3', ['HW3/scripts/verify_task03.py']),
        ('Tasks 4/5', ['HW3/scripts/verify_task04.py']),
        ('Tasks 6/7', ['HW3/scripts/verify_task06.py']),
        ('Task 8 unchanged classical artifacts', ['HW3/scripts/verify_task08_classical.py']),
        ('Task 8 actual reader workflow', ['HW3/scripts/verify_task08_workflow.py']),
        ('Task 8 independent engineering', ['HW3/scripts/verify_task08_engineering.py']),
        ('Task 8 actual solver results', ['HW3/scripts/verify_task08_opensees.py']),
        ('Final isolated Plan3 comparison', ['HW3/scripts/final_plan3_reader.py']),
        ('R3 supplemental comparison', ['HW3/scripts/task08_compare_human_r3.py']),
    ]
    results = []
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    for label, command in commands:
        result = subprocess.run([sys.executable, '-c', WRAPPER, *command], cwd=ROOT,
                                env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        results.append({'label': label, 'command': command, 'exit_code': result.returncode,
                        'stdout': result.stdout, 'stderr': result.stderr})
        print(('PASS: ' if result.returncode == 0 else 'FAIL: ')+label, flush=True)
    probe = '''import runpy, subprocess
try:
    subprocess.run(['git', '--version'])
except RuntimeError:
    print('PASS: Git invocation blocked')
else:
    raise AssertionError('Git was not blocked')
namespace = runpy.run_path('HW3/scripts/stage07_floor_and_record.py')
for name in ['tributary_regions.py', 'Step_01C_Tributary_Areas.csv', 'Step_02_Element_Load_Summary.csv']:
    assert namespace['archived_input'](name)
print('PASS: three hash-verified historical inputs readable without Git')
'''
    # Pass the probe through the same guarded environment without a temporary source file.
    result = subprocess.run([sys.executable, '-c', WRAPPER.split('target = sys.argv[1]')[0]+probe],
                            cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    results.append({'label': 'Git-free historical-input probe', 'exit_code': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    static = static_audit()
    passed = all(r['exit_code'] == 0 for r in results) and static['passed']
    report = {'prepared_utc': datetime.now(timezone.utc).isoformat(), 'interpreter': sys.executable,
              'scope': 'Extracted-copy audit of retained results, evidence bytes, current English text and local links. Not a clean installation, new inference or unconditional rubric-compliance claim.',
              'git_invocations_blocked': True, 'commands': results, 'static_audit': static, 'passed': passed}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Static audit:', static['text_files'], 'text files,', static['local_links'], 'local links,', len(static['errors']), 'errors')
    if static['errors']: print('\n'.join(static['errors']))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
