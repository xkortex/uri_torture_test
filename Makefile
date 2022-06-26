PYTEST_OPTS ?= --cov

## ============================ Testing =================================
.PHONY: test format lint
# PYTHONPATH here ensures local code is imported first and test coverage is tabulated correctly
test:
	PYTHONPATH=. pytest $(PYTEST_OPTS) .

format:
	isort .
	black .

lint:
	isort . --check-only --df
	black . --check --diff