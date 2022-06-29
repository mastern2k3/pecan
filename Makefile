DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


test:
	pytest


lint-check:
	black --check .
	isort --check .


lint:
	black .
	isort .


publish:
	poetry publish --build


# docs-serve:
# 	mkdocs serve
