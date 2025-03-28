.PHONY: test build dev publish
LANGUAGES:=`find conjunto/locale/ -mindepth 1 -maxdepth 1 -type d -printf "--locale %f "`
PYTHON = /usr/bin/env python
MANAGE = cd src && django-admin


dev:
	$(PYTHON) -m pip install -e ".[dev]"

all: init locale staticfiles
production: localecompile staticfiles

jsi18n: # TODO
	$(MANAGE) compilejsi18n

localecompile:
	$(MANAGE) compilemessages

setup:
	$(PYTHON) -m pip install .

localegen:
    # don't --keep-pot
	$(MANAGE) makemessages --ignore "static/*" --ignore "medux/static/*" --ignore "build/*" $(LANGUAGES)
	$(MANAGE) makemessages -d djangojs --ignore "static/*" --ignore "medux/static/*" --ignore "build/*" $(LANGUAGES)

staticfiles: jsi18n
	$(MANAGE) collectstatic --noinput


locale: localegen localecompile


test:
	$(PYTHON) -m pytest

coverage:
	coverage run -m pytest

#check:
#	ruff check .
#
doc:
	mkdocs build -d build/doc/

livedocs:
	mkdocs serve

clean:
	rm -rf dist/* build/*

build: clean
	$(PYTHON) -m build

publish: build
	$(PYTHON) -m twine upload dist/*
