.PHONY: all extract simulate extended sensitivity requirements56 reconcile clean

RESULTS_DIR ?= results

all: simulate extended sensitivity requirements56 reconcile

extract:
	python3 src/extraction/ghana_survey_toolkit.py auto --root data/raw

simulate:
	RESULTS_DIR=$(RESULTS_DIR) python3 src/simulation/simulation.py

extended: simulate
	RESULTS_DIR=$(RESULTS_DIR) python3 src/simulation/extended_simulation.py

sensitivity:
	RESULTS_DIR=$(RESULTS_DIR) python3 src/simulation/sensitivity_analysis.py

requirements56:
	RESULTS_DIR=$(RESULTS_DIR) python3 src/simulation/requirements_5_6_analysis.py

reconcile:
	RESULTS_DIR=$(RESULTS_DIR) python3 src/simulation/reconciliation_analysis.py

clean:
	rm -f $(RESULTS_DIR)/*.csv $(RESULTS_DIR)/*.png figures/*.png
