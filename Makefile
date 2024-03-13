.PHONY: test build dev publish
LANGUAGES:=`find conjunto/locale/ -mindepth 1 -maxdepth 1 -type d -printf "--locale %f "`
PYTHON = $(VIRTUAL_ENV)/bin/python3
MANAGE = cd src && django-admin


dev:
	$(PYTHON) -m pip install -e ".[dev]"

all: init locale staticfiles
production: localecompile staticfiles

localecompile:
	$(MANAGE) compilemessages

setup:
	$(PYTHON) -m pip install .

localegen:
    # don't --keep-pot
	$(MANAGE) makemessages --ignore "static/*" --ignore "medux/static/*" --ignore "build/*" $(LANGUAGES)
	$(MANAGE)  makemessages -d djangojs --ignore "static/*" --ignore "medux/static/*" --ignore "build/*" $(LANGUAGES)

staticfiles: jsi18n
	$(MANAGE) collectstatic --noinput

jsi18n: # TODO
	$(MANAGE) compilejsi18n

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
