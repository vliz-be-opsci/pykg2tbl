PYTHON = python
TEST_PATH = ./tests/
FLAKE8_EXCLUDE = venv,.venv,.eggs,.tox,.git,__pycache__,*.pyc
SHELL := /bin/bash

clean:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force {} +
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -f *.sqlite
	@rm -rf .cache

init:
	pip install --upgrade pip
	which poetry >/dev/null || pip install poetry
	poetry install
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg

init-dev: init
	poetry install --extras 'dev'

docu:
	poetry run sphinx-build -b html docs/source/ docs/build/html

test:
	poetry run pytest ${TEST_PATH}

check:
	poetry run black --check --diff .
	poetry run isort --check --diff .
	poetry run flake8 . --exclude ${FLAKE8_EXCLUDE}

lint_fix:
	poetry run black .
	poetry run isort .

install:
	poetry install

docker-build:
	docker build . -t pykg2tbl

build: init-dev check test docu
	poetry build

update:
	poetry update
	poetry run -m pre-commit autoupdate

release: build update
	poetry run release

build-poetry-reqs:
	cat requirements.txt | grep -E '^[^# ]' | cut -d= -f1 | xargs -n 1 poetry add 
	cat requirements-dev.txt | grep -E '^[^# ]' | cut -d= -f1 | xargs -n 1 poetry add --group dev --extras dev
	poetry update
