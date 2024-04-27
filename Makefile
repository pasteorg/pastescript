# simple Makefile for some common tasks
.PHONY: clean test dist release pypi tagv

pastescript-version := $(shell python setup.py --version)

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -rf .tox || true
	rm -r cover .coverage || true
	rm -r .eggs || true
	rm -r pastescript.egg-info || true

tagv:
	git tag -s -m ${pastescript-version} ${pastescript-version}
	git push origin master --tags

cleanagain:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r .tox || true
	rm -r cover .coverage || true
	rm -r .eggs || true
	rm -r pastescript.egg-info || true

test:
	tox --skip-missing-interpreters

dist: test
	python3 setup.py sdist bdist_wheel

release: clean test cleanagain tagv pypi gh

pypi:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

gh:
	gh release create ${pastescript-version} --generate-notes dist/*
