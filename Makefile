.PHONY: test build dev publish
LANGUAGES:=`find conjunto/locale/ -mindepth 1 -maxdepth 1 -type d -printf "--locale %f "`
PYTHON = /usr/bin/env python

dev:
	$(PYTHON) -m pip install -e ".[dev]"

all: init locale staticfiles
production: localecompile staticfiles

setup:
	$(PYTHON) -m pip install .

test:
	$(PYTHON) -m pytest

coverage:
	coverage run -m pytest

#check:
#	ruff check .
#
docs-build:
	mkdocs build

docs-live:
	mkdocs serve

clean:
	rm -rf dist/* build/*

build: clean
	$(PYTHON) -m build

publish: build
	$(PYTHON) -m twine upload dist/*
