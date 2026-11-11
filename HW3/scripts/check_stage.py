"""Validate the actual Git index without changing staged files."""
import ast
import json
import re
import subprocess
import sys


def check_text(path, text):
    errors = []
    if re.search(r"[\u3400-\u9fff]", text):
        errors.append("non-English CJK text")
    if re.search(r"^(<<<<<<< |=======\s*$|>>>>>>> )", text, re.M):
        errors.append("merge conflict marker")
    try:
        if path.endswith((".json", ".geojson")):
            json.loads(text)
        if path.endswith(".jsonl"):
            for line in text.splitlines():
                if line.strip():
                    json.loads(line)
        if path.endswith(".py"):
            ast.parse(text, filename=path)
    except (ValueError, SyntaxError) as exc:
        errors.append(str(exc))
    return errors


def main():
    if "--self-test" in sys.argv:
        assert check_text("bad.md", "\u4e2d\u6587")
        assert check_text("bad.json", "{")
        assert check_text("bad.geojson", "{")
        assert check_text("bad.jsonl", '{}\n{')
        assert check_text("bad.py", "if:")
        assert not check_text("good.md", "English evidence")
        print("PASS: invalid language, JSON and syntax rejected; valid text accepted")
        return 0
    names = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    ).decode("utf-8").split("\0")
    failures = []
    count = 0
    for name in filter(None, names):
        if re.search(r"[\u3400-\u9fff]", name):
            failures.append("Non-English filename")
        if not name.endswith((".md", ".py", ".json", ".geojson", ".jsonl", ".csv", ".txt", ".sh")):
            continue
        raw = subprocess.check_output(["git", "show", ":" + name])
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            failures.append(name + ": text must be UTF-8")
            continue
        failures.extend(name + ": " + e for e in check_text(name, text))
        count += 1
    if failures:
        print("FAIL: staged-content gate\n" + "\n".join(failures))
        return 1
    print(f"PASS: staged-content gate ({count} text files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
