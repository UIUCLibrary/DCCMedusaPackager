PYTHON      = python
PIP         = pip
TOX         = tox
current_dir = $(shell pwd)
MANPATH     = $(HOME)/.local/share/man
DOC_BUILD   = $(current_dir)/docs/build

.PHONY: docs tox-test

all:
	@echo "DCC Packager"
	@$(PYTHON) setup.py build

test:
	$(PYTHON) setup.py test

install-tox:
	$(PIP) install -q tox

install-sphinx:
	@echo 'Installing Sphinx'
	@$(PIP) install -q sphinx

install: docs
	@echo "Installing DCC Packager."
	@$(PYTHON) setup.py install
docs: install-sphinx
	@echo 'Creating Sphinx documentation'
	make html -C ./docs -e BUILDDIR=$(DOC_BUILD)

tox-test: install-tox
	@echo 'Running tox tests'
	@$(TOX)

clean:
	@if [ -d docs/build ]; then \
	    echo 'Deleting generated documentation'; \
		rm -R docs/build; \
    fi


	@if [ -d build ]; then \
	    echo 'Deleting build.'; \
    	rm -R build; \
    fi


	@if [ -d dist ]; then \
		echo 'Deleting dist.'; \
		rm -R dist; \
	fi

	@if [ -d .tox ]; then \
		echo 'Deleting tox cache.'; \
		rm -R .tox; \
	fi
	@if [ -d .cache ]; then \
		rm -R .cache; \
	fi

uninstall:
	@echo 'Uninstalling DCC Medusa Packager'
	@$(PIP) uninstall DCCMedusaPackager -y