# Legacy frozen-text portability

Final audit date: 2026-11-12.

The legacy Plan 3 reference and 36 other protected text outputs were originally hashed with Windows CRLF bytes. Git normalises those files to LF. Their mathematical content is identical, but a fresh Git checkout would fail the original strict SHA256 comparisons. The later V4/R2/R3 additional-plan files already use explicit LF and are unaffected.

The old references, answers and hash expectations are **not changed**. [Legacy_Frozen_Text_Bytes.json](Legacy_Frozen_Text_Bytes.json) records both each canonical LF hash and the original CRLF hash. [The bootstrap](../scripts/restore_legacy_frozen_bytes.py) will restore only a line-ending transformation whose complete bytes match both recorded hashes. A changed character, geometry, size or response causes refusal. Active reports and source-code revisions are excluded from restoration.

After a Git clone, run from its root:

```text
python HW3/scripts/restore_legacy_frozen_bytes.py --restore
```

The delivered working-byte snapshot already preserves those original bytes; the same command safely verifies them without modification. This is a disclosed portability repair, not a retroactive change to a reader/reference result. The source ZIP will also contain byte-exact snapshots of the three inherited inputs required by stage07; numerical inspection does not require Git.
