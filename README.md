# Healthcare Affordability Burden Study: Ghana's Generation Z — Reproduction Repo

This repository reproduces the data extraction, simulation, and sensitivity
analyses behind the manuscript *Healthcare Affordability Burden Study:
Ghana's Generation Z* (Prempeh, N. O. A., 2026).

## Repository layout

```
.
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── Makefile                      # one command per pipeline stage, and `make all`
├── config/
│   └── config.example.json       # template for the extraction toolkit (no local paths)
├── src/
│   ├── extraction/
│   │   └── ghana_survey_toolkit.py
│   ├── simulation/
│   │   ├── simulation.py
│   │   ├── extended_simulation.py
│   │   ├── sensitivity_analysis.py
│   │   ├── requirements_5_6_analysis.py
│   │   └── reconciliation_analysis.py
│   └── analysis/                 # urban/rural disaggregation, etc. (add as you port it)
├── notebooks/                    # exploratory / results notebooks
├── figures/                      # generated figures (gitignored except .gitkeep)
├── results/                      # generated CSVs/tables (gitignored except .gitkeep)
├── data/
│   ├── raw/                      # YOU place GLSS7/AHIES .dta/.sav files here — NEVER committed
│   └── processed/                # intermediate outputs — NEVER committed
└── docs/
    └── SSRN_submission_draft.md
```

## Why the data isn't in this repo

GLSS7/AHIES microdata is distributed by the Ghana Statistical Service (GSS)
and requires registration/approval. This repo does not redistribute raw
survey data, and `.gitignore` is set up so you cannot accidentally commit it.
Anyone reproducing this work needs to request their own copy of the data from
GSS and place it under `data/raw/`.

## One-time setup

```bash
git clone <your-new-repo-url>.git
cd <your-new-repo-name>
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Step 1 — Extraction (requires your own GLSS7/AHIES data)

Place your `.dta`/`.sav` files under `data/raw/`, then run the toolkit's
auto-discovery mode:

```bash
python3 src/extraction/ghana_survey_toolkit.py scan --root data/raw
python3 src/extraction/ghana_survey_toolkit.py auto --root data/raw
```

`scan` writes `data/raw/scan_report.csv` so you can sanity-check which
columns were matched. `auto` self-discovers the household/health/consumption
files and writes `data/raw/config_auto.json`, then runs the weighted CHE
analysis. Review the printed "AUTO-SELECTED CONFIGURATION" block before
trusting the output — the script says so itself.

If auto-discovery doesn't work for your file-naming convention, use the
manual path instead:

```bash
cp config/config.example.json config/config.json
# edit config/config.json using scan_report.csv
python3 src/extraction/ghana_survey_toolkit.py analyze --config config/config.json
```

## Step 2 — Core simulation (no raw data needed — parameters are hardcoded/calibrated)

```bash
export RESULTS_DIR=results          # see note below on removing the hardcoded path
python3 src/simulation/simulation.py
python3 src/simulation/extended_simulation.py
```

## Step 3 — Sensitivity and reconciliation analyses

```bash
python3 src/simulation/sensitivity_analysis.py
python3 src/simulation/requirements_5_6_analysis.py
python3 src/simulation/reconciliation_analysis.py
```

## Or just run everything

```bash
make all
```

## Reproducibility notes

- Every simulation script seeds its own `numpy.random.default_rng` locally
  (not a shared global stream) and derives scenario-specific seeds via
  `hashlib.md5` rather than Python's randomized `hash()` — so results are
  bit-identical across runs and machines. See comments in `simulation.py`.
- `N_YEARS=26` spans 2026–2051 inclusive (25-year horizon from a 2026 start).
  An earlier draft used `N_YEARS=25`, which under-counted by one year — see
  the note in `simulation.py`.

## Status

- [x] Manuscript drafted and submitted (Springer journal, under review)
- [x] Simulation, sensitivity, and reconciliation code in this repo
- [ ] Extraction toolkit tested against a fresh GLSS7/AHIES pull end-to-end
- [ ] Preprint posted (SSRN)

## Citation

```
Prempeh, N. O. A. (2026). Healthcare Affordability Burden Study: Ghana's
Generation Z. [Journal details to be added upon publication]
```

## Author

**Nana Owusu Achiaw Prempeh**
MSc Data Science, Academic City University College
GitHub: [@steveprempeh23](https://github.com/steveprempeh23)
