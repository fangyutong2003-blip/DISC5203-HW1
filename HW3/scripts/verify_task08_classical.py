"""Audit frozen inputs, preserved history and additional-plan evidence, not structural accuracy."""
import hashlib
import json
import zipfile
from pathlib import Path

import cv2
import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    def invalid(value):
        raise ValueError('Non-finite JSON literal: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=invalid)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []

    def check(name, condition):
        checks.append({'check':name,'passed':bool(condition)})

    frozen = load(ROOT / 'records/Task_08_Input_Freeze.json')
    for item in frozen['inputs'] + frozen['historic_plan3_outputs']:
        check('Frozen file unchanged: '+item['file'], sha(ROOT/item['file']) == item['sha256'])
    baseline = ROOT / 'outputs/Plan3/stage01'
    regression = ROOT / 'outputs/Regression_Plan3_Task08/stage01'
    for p in baseline.glob('*.png'):
        if p.name == '07_Component_Overlay.png':
            continue
        check('Plan 3 exact classical image regression: '+p.name,sha(p)==sha(regression/p.name))
    original_components = load(baseline/'Classical_Components.json')['components']
    check('Plan 3 complete component records unchanged',original_components==load(regression/'Classical_Components.json')['components'])
    old_overlay = cv2.imread(str(baseline/'07_Component_Overlay.png'))
    new_overlay = cv2.imread(str(regression/'07_Component_Overlay.png'))
    changed = np.any(old_overlay != new_overlay,axis=2)
    labels = np.zeros(changed.shape,np.uint8)
    for component in original_components:
        x,y,_,_ = component['bbox_px']
        cv2.rectangle(labels,(x-3,y-35),(x+55,y+15),255,-1)
    check('Plan 3 overlay differences confined to ID label neighborhoods',not np.any(changed & (labels==0)))
    observations = [{'check':'Plan 3 exact overlay bytes','passed':sha(baseline/'07_Component_Overlay.png')==sha(regression/'07_Component_Overlay.png'),
                     'differing_pixels':int(np.count_nonzero(changed)),
                     'interpretation':'Overlay is not byte/pixel-identical. All six processing images and complete component records are identical; differences lie within ID text neighborhoods. Historic overlay retained. This observation is not reported as an exact-overlay pass.'}]
    summaries = []
    for plan in ('NewPlan','NIST'):
        out = ROOT / 'outputs' / plan
        components = load(out/'stage01/Classical_Components.json')
        check(plan+' fixed threshold/morphology rules', components['parameters']=={
            'ink_less_than':225,'diagonal_line_px':11,'close_square_px':17,
            'open_square_px':21,'wall_aspect_ratio':4,'long_line_kernel_px':81})
        mask = cv2.imread(str(out/'stage01/04_Open21.png'),0)
        check(plan+' component area conservation',int(np.count_nonzero(mask)) == sum(c['area_px'] for c in components['components']))
        check(plan+' mask is binary',set(np.unique(mask)) <= {0,255})
        check(plan+' original image shape retained',list(mask.shape)==components['image_shape_hw'])
        ocr = load(out/'stage02/Dual_OCR.json')
        check(plan+' two actual OCR passes',set(ocr['raw_passes'])=={'original','lines_removed'})
        for name,reading in ocr['raw_passes'].items():
            check(plan+' OCR input hash '+name,sha(ROOT/reading['source'])==reading['sha256'])
        bars = load(out/'stage03/Bar_Label_Matches.json')
        check(plan+' unique label claims',len({x['label'] for x in bars['matches']})==len(bars['matches']))
        check(plan+' unique bar claims',len({x['candidate_id'] for x in bars['matches']})==len(bars['matches']))
        check(plan+' absent scale represented by null',bars['scale_seed_px_per_m'] is None)
        forest = load(out/'stage04_forest/Forest_Report.json')
        saved = joblib.load(out/'stage04_forest/Forest_Never_Selected.joblib')
        check(plan+' forest actually retained and never selected',saved['selected'] is False and forest['selected'] is False)
        check(plan+' frozen forest settings',forest['random_seed']==5203 and forest['trees']==60 and forest['features']==15 and saved['model'].n_estimators==60)
        importance = sum(forest['feature_importance'].values())
        check(plan+' feature importance matches class degeneracy',importance==0 if forest['degenerate_single_class'] else abs(importance-1)<1e-10)
        check(plan+' stored training counts',sum(forest['class_counts'].values())==forest['training_pixels'])
        check(plan+' training is not advertised as transfer accuracy',forest['test_plan'] is None and forest['training_plan']==plan)
        package = out/'reader_package_v3'
        private = load(package/'Flag_Manifest.json')
        public = load(package/'Reader_Manifest.json')
        reference = load(out/'independent_reference_v3/Reference.json')
        check(plan+' reference frozen hash',private['reference_sha256']==sha(out/'independent_reference_v3/Reference.json'))
        check(plan+' common instructions unchanged',private['common_instruction_sha256']==sha(ROOT/'prompts/Reader_Instructions.md')==sha(package/'Reader_Instructions.md'))
        check(plan+' no fabricated reader run or promotion',private['model_runs']==[] and 'no promotion' in private['status'])
        check(plan+' same order public/private/reference',[f['flag_id'] for f in public['flags']]==[f['flag_id'] for f in private['flags']]==[f['flag_id'] for f in reference['records']])
        for flag in private['flags']:
            check(plan+' crop hash '+flag['flag_id'],sha(package/flag['crop'])==flag['sha256'])
            x0,y0,x1,y1 = flag['crop_bbox_px']
            ax,ay = flag['anchor_px']
            check(plan+' marker within crop '+flag['flag_id'],x0<=ax<x1 and y0<=ay<y1)
            if 'target_text_bbox_px' in flag:
                a,b,c,d = flag['target_text_bbox_px']
                check(plan+' full target text within crop '+flag['flag_id'],x0<=a and y0<=b and c<=x1 and d<=y1)
        expected_names = {'Reader_Instructions.md','Reader_Manifest.json','Questions.md'}|{f['crop'] for f in public['flags']}
        with zipfile.ZipFile(ROOT/f'HW3_Task_08_{plan}_Reader_Package_V3.zip') as archive:
            check(plan+' reader ZIP excludes evaluator/reference answers',set(archive.namelist())==expected_names)
            check(plan+' reader ZIP bytes match frozen files',all(archive.read(name)==(package/name).read_bytes() for name in expected_names))
        summaries.append({'plan':plan,'components':len(components['components']),
            'ocr_original':len(ocr['raw_passes']['original']['detections']),
            'ocr_lines_removed':len(ocr['raw_passes']['lines_removed']['detections']),
            'size_hypotheses':len(ocr['label_hypotheses']),'bar_candidates':len(bars['candidates']),
            'provisional_matches':len(bars['matches']),'scale_seed':bars['scale_seed_px_per_m'],
            'forest_training_pixels':forest['training_pixels'],'forest_degenerate':forest['degenerate_single_class'],
            'reader_flags':len(private['flags']),
            'reference_resolved':sum(x['reference_resolved'] for x in reference['records']),
            'reference_unresolved':[x['flag_id'] for x in reference['records'] if not x['reference_resolved']],
            'rejected_queries':len(private['rejected_queries']),'actual_reader_runs':0,
            'CM_CR_status':'pending; no promoted additional-plan geometry'})
    report = {'scope':'Artifact integrity and unchanged classical portability. Passing does not establish correct geometry, reader accuracy or completed Task 8.',
              'passed':sum(x['passed'] for x in checks),'total':len(checks),'checks':checks,'observations':observations,'plans':summaries}
    (ROOT/'records/Task_08_Classical_Validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"Task 8 artifact checks: {report['passed']}/{report['total']}")
    for summary in summaries:
        print(json.dumps(summary))
    if report['passed'] != report['total']:
        raise SystemExit('Task 8 evidence check failed')


if __name__=='__main__':
    main()
