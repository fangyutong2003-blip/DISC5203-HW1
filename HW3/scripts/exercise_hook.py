"""Exercise the real installed hook against a deliberately invalid staged fixture."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
fixture = root / "HW3" / "records" / "Hook_Test_Fixture.json"
fixture.write_text("{", encoding="utf-8")
subprocess.run(["git", "add", str(fixture)], cwd=root, check=True)
result = subprocess.run(["git", "hook", "run", "pre-commit"], cwd=root,
                        capture_output=True, text=True)
fixture.write_text(json.dumps({"purpose": "hook exercise", "valid": True}, indent=2),
                   encoding="utf-8")
subprocess.run(["git", "add", str(fixture)], cwd=root, check=True)
accepted = subprocess.run(["git", "hook", "run", "pre-commit"], cwd=root,
                          capture_output=True, text=True)
log = {"created_utc": datetime.now(timezone.utc).isoformat(),
       "hook": ".githooks/pre-commit", "scope": "actual hook invoked against staged fixture",
       "malformed_staged_json_exit": result.returncode,
       "malformed_staged_json_output": result.stdout + result.stderr,
       "repaired_staged_json_exit": accepted.returncode,
       "repaired_staged_json_output": accepted.stdout + accepted.stderr}
(root / "HW3" / "records" / "Hook_Exercise.json").write_text(
    json.dumps(log, indent=2), encoding="utf-8")
print(json.dumps(log, indent=2))
sys.exit(0 if result.returncode != 0 and accepted.returncode == 0 else 1)
