"""Build a complete tracked-working-byte delivery with readable Git evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def safe_extract(archive, target):
    with zipfile.ZipFile(archive) as source:
        for info in source.infolist():
            name = PurePosixPath(info.filename)
            if name.is_absolute() or '..' in name.parts or ':' in info.filename or '\\' in info.filename:
                raise ValueError('Unsafe ZIP path: '+info.filename)
        source.extractall(target)


def verify_copy(copy, output):
    result = subprocess.run([sys.executable, str(copy/'HW3/scripts/submission_verify.py'), '--output', str(output)],
                            cwd=copy, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout, flush=True)
    if result.returncode:
        print(result.stderr)
        raise RuntimeError('Extracted-copy validation failed; inspect '+str(output))
    return json.loads(output.read_text(encoding='utf-8'))


def manifest(folder):
    return [{'file': p.relative_to(folder).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
            for p in sorted(folder.rglob('*')) if p.is_file() and p.name != 'SUBMISSION_MANIFEST.json']


def make_zip(folder, archive):
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for path in sorted(folder.rglob('*')):
            if path.is_file(): target.write(path, path.relative_to(folder).as_posix())


def readable_history(folder, head):
    evidence = folder/'Git_Evidence'
    patches = evidence/'Patches'
    patches.mkdir(parents=True)
    commits = git('rev-list', '--reverse', 'HEAD').decode().splitlines()
    lines = ['# Readable English Git history', '', 'Source snapshot: `'+head+'`.', '',
             'All commits remain in the additional Repository.bundle. This export can be read without Git. '
             'The one historical non-English subject is rendered as Created using Colab. '
             'Any CJK characters in historical patch text are represented by literal Unicode escapes; '
             'current authored report text is English. Binary changes are identified, not expanded. '
             'These text exports aid review and are not substitutes for the original Git objects.', '',
             '| Commit | Date | Subject | Changes |', '|---|---|---|---|']
    for number, commit in enumerate(commits, 1):
        meta = git('show', '-s', '--format=%aI%x00%s', commit).decode('utf-8', errors='replace').strip().split('\0', 1)
        date, subject = meta
        if any('\u3400' <= c <= '\u9fff' for c in subject): subject = 'Created using Colab [English rendering of retained original subject]'
        name = f'{number:03d}_{commit[:12]}.patch.txt'
        raw = git('show', '--format=', '--no-ext-diff', '--no-textconv', '--no-color', commit).decode('utf-8', errors='replace')
        raw = ''.join(('\\u'+format(ord(c), '04x')) if '\u3400' <= c <= '\u9fff' else c for c in raw)
        (patches/name).write_text('Commit: '+commit+'\nSubject: '+subject+'\n\n'+raw, encoding='utf-8', newline='\n')
        lines.append(f'| `{commit}` | {date} | {subject.replace("|", "/")} | [Text patch](Patches/{name}) |')
    (evidence/'History_English.md').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    bundle = evidence/'Repository.bundle'
    result = subprocess.run(['git', 'bundle', 'create', str(bundle), '--all'], cwd=ROOT, capture_output=True, text=True)
    if result.returncode: raise RuntimeError(result.stderr)
    result = subprocess.run(['git', 'bundle', 'verify', str(bundle)], cwd=ROOT, capture_output=True, text=True)
    if result.returncode: raise RuntimeError(result.stderr)
    write(evidence/'Bundle_Verification.json', {'source_head': head, 'commits_in_readable_head_history': len(commits),
        'bundle_sha256': sha(bundle.read_bytes()), 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    scratch = ROOT/'tmp'/('submission_check_'+uuid.uuid4().hex[:10])
    scratch.mkdir(parents=True)
    names = [s for s in git('ls-files', '-z').decode('utf-8').split('\0') if s]
    copy = scratch/'working_snapshot'
    for name in names:
        target = copy/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, target)
    if args.preflight_only:
        report = verify_copy(copy, scratch/'Preflight_Validation.json')
        # Simulate exactly the Git-stored LF form of the 37 legacy frozen files.
        entries = json.loads((copy/'HW3/records/Legacy_Frozen_Text_Bytes.json').read_text(encoding='utf-8'))['files']
        for entry in entries:
            data = git('show', 'HEAD:'+entry['file'])
            if sha(data) != entry['canonical_lf_sha256']: raise ValueError('Unexpected canonical Git bytes')
            (copy/entry['file']).write_bytes(data)
        restored = subprocess.run([sys.executable, str(copy/'HW3/scripts/restore_legacy_frozen_bytes.py'), '--restore'],
                                  cwd=copy, capture_output=True, text=True)
        if restored.returncode: raise RuntimeError(restored.stderr+restored.stdout)
        again = verify_copy(copy, scratch/'Restored_Git_Bytes_Validation.json')
        receipt = {'scope': 'Pre-commit working snapshot and Git-canonical legacy-byte restoration audit',
                   'working_snapshot_passed': report['passed'], 'git_canonical_restore_stdout': restored.stdout,
                   'git_canonical_restore_passed': again['passed'], 'validation': report,
                   'scratch': str(scratch), 'timestamp_utc': datetime.now(timezone.utc).isoformat()}
        write(ROOT/'HW3/records/Final_Preflight_Validation.json', receipt)
        print('Preflight and canonical Git-byte restoration passed. Scratch:', scratch)
        return
    if not args.destination: raise ValueError('Supply --destination or --preflight-only')
    if git('status', '--porcelain', '--untracked-files=no').strip(): raise ValueError('Commit tracked changes before final delivery')
    destination = args.destination.resolve()
    archive = destination.with_suffix('.zip')
    if destination.exists() or archive.exists(): raise FileExistsError('Choose a new delivery name; previous deliveries are retained')
    head = git('rev-parse', 'HEAD').decode().strip()
    shutil.copytree(copy, destination)
    readable_history(destination, head)
    start = f'''# DISC 5203 HW3 - Submission

Student: Fangyutong (21353319). Prepared: 2026-11-12.
Repository snapshot: `{head}`.
Public repository: https://github.com/fangyutong2003-blip/DISC5203-HW1

1. Read [the continuous English report](HW3_Final_Report.md).
2. Check [requirements and disclosed limitations](HW3/records/Submission_Requirements_Audit.md).
3. Follow [reproduction and no-Git inspection](HW3/records/Submission_Reproduction.md).
4. Inspect [Reader A JSON](HW3/outputs/final_reader_records/Reader_A_Codex_Flags.json) and [Reader B JSON](HW3/outputs/final_reader_records/Reader_B_Grok_Flags.json); raw records remain linked in the report.
5. Read [English Git history and per-commit changes](Git_Evidence/History_English.md). The additional full-history bundle is in Git_Evidence.
6. Inspect SUBMISSION_VALIDATION.json and SUBMISSION_MANIFEST.json for actual extracted-copy checks and hashes.

All tracked HW1/HW2/HW3 process files are included to preserve the dependency chain. Local virtual environments, temporary inspection material and unrelated personal screenshots are excluded. Earlier steps are retained. The package preserves working-file bytes; run the documented paired-hash bootstrap after a Git clone.

The additional-plan calculations are conditional, with the failed unchanged extraction and source ambiguities explicitly retained. Different reader interfaces, unverified exact Grok backend and tied results are disclosed. This package does not claim full rubric compliance or surveyed geometry.
'''
    (destination/'START_HERE.md').write_text(start, encoding='utf-8', newline='\n')
    provisional = scratch/'provisional.zip'
    make_zip(destination, provisional)
    extracted = scratch/'extracted_submission'
    safe_extract(provisional, extracted)
    report = verify_copy(extracted, scratch/'Extracted_Validation.json')
    write(destination/'SUBMISSION_VALIDATION.json', report)
    write(destination/'SUBMISSION_MANIFEST.json', {'source_commit': head, 'files': manifest(destination),
        'scope': 'Every delivered file except this manifest; exact working bytes and Git evidence included'})
    make_zip(destination, archive)
    with zipfile.ZipFile(archive) as zipped:
        expected = manifest(destination)
        assert len(zipped.namelist()) == len(expected)+1
        for row in expected:
            data = zipped.read(row['file'])
            assert len(data) == row['bytes'] and sha(data) == row['sha256'], row['file']
        assert zipped.read('SUBMISSION_MANIFEST.json') == (destination/'SUBMISSION_MANIFEST.json').read_bytes()
    archive_sha = sha(archive.read_bytes())
    archive.with_suffix('.sha256.txt').write_text(archive_sha+'  '+archive.name+'\n', encoding='utf-8')
    receipt = {'source_commit': head, 'directory': str(destination), 'archive': str(archive),
        'archive_bytes': archive.stat().st_size, 'archive_sha256': archive_sha,
        'files': len(expected)+1, 'all_archive_entries_match_folder_and_manifest': True,
        'extracted_validation_passed': report['passed'], 'scratch': str(scratch),
        'timestamp_utc': datetime.now(timezone.utc).isoformat()}
    write(ROOT/'HW3/records/Final_Delivery_Receipt.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
