"""
Run this once from inside src/simulation/, after copying your 5 scripts in:

    python fix_paths.py

It rewrites the hardcoded "/home/claude/arf_paper/" output path to use a
RESULTS_DIR environment variable (defaulting to "../../results" relative to
this folder), and fixes the sys.path.insert import hack so the scripts work
on any machine, not just the one they were originally written on.

Safe to run more than once -- it skips files that are already patched.
"""
import re
from pathlib import Path

FILES = [
    "simulation.py",
    "extended_simulation.py",
    "sensitivity_analysis.py",
    "requirements_5_6_analysis.py",
    "reconciliation_analysis.py",
]

OLD_PATH = "/home/claude/arf_paper/"
NEW_PATH_EXPR = 'os.environ.get("RESULTS_DIR", str(Path(__file__).resolve().parent.parent.parent / "results")) + "/"'

OLD_SYS_PATH_LINE_RE = re.compile(r'sys\.path\.insert\(0,\s*["\']\/home\/claude\/arf_paper["\']\)')
NEW_SYS_PATH_LINE = 'sys.path.insert(0, str(Path(__file__).resolve().parent))'

changed_any = False

for fname in FILES:
    p = Path(fname)
    if not p.exists():
        print(f"SKIP (not found): {fname}")
        continue

    src = p.read_text(encoding="utf-8")
    original = src

    # 1. Fix hardcoded output path
    if OLD_PATH in src:
        src = src.replace(f'"{OLD_PATH}', f'{NEW_PATH_EXPR} + "')

    # 2. Fix sys.path.insert hack, if present
    if OLD_SYS_PATH_LINE_RE.search(src):
        src = OLD_SYS_PATH_LINE_RE.sub(NEW_SYS_PATH_LINE, src)

    # 3. Ensure required imports are present
    needed_imports = []
    if "os.environ" in src and "import os" not in src:
        needed_imports.append("import os")
    if "Path(__file__)" in src and "from pathlib import Path" not in src:
        needed_imports.append("from pathlib import Path")

    if needed_imports:
        # insert after the module docstring if present, else at the top
        lines = src.split("\n")
        insert_at = 0
        if lines and lines[0].strip().startswith(('"""', "'''")):
            quote = lines[0].strip()[:3]
            # find closing triple-quote
            if lines[0].strip().count(quote) >= 2 and len(lines[0].strip()) > 3:
                insert_at = 1  # single-line docstring
            else:
                for i in range(1, len(lines)):
                    if quote in lines[i]:
                        insert_at = i + 1
                        break
        lines[insert_at:insert_at] = needed_imports
        src = "\n".join(lines)

    if src != original:
        p.write_text(src, encoding="utf-8")
        print(f"PATCHED: {fname}")
        changed_any = True
    else:
        print(f"NO CHANGE NEEDED: {fname}")

if not changed_any:
    print("\nNothing patched -- either files were already fixed, or none were found.")
else:
    print("\nDone. Double check each file's changed lines before running it.")
