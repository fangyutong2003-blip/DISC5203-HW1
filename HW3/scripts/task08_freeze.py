"""Freeze additional-plan sources and pre-routing code before execution."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = ROOT / 'records/Task_08_Input_Freeze.json'
    if target.exists():
        record = json.loads(target.read_text(encoding='utf-8'))
        for item in record['inputs']:
            assert digest(ROOT / item['file']) == item['sha256'], item['file']
        print('Frozen source hashes verified; original code hashes not rewritten')
        return
    sources = {'NewPlan': 'sources/assets/NewPlan.png',
               'NIST': 'sources/third_plan_candidates/NIST_Figure_02_Plan.png'}
    record = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'pre_execution_git_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT.parent, text=True).strip(),
        'inputs': [{'plan': k, 'file': v, 'sha256': digest(ROOT / v)}
                   for k, v in sources.items()],
        'original_code': [{'file': 'scripts/' + name, 'sha256': digest(ROOT / 'scripts' / name)}
                          for name in ('stage01_classical.py', 'stage02_ocr.py',
                                       'stage03_bars.py', 'stage04_forest.py')],
        'historic_plan3_outputs': [
            {'file': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)}
            for p in sorted((ROOT / 'outputs/Plan3').rglob('*')) if p.is_file()],
        'scope': 'Freeze before source routing; no VLM answers or promoted geometry supplied.',
        'preprocessing_resize': None,
        'rules': {'threshold_lt': 225, 'diagonal_px': 11, 'close_px': 17,
                  'open_px': 21, 'long_line_px': 81, 'wall_aspect': 4,
                  'bar_open_px': 121, 'forest_seed': 5203, 'forest_trees': 60,
                  'forest_resize': 0.5},
    }
    target.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('Frozen two source images, four original scripts and historic Plan 3 artifacts')


if __name__ == '__main__':
    main()
