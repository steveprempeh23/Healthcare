# Migration guide: porting your existing scripts into this scaffold

You already have working code in your old repo. Don't rewrite it — copy it
in and apply this one fix everywhere.

## The problem

Four scripts currently write their output to a hardcoded absolute path that
only exists on your machine:

```
/home/claude/arf_paper/
```

This appears in:
- `simulation.py` (2 occurrences: `summary_table.csv`, `annual_paths.csv`)
- `extended_simulation.py` (1 occurrence: `annual_paths_extended.csv`, plus
  the `summary_at_age50_60.csv` write)
- `sensitivity_analysis.py` (2 occurrences: `sensitivity_results.csv`,
  `tornado_chart.png`)
- `requirements_5_6_analysis.py` (3 occurrences: `debt_trigger_sensitivity.csv`,
  `probabilistic_sensitivity.csv`, `psa_correlations.csv`)
- `reconciliation_analysis.py` (1 occurrence: `calibration_comparison.csv`)

Three of these scripts also do:

```python
sys.path.insert(0, "/home/claude/arf_paper")
from simulation import SCENARIOS, run_scenario, N_HOUSEHOLDS, BASE_OOP_FRACTION
```

That import line is why the scripts currently can't run anywhere except on
your machine, in that exact folder.

## The fix

### 1. Copy your scripts in

```bash
cp /path/to/old/repo/simulation.py src/simulation/
cp /path/to/old/repo/extended_simulation.py src/simulation/
cp /path/to/old/repo/sensitivity_analysis.py src/simulation/
cp /path/to/old/repo/requirements_5_6_analysis.py src/simulation/
cp /path/to/old/repo/reconciliation_analysis.py src/simulation/
cp /path/to/old/repo/ghana_survey_toolkit.py src/extraction/
```

### 2. Replace the hardcoded output path with an environment variable

In each of the 5 simulation-folder scripts, replace every occurrence of:

```python
"/home/claude/arf_paper/
```

with:

```python
os.environ.get("RESULTS_DIR", "results") + "/"
```

...and add `import os` near the top if it isn't already there. Fastest way,
from the repo root, after copying the files in:

```bash
cd src/simulation
for f in simulation.py extended_simulation.py sensitivity_analysis.py \
         requirements_5_6_analysis.py reconciliation_analysis.py; do
  python3 - "$f" <<'EOF'
import re, sys
path = sys.argv[1]
src = open(path).read()
if "import os" not in src:
    src = "import os\n" + src
src = src.replace('"/home/claude/arf_paper/', 'os.environ.get("RESULTS_DIR", "results") + "/" + "')
open(path, "w").write(src)
EOF
done
cd ../..
```

Then open each file and double-check the replaced lines read cleanly, e.g.:

```python
comparison.to_csv(os.environ.get("RESULTS_DIR", "results") + "/" + "calibration_comparison.csv", index=False)
```

(The quick regex above produces a slightly ugly but correct concatenation —
tidy it to `os.path.join(os.environ.get("RESULTS_DIR", "results"), "calibration_comparison.csv")`
if you want it cleaner. Either works.)

### 3. Fix the `sys.path.insert` import hack

In `reconciliation_analysis.py` and `requirements_5_6_analysis.py`, replace:

```python
import sys
sys.path.insert(0, "/home/claude/arf_paper")
from simulation import SCENARIOS as ORIGINAL_SCENARIOS, run_scenario, N_HOUSEHOLDS, BASE_OOP_FRACTION
```

with:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from simulation import SCENARIOS as ORIGINAL_SCENARIOS, run_scenario, N_HOUSEHOLDS, BASE_OOP_FRACTION
```

Same pattern in `extended_simulation.py` (which imports
`SCENARIOS, run_scenario, N_HOUSEHOLDS` without the `ORIGINAL_SCENARIOS`
alias — adjust the import line to match what that file actually imports).

This makes the import relative to wherever the script file itself lives,
rather than to a path that only exists on your machine — so it works the
same whether you run it from the repo root, from inside `src/simulation/`,
or after someone else clones the repo.

### 4. Test it

```bash
mkdir -p results
cd src/simulation
python3 simulation.py
python3 extended_simulation.py
python3 sensitivity_analysis.py
python3 requirements_5_6_analysis.py
python3 reconciliation_analysis.py
cd ../..
ls results/
```

You should see `summary_table.csv`, `annual_paths.csv`,
`annual_paths_extended.csv`, `summary_at_age50_60.csv`,
`sensitivity_results.csv`, `tornado_chart.png`,
`debt_trigger_sensitivity.csv`, `probabilistic_sensitivity.csv`,
`psa_correlations.csv`, and `calibration_comparison.csv`.

### 5. Do the same check for `ghana_survey_toolkit.py`

This one already takes `--root` as a CLI argument and writes its outputs
relative to that root, so it doesn't need the same fix — just confirm there
are no other hardcoded absolute paths left in it (search for
`/home/claude` or `C:\\` to be sure).

```bash
grep -rn "/home/claude" src/
grep -rn "C:\\\\" src/
```

Both should return nothing once you're done.
