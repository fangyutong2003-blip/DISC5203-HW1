# Historical inputs retained for no-Git inspection

These files are byte-exact copies from commit 5f1eafe, with original Git object paths and hashes in Manifest.json. They are inherited HW1 inputs, not current executable entry points or newly measured CAD geometry.

stage07_floor_and_record.py reads the archived Python file with the AST literal reader to recover only the declared slab/opening data; it does not execute that old plotting script. It reads the two CSV files as retained historical cross-checks. Prefer the current scripts for calculations and plotting. Keeping these snapshots lets the source ZIP be inspected without Git while preserving the original repository history separately.
