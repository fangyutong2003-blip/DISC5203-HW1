"""Export readable Git evidence; no Git installation is needed to read the output."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
history = subprocess.check_output(
    ["git", "log", "--date=iso-strict", "--format=%h | %aI | %s", "--name-status"],
    cwd=root).decode("utf-8")
history = "".join(c if not "\u3400" <= c <= "\u9fff" else "?" for c in history)
path = root / "HW3" / "records" / "Git_History.md"
path.write_text("# Readable Git History\n\nExported UTC: " +
                datetime.now(timezone.utc).isoformat() +
                "\n\nLegacy non-English characters are replaced by ? in this display only. Original Git history remains intact.\n\n```text\n" +
                history + "\n```\n", encoding="utf-8")
print("Saved", path)
