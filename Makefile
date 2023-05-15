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
	pip install poetry
	poetry install

init-dev: init
	poetry install --extras 'dev'

docu:
	@${PYTHON} setup.py build_sphinx

test:
	@${PYTHON} -m pytest ${TEST_PATH}

check:
	@${PYTHON} -m black --check --diff .
	@${PYTHON} -m isort --check --diff .
	@${PYTHON} -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude ${FLAKE8_EXCLUDE}
	@${PYTHON} -m flake8 . --count --exit-zero --statistics --exclude ${FLAKE8_EXCLUDE}

install:
	@${PYTHON} poetry install

docker-build:
	@docker build . -t pykg2tbl

build: init-dev check test docu
	@${PYTHON} -m build

release: build
	@${PYTHON} setup.py release

build-poetry-reqs:
	cat requirements.txt | grep -E '^[^# ]' | cut -d= -f1 | xargs -n 1 poetry add 
	cat requirements-dev.txt | grep -E '^[^# ]' | cut -d= -f1 | xargs -n 1 poetry add --group dev --extras dev
