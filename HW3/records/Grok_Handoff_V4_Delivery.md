# Frozen V4 reader handoff delivery

Prepared on 2026-11-11 at the student's request. This is a delivery record, not evidence of a Grok model run.

- Desktop folder: `C:/Users/099fyt/Desktop/HW3_Task08_Grok_V4_2026-11-11`
- Desktop ZIP: `C:/Users/099fyt/Desktop/HW3_Task08_Grok_V4_2026-11-11.zip`
- ZIP SHA256: `54517acdcd34f3f694ae46cf78ddff9c13293c449bc7b5be49773d377a54d4f9`
- Contents: ten unchanged V4 images, ten matching question text files, the unchanged common reader instructions, an English student setup guide and a public-input hash manifest (23 files).

Each question file supplies its flag ID and the exact frozen question. Six NewPlan questions precede four NIST questions. Image hashes were checked against the existing public manifests, common instructions were checked for byte equality, and all ZIP entries were compared byte-for-byte with the delivered folder. An exact file allowlist excludes evaluator reference answers, candidate-label metadata and other-reader responses.

The student should start a fresh chat for each plan, paste `00_Send_First.md` and then send one PNG with its corresponding question file at a time. Record the actual UI model selection and run date; preserve raw answers and conversation evidence. No self-reported backend version is accepted as independently verified identity.

Rebuild in a new destination with the standard-library-only [packager](../scripts/package_grok_handoff.py):

```powershell
python HW3/scripts/package_grok_handoff.py --destination C:/Users/099fyt/Desktop/HW3_Task08_Grok_V4_New_Copy
```

The existing HW3 virtual environment's base interpreter path was unavailable after the host runtime update. This packaging run used `C:/Users/099fyt/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; no structural calculations were rerun and no environment repair is claimed. A newly built ZIP may have different ZIP metadata/timestamps; validate contained files using the manifest rather than expecting identical container hashes.
