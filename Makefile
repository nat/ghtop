.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard ./*.ipynb)

all:
	echo not using nbdev at the moment

ghtop: $(SRC)
	nbdev_build_lib
	touch ghtop

sync:
	nbdev_update_lib

docs_serve: docs
	cd docs && JEKYLL_ENV=production bundle exec jekyll serve

docs: $(SRC)
	nbdev_build_docs
	touch docs

release: pypi conda_release
	nbdev_bump_version

conda_release:
	fastrelease_conda_package

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist
