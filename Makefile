# system python interpreter. used only to create virtual environment
PY = python3
VENV = venv
BIN=$(VENV)/bin

.PHONY: all
all: fmt test build

## Environment
$(VENV): requirements.txt setup.py
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade -r requirements.txt
	$(BIN)/pip install -e .
	touch $(VENV)

## Activate
.PHONY: activate
activate: $(VENV)
	echo "source ./venv/bin/activate"

## Test
.PHONY: fmt
fmt: $(VENV)
	$(BIN)/yapf -ir ./pparse/ ./tests/

.PHONY: test
test: $(VENV)
	$(BIN)/pytest

## Build & Install
.PHONY: build
build: $(VENV)
	$(BIN)/$(PY) -m build

.PHONY: install
install: $(VENV)
	$(BIN)/pip install dist/*.whl

.PHONY: build install

## Clean
.PHONY: clean
clean:
	rm -rf .out .pytest_cache .tox *.egg-info dist build

