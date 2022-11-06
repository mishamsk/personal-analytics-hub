.DEFAULT_GOAL := help

sources = etl

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr site/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '.mypy_cache' -exec rm -fr {} +
	find . -name 'requirements-*.txt' -exec rm -fr {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr testtemp/

.PHONY: format
format:
	isort $(sources)
	black $(sources)

.PHONY: lint
lint:
	flake8 $(sources)
	mypy $(sources)

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

.PHONY: docker-reset
docker-reset:
	scripts/reset_and_init.sh

.PHONY: docker-start
docker-start:
	docker-compose -p pah up -d

.PHONY: docker-stop
docker-stop:
	docker-compose -p pah down --remove-orphans

.PHONY: docker-start-postgres
docker-start-postgres:
	docker-compose -p pah up postgres -d

.PHONY: etlload
etlload:
	docker exec -it pah_etl poetry run loader load

.PHONY: dbt-run
dbt-run:
	docker exec -it -w /app/dbt/pah pah_etl poetry run dbt run
