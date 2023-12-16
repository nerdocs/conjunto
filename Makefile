.PHONY: test build dev publish
LANGUAGES:=`find medux/locale/ -mindepth 1 -maxdepth 1 -type d -printf "--locale %f "`
PYTHON = $(VENV)/bin/python3
MANAGE = cd src && python ./manage.py


dev:
	python -m pip install --editable ".[dev]"

publish: build
	flit publish

all: init locale staticfiles
production: localecompile staticfiles

localecompile:
	$(MANAGE) compilemessages

setup:
	python -m pip install .

localegen:
    # don't --keep-pot
	$(MANAGE) makemessages --ignore "static/*" --ignore "medux/static/*" --ignore "build/*" $(LANGUAGES)
	$(MANAGE) makemessages -d djangojs --ignore "static/*" --ignore "medux/static/*" --ignore "build/*" $(LANGUAGES)

staticfiles: jsi18n
	$(MANAGE) collectstatic --noinput

jsi18n:
	$(MANAGE) compilejsi18n

locale: jsi18n localegen localecompile


test:
	pytest

coverage:
	coverage run -m pytest

#check:
#	ruff check .
#
#doc:
#	mkdocs build -d build/doc/

build:
	flit build

publish:
	flit publish