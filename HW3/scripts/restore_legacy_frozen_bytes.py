"""Restore only proven legacy line endings after Git normalisation; never change content."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore',action='store_true',help='Restore original CRLF bytes only when both recorded hashes prove an EOL-only difference')
    args=parser.parse_args()
    manifest=json.loads((ROOT/'HW3/records/Legacy_Frozen_Text_Bytes.json').read_text(encoding='utf-8'))
    restored=[];already=[];need=[]
    for item in manifest['files']:
        path=(ROOT/item['file']).resolve()
        path.relative_to(ROOT.resolve())
        data=path.read_bytes()
        if digest(data)==item['original_bytes_sha256']:
            already.append(item['file']);continue
        canonical=data.replace(b'\r\n',b'\n')
        if digest(canonical)!=item['canonical_lf_sha256']:
            raise ValueError('Content changed, not merely EOL; refuse repair: '+item['file'])
        original=canonical.replace(b'\n',b'\r\n')
        if digest(original)!=item['original_bytes_sha256']:
            raise ValueError('Cannot reconstruct frozen original bytes: '+item['file'])
        if args.restore:
            path.write_bytes(original);restored.append(item['file'])
        else:need.append(item['file'])
    print(json.dumps({'scope':'Exact EOL-only reconstruction of recorded original text; no reference/geometry/answer modification',
                      'already_original':len(already),'restored':len(restored),'need_restore':len(need),
                      'restore_required_files':need},indent=2))
    if need:raise SystemExit('Run with --restore before checking legacy frozen byte hashes')


if __name__=='__main__':
    main()
