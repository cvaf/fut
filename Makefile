setup:
	pip install poetry
	poetry install
	poetry run pre-commit install

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f coverage.*

clean:	clean-pyc clean-test

test:  clean
	poetry run pytest

mypy:
	poetry run mypy fut

check: test mypy
