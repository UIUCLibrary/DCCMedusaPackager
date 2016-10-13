.PHONY: docs tox-test
PYTHON=python
PIP=pip
TOX=tox


test:
	$(PYTHON) setup.py test

install-tox:
	$(PIP) install -q tox

install-sphinx:
	@echo 'Installing Sphinx'
	@$(PIP) install -q sphinx

install:
	@$(PYTHON) setup.py install

docs: install-sphinx
	@echo 'Creating Sphinx documentation'

tox-test: install-tox
	@echo 'Running tox tests'
	@$(TOX)
