PYTHON      ?= python
PIP         ?= pip
TOX         ?= tox
current_dir = $(shell pwd)
MANPATH     = $(HOME)/.local/share/man
DOC_BUILD   = $(current_dir)/docs/build
DOCKER=docker
DOCKER_IMAGE=medusapackager
DOCKER_RUN_ARGS='-e JAVA_OPTS="-Xms 256m -Dorg.jenkinsci.plugins.durabletask.BourneShellScript.LAUNCH_DIAGNOSTICS=true" --rm'
JOB_NAME=medusapackager
JENKINS_UC_DOWNLOAD=https://ftp-nyc.osuosl.org/pub/jenkins/
JENKINS_DOCKERFILE=ci/jenkins/jenkinsfile-runner/Dockerfile

.PHONY: docs tox-test

all:
	@echo "DCC Packager"
	@$(PYTHON) setup.py build

test:
	$(PYTHON) setup.py test

install-tox:
	@$(PIP) install -q tox

install-sphinx:
	@echo 'installing Sphinx'
	@$(PIP) install -q sphinx

install: docs
	@echo "installing DCC Packager"
	@$(PYTHON) setup.py install
docs: install-sphinx
	@echo 'creating Sphinx documentation'
	@$(PYTHON) setup.py build_sphinx
tox-test: install-tox
	@echo 'running tox tests'
	@$(TOX)

.jenkinsci: $(JENKINS_DOCKERFILE) ci/jenkins/jenkinsfile-runner/plugins.yaml
	@USER_ID=$(shell id -u) ; \
	GROUP_ID=$(shell id -g) ;\
	echo "using $$USER_ID:$$GROUP_ID" ; \
	$(DOCKER) build -f $(JENKINS_DOCKERFILE) --build-arg USER_ID --build-arg GROUP_ID --build-arg JENKINS_UC_DOWNLOAD=$(JENKINS_UC_DOWNLOAD) --progress plain -t $(DOCKER_IMAGE) --iidfile .jenkinsci .

.PHONY: jenkinsci
jenkinsci: .jenkinsci
	@echo "Starting Jenkinsfile Runner"
	@ID=$(shell $(DOCKER) run $(DOCKER_RUN_ARGS) \
			-v ${PWD}/ci/:/workspace/ci/ \
			-v ${PWD}/docs/:/workspace/docs/ \
			-v ${PWD}/MedusaPackager/:/workspace/MedusaPackager/ \
			-v ${PWD}/tests/:/workspace/tests/ \
			-v ${PWD}/cx_setup.py:/workspace/cx_setup.py \
			-v ${PWD}/deployment.yml:/workspace/deployment.yml \
			-v ${PWD}/documentation.url:/workspace/documentation.url \
			-v ${PWD}/Jenkinsfile:/workspace/Jenkinsfile \
			-v ${PWD}/make.bat:/workspace/make.bat \
			-v ${PWD}/Makefile:/workspace/Makefile \
			-v ${PWD}/MANIFEST.in:/workspace/MANIFEST.in \
			-v ${PWD}/README.rst:/workspace/README.rst \
			-v ${PWD}/requirements.txt:/workspace/requirements.txt \
			-v ${PWD}/requirements-dev.txt:/workspace/requirements-dev.txt \
			-v ${PWD}/requirements-freeze.txt:/workspace/requirements-freeze.txt \
			-v ${PWD}/setup.cfg:/workspace/setup.cfg \
			-v ${PWD}/setup.py:/workspace/setup.py \
			-v ${PWD}/tox.ini:/workspace/tox.ini \
			-v ${PWD}/ci/jenkins/jenkinsfile-runner/casc/:/usr/share/jenkins/ref/casc/ \
			-v /var/run/docker.sock:/var/run/docker.sock \
		-t -d $(DOCKER_IMAGE) \
		--job-name $(JOB_NAME)) ;\
	echo "Attaching to Docker container $$ID" ; \
	$(DOCKER) attach --no-stdin $$ID ; \
	echo "\nStopping $$ID" ; \
	$(DOCKER) stop $$ID


clean:
	@if [ -f ".jenkinsci" ]; then \
		sed 's/sha256://' .jenkinsci | xargs docker rmi ; \
		rm -f .jenkinsci ; \
	fi

	@$(PYTHON) setup.py clean

	@if [ -d docs/build ]; then \
	    echo 'deleting generated documentation'; \
		rm -R docs/build; \
    fi


	@if [ -d build ]; then \
	    echo 'deleting build'; \
    	rm -R build; \
    fi


	@if [ -d dist ]; then \
		echo 'deleting dist'; \
		rm -R dist; \
	fi

	@if [ -d .tox ]; then \
		echo 'deleting tox cache'; \
		rm -R .tox; \
	fi
	@if [ -d .cache ]; then \
		rm -R .cache; \
	fi

	@if [ -d DCCMedusaPackager.egg-info ]; then \
		echo 'Deleting DCCMedusaPackager.egg-info.'; \
		rm -R DCCMedusaPackager.egg-info; \
	fi


uninstall:
	@echo 'Uninstalling DCC Medusa Packager'
	@$(PIP) uninstall DCCMedusaPackager -y