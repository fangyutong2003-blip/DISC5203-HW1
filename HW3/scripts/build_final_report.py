"""Build a continuous English report from current results while preserving all source chapters."""
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote

REPO=Path(__file__).resolve().parents[2]
HW3=REPO/'HW3'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def merge_chapter(path,title):
    text=path.read_text(encoding='utf-8-sig')
    text=re.sub(r'^# .+\n','',text,count=1).lstrip()
    text=re.sub(r'^Student:.+\n','',text,count=1).lstrip()
    # Original files are unmodified; chapter status language refers to its audit stage.
    def link(match):
        target=match[2].strip()
        if target.startswith(('http:','https:','mailto:','#')):return match[0]
        if target.startswith('<')and target.endswith('>'):target=target[1:-1]
        base,sep,anchor=target.partition('#')
        absolute=(path.parent/unquote(base)).resolve()
        if not absolute.exists():raise FileNotFoundError(str(path)+': '+target)
        relative=Path(os.path.relpath(absolute,REPO)).as_posix()
        return match[1]+relative+(sep+anchor if sep else'')+match[3]
    text=re.sub(r'(!?\[[^\]]*\]\()([^\)]+)(\))',link,text)
    text=re.sub(r'^(#{2,5}) ',lambda m:'#'+m[1]+' ',text,flags=re.M)
    return f'## {title}\n\nSource stage: [{path.name}]({path.relative_to(REPO).as_posix()}). Historical status statements describe that stage; the current status/audit at the start of this report controls.\n\n'+text.rstrip()+'\n\n'


def aggregate_readers():
    target=HW3/'outputs/final_reader_records';target.mkdir(parents=True,exist_ok=True)
    a={p:load(HW3/('outputs/Plan3/reader_A_isolated_final/Raw_Answers.json'if p=='Plan3'else f'outputs/{p}/reader_codex_isolated_v4/Parsed_Answers.json'))for p in ('Plan3','NewPlan','NIST')}
    b={'Plan3':load(HW3/'outputs/Plan3/reader_B_grok/Raw_Answers.json'),
       'NewPlan':[json.loads(line)for line in (HW3/'outputs/NewPlan/reader_grok_received_v4/Raw_User_Messages.jsonl').read_text().splitlines()],
       'NIST':[load(HW3/f'outputs/NIST/reader_grok_received_v4/Followup_NI-F{i:02d}.json')for i in range(1,5)]}
    write(target/'Reader_A_Codex_Flags.json',a);write(target/'Reader_B_Grok_Flags.json',b)
    paths=['outputs/Plan3/reader_A_isolated_final/Raw_Answers.json','outputs/Plan3/reader_B_grok/Raw_Answers.json',
           'outputs/NewPlan/reader_codex_isolated_v4/Parsed_Answers.json','outputs/NewPlan/reader_grok_received_v4/Raw_User_Messages.jsonl',
           'outputs/NIST/reader_codex_isolated_v4/Parsed_Answers.json']+[f'outputs/NIST/reader_grok_received_v4/Followup_NI-F{i:02d}.json'for i in range(1,5)]
    write(target/'Provenance.json',{'prepared_date':'2026-11-12','purpose':'Mechanical aggregation, not a new model run or answer repair',
        'path_base':'repository root','reader_A':'gpt-6.1-sol, runtime-evidenced isolated sessions',
        'reader_B':'Grok 4.5, student-reported; NIST records are complete follow-ups, originals retained',
        'files':[{'file':'HW3/'+p,'sha256':hashlib.sha256((HW3/p).read_bytes()).hexdigest()}for p in paths]})
    assert sum(map(len,a.values()))==sum(map(len,b.values()))==15


def main():
    aggregate_readers()
    audit='''# HW3 requirement-to-evidence audit

Prepared: 2026-11-12. This is a truthful evidence map, not a blanket assertion of rubric compliance.

| Requirement | Main evidence | Current assessment |
|---|---|---|
| 1A classical threshold/morphology/components/grid/regions | HW3_Task_01_Report.md; Plan3 stage01 and task1 | Assigned-plan implementation retained; outline/scale assumptions stated |
| 1B two OCR reads, one label/bar, dimensions/JSON/audit | Plan3 stage02/stage03/stage05/task1 | 21 assigned-plan elements; measured and dimension-chain scale routes retained |
| 1C trained forest and importance, never selected | Three stage04_forest directories | Real models retained; NIST is explicitly background-only/degenerate |
| 1D flags only, copies, source provenance | Frozen packages; actual raw transcripts; applied geometry copies | No VLM vertices; old contextual first reading preserved as historical |
| 2 two different VLMs, same crops/questions/order | Two consolidated JSON files; Plan3 reader_A_isolated_final; Task8 actual records | Actual isolated Codex plus user-pasted Grok; same public inputs; exact same execution harness NOT established |
| Independent reference and resolved/broken scores | Original Plan3 reference; V4/R2/R3 references and comparisons | Plan3 reference predates answers; additional-plan R2/human supplements are disclosed post-response revisions |
| Higher-score winner, no regression | Per-plan comparisons and two applied Plan3 copies | Ties retained; no invented superiority-based winner; conditional common geometry rather than unconditional pipeline promotion |
| 3 CM, shear-inclusive stiffness, hand 3x3 K/CR | HW3_Task_03_Analytical_Report.md; hand JSON/CSV | Matched provisional baseline; dimensional inconsistencies corrected by derivation |
| 4 actual rigidDiaphragm/Transformation OpenSees, unit loads | HW3_Task_04_05_OpenSees_Report.md; raw results | 75 retained main-plan checks; forces are assumed 100 kN demonstrations |
| 5 zero rotation through CR and push/turn decomposition | Task4 results/checks and additional-plan solver checks | Numerical checks passed under the stated model |
| 6 fixed-mass modification with before/after | HW3_Task_06_07_Modification_Report.md; trajectory | Actual hand/model reruns; exact and rounded designs, cost and limits retained |
| 7 amplification, modes, limits and extraction consequence | Tasks6/7 report; Task8 source sensitivities | Quantified; single-floor diagnostics distinguished from full-building modes |
| 8 unchanged pipeline on NewPlan and found plan | Frozen stage01-04 outputs; original comparison | Unchanged rules were run but FAILED complete extraction; not relabelled as success |
| 8 engineering comparison on additional plans | HW3_Task_08_Conditional_Engineering_Report.md | Supplemental deterministic recovery and conditional calculations, 364 engineering/140 solver checks |
| Full source certainty on additional plans | Geometry/source audit and sensitivity files | NOT established: C17/C20 inferred, NIST 21/25 column discrepancy, unknown column weights, schematic wall sizes |
| All English and retained process files | Continuous report, scripts, records and snapshot | Current authored text audited; original source images preserved; one legacy commit subject rendered in English without rewriting history |
| Git/hooks/readable process evidence | .githooks/pre-commit, actual rejection/repair logs, bundle and readable export | JSON/JSONL/GeoJSON/syntax/language gate; Git-free inspection supplied |
| Student instructions versus agent proposals | Pre-solve briefs, iteration log, raw T3 source reading | No signed student pre-solve prediction or backdated human review invented |

Open deviations must remain visible in the submitted report: different reader interfaces; unverified exact Grok backend; no unique accuracy winner; post-response supplementary references; failed unchanged additional-plan extraction; conditional source geometry/known-only NIST gravity. Submission assembly does not erase these deviations.
'''
    (HW3/'records/Submission_Requirements_Audit.md').write_text(audit,encoding='utf-8',newline='\n')
    reproduce='''# Reproduction and Git-free inspection

Prepared: 2026-11-12. Tested environment: Windows x64, Python 3.12.14; observed versions are in Submission_Runtime_Versions.json. Other operating systems and a fresh dependency installation have not been claimed as tested.

## Read without Git

Open HW3_Final_Report.md at the repository/package root. All figures, raw outputs, model code and intermediate records are included. The delivered package also supplies Git_Evidence/History_English.md and per-commit text patches, so process grading does not require a Git installation. Repository.bundle is an additional full-history copy, not the only process evidence.

## Environment

From the repository root, use Python 3.12 and install HW3/requirements.txt in an isolated environment. Direct dependencies include SciPy and joblib. On Windows, an example is:

```powershell
py -3.12 -m venv .venv_reproduce
.venv_reproduce/Scripts/python.exe -m pip install -r HW3/requirements.txt
.venv_reproduce/Scripts/python.exe HW3/scripts/restore_legacy_frozen_bytes.py --restore
.venv_reproduce/Scripts/python.exe HW3/scripts/submission_verify.py
```

On another platform use its Python 3.12 virtual-environment interpreter and available OpenSeesPy backend. The retained forest pickle is version-sensitive; compare the observed package versions before loading it. No API key is needed to inspect or validate the retained actual reader answers. Scripts do not fabricate a new VLM run.

## Preserve frozen evidence when replaying

The numerical validators independently inspect retained exported results. They are not a claim to rerun a model inference. To replay calculations, work in a separate copy so the original frozen evidence remains untouched:

```text
python HW3/scripts/task03_centres.py
python HW3/scripts/task04_opensees.py
python HW3/scripts/task06_modify.py
python HW3/scripts/task08_geometry_recovery.py
python HW3/scripts/task08_areas_and_hand.py
python HW3/scripts/task08_areas_and_hand.py --refined
python HW3/scripts/verify_task08_engineering.py
python HW3/scripts/task08_opensees.py
python HW3/scripts/verify_task08_opensees.py
python HW3/scripts/task08_source_sensitivity.py
```

The original image-stage commands and their failures remain in the retained task reports. Rebuilding classical/forest stages can change creation times/training times and thus artifact hashes; this must not be confused with a fresh blinded reference or an identical raw model run. Main-plan stage07 can read the three byte-exact historical snapshots in HW3/sources/legacy_snapshots/5f1eafe without Git; it parses the old Python literals rather than executing the old plotting code.

## Legacy byte hashes

37 legacy Plan3 text artifacts were frozen as CRLF before Git LF normalization. The bootstrap uses paired full-file hashes to reconstruct only that exact EOL change. It refuses real content changes and never changes a reference expectation. The later V4/R2/R3 records already use explicit LF. The working-byte submission snapshot preserves original bytes; Git clones should run the bootstrap before frozen-hash validators. See Legacy_Line_Ending_Portability.md.

## Validation scope

The final package check runs the retained-data validators in an extracted copy using the available tested interpreter, with Git calls unavailable to the check process. This is an extraction/portability and numerical-result audit, not a clean-machine dependency-install test or proof that all rubric conditions were met. Source interpretation, harness differences and known-only NIST gravity remain explicitly conditional.
'''
    (HW3/'records/Submission_Reproduction.md').write_text(reproduce,encoding='utf-8',newline='\n')
    intro='''# DISC 5203 Homework 3 - Continuous Submission Report

**Student:** Fangyutong  
**Student ID:** 21353319  
**Date assembled:** 12 November 2026  
**Assigned drawing:** Floor Plan 3  
**Repository:** [DISC5203-HW1](https://github.com/fangyutong2003-blip/DISC5203-HW1)

## Current result and honest submission status

This report consolidates the completed calculations and the actual image-reader/process evidence. The retained main-plan model has CM=(4.963771,8.326083) m, CR=(5.563280,9.694116) m and e=1.493628 m. A fixed-mass T9/T10 thickening proposal aligns the ideal model numerically; the 5 mm-rounded proposal leaves e=0.007113 m. NewPlan and the found NIST plan have supplementary conditional geometry, closed regions, known gravity, hand CM/K/CR and actual matched OpenSees calculations.

The original main-plan contextual reader is preserved. A fresh history-free gpt-6.1-sol reader actually completed its five frozen questions on 11 November, before the pause; its recorded evidence was ingested on 12 November. It and student-reported Grok 4.5 resolve all five against the original separately generated reference, and both applied mechanical geometries match the geometry already used in the calculations. No model answer or original geometry is rewritten to force agreement.

Both models also agree on the ten additional-plan flags under the separately recorded R2/R3 supplements. These are ties, not evidence of a more accurate winner. The native and web interfaces differ; Grok's exact backend is unverified. Additional-plan R2 and human-reference supplements are post-response audits. The unchanged image rules failed complete extraction on the extra drawings; later solid-symbol recovery is a disclosed supplementary method. C17/C20 assumptions, NIST missing column information and schematic wall uncertainty remain material limitations. This is a submission of actual conditional work, not a claim of unconditional rubric compliance or design certification.

**Start here for evidence:** [requirement audit](HW3/records/Submission_Requirements_Audit.md), [reproduction/no-Git guide](HW3/records/Submission_Reproduction.md), [task status](HW3/records/Task_Status.md), [iteration log](HW3/records/Iteration_Log.md).

**The two model-output JSON files:** [Reader A - isolated Codex, all three plans](HW3/outputs/final_reader_records/Reader_A_Codex_Flags.json) and [Reader B - student-reported Grok, all three plans](HW3/outputs/final_reader_records/Reader_B_Grok_Flags.json). These are mechanical aggregations of retained original JSON, with [source hashes](HW3/outputs/final_reader_records/Provenance.json); NIST Grok entries are complete follow-ups and its abbreviated originals remain retained.

## Report structure and authorship

The chapters below contain the analytical derivations, actual solver checks and numerical interpretation in one continuous Markdown file. Their original stage reports and all earlier outputs remain available. Historical status lines inside retained chapters describe that stage; the current result and requirement audit above control. No student-signed prediction, independent CAD survey, API call, earlier timestamp or human review is invented. Agent-authored pre-solve proposals and actual student instructions are separated in the linked records.

The 100 kN forces are assumed linear-analysis demonstrations, not prescribed code seismic demands. Periods are single-floor 3-DOF diagnostics, not whole-building periods. NIST gravity output is known-only because column sections/weights are missing. Independent numerical agreement checks the stated idealisation; it does not authenticate source geometry or remove experimental limits.

'''
    chapters=[(HW3/'HW3_Task_01_Report.md','1. Assigned-plan extraction and retained forest'),
              (HW3/'outputs/Plan3/reader_A_isolated_final/Report.md','2. Final isolated two-reader comparison on Plan 3'),
              (HW3/'HW3_Task_03_Analytical_Report.md','3. Hand mass, stiffness and centre of rigidity'),
              (HW3/'HW3_Task_04_05_OpenSees_Report.md','4. Actual main-plan OpenSees and load decomposition'),
              (HW3/'HW3_Task_06_07_Modification_Report.md','5. Fixed-mass modification and why alignment matters'),
              (HW3/'HW3_Task_08_Conditional_Engineering_Report.md','6. Additional plans and the conditional three-plan comparison')]
    text=intro+''.join(merge_chapter(path,title)for path,title in chapters)
    text+='''## 7. Reproduction, process record and remaining limits

Use the [reproduction guide](HW3/records/Submission_Reproduction.md) and [observed runtime versions](HW3/records/Submission_Runtime_Versions.json). The package includes a plain-readable Git history/change export in addition to a full Git bundle. The [installed hook](.githooks/pre-commit), [actual damaged-fixture rejection/repair log](HW3/records/Task_08_Actual_Hook_Exercise.json), [project guidance](AGENTS.md) and [reusable project procedures](skills.md) are retained. The package's START_HERE.md identifies its exact source snapshot and manifest.

The final audit distinguishes delivered work from open methodology/source deviations. In particular, it does not claim an identical execution harness, a uniquely higher-score reader, an unchanged-pipeline success on both added drawings, complete NIST gravity information or surveyed precision of image-derived coordinates. These limits are part of the engineering argument and must remain visible when submitting or defending the work.
'''
    (REPO/'HW3_Final_Report.md').write_text(text,encoding='utf-8',newline='\n')
    print('Built continuous English report, requirement audit, reproduction guide and two consolidated reader JSON files')


if __name__=='__main__':
    main()
