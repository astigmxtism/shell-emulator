PYTHON ?= python3
export PYTHONPATH := src

.PHONY: run test

run:
	$(PYTHON) -m shell_emulator $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v
