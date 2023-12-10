.PHONY: test build dev publish

test:
	pytest

build:
	flit build

dev:
	python -m pip install --editable .

publish: build
	flit publish
