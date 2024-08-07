DOCKER := $(if $(LRN_SDK_NO_DOCKER),,$(shell which docker))
PYTHON_VERSION = 3.9

TARGETS = build build-clean devbuild prodbuild \
	dist dist-check-version dist-upload dist-upload-twine release \
	pip-requirements-dev pip-requirements-test venv \
	test test-clean test-integration-dev test-integration-env test-unit \
	clean distclean real-clean
.PHONY: $(TARGETS)

ifneq (,$(DOCKER))
# Re-run the make command in a container
DKR = docker container run -it --rm \
		-v $(CURDIR):/srv/sdk/python \
		-v lrn-sdk-python_cache:/root/.cache \
		-w /srv/sdk/python \
		-e LRN_SDK_NO_DOCKER=1 \
		-e ENV -e REGION -e VER \
		-e GIT_AUTHOR_EMAIL=licenses@learnosity.com \
		-e GIT_AUTHOR_NAME=learnosity \
		-e GIT_COMMITTER_EMAIL=licenses@learnosity.com \
		-e GIT_COMMITTER_NAME=learnosity \
		python:$(PYTHON_VERSION)

$(TARGETS):
	$(DKR) make -e MAKEFLAGS="$(MAKEFLAGS)" $@

else
# The primary make targets
PYTHON=python3
VENV=.venv
VENVPATH=$(VENV)/$(shell uname)-$(shell uname -m)-sdk-python
VIRTUALENV = $(PYTHON) -m venv

ENV=prod
REGION=.learnosity.com
# Data API
VER=v1

define venv-activate
	. $(VENVPATH)/bin/activate
endef

devbuild: build
prodbuild: dist-check-version build
build: venv pip-requirements-dev
	$(call venv-activate); \
		$(PYTHON) setup.py sdist

release:
	@./release.sh
	@echo '*** You can now use \`make dist-upload\` to publish the new version to PyPI'

test: test-unit test-integration-dev test-integration-env
test-unit: venv pip-requirements-test
	$(call venv-activate); \
		pytest --pyargs tests.unit

test-integration-env: venv pip-requirements-test
	$(call venv-activate); \
		ENV=$(ENV) \
		pytest  --pyargs tests.integration

test-integration-dev: venv pip-requirements-dev pip-requirements-test
	$(call venv-activate); \
		pytest --cov=learnosity_sdk

build-clean: real-clean

dist: distclean venv pip-requirements-dev
	$(call venv-activate); \
		$(PYTHON) setup.py sdist; \
		$(PYTHON) setup.py bdist_wheel --universal
dist-upload: dist-check-version clean test dist-upload-twine
dist-check-version: PKG_VER=$(shell sed -n "s/^.*__version__\s*=\s*'\([^']\+\)'.*$$/\1/p" learnosity_sdk/_version.py)
dist-check-version: GIT_TAG=$(shell git describe --tags)
dist-check-version:
ifeq ($(shell echo $(GIT_TAG) | grep -qw "$(PKG_VER)"; echo $$?),1)
	$(error Version number $(PKG_VER) in learnosity_sdk/_version.py does not match git tag $(GIT_TAG))
endif
dist-upload-twine: venv pip-requirements-dev dist # This target doesn't do any safety check!
	$(call venv-activate); \
		twine upload dist/*

clean: test-clean distclean
	test ! -d build || rm -r build
	find . -path __pycache__ -delete
	find . -name *.pyc -delete
test-clean:
	test ! -d .tox || rm -r .tox
	test ! -d .pytest_cache || rm -r .pytest_cache
	test ! -f .coverage || rm .coverage
distclean:
	test ! -d dist || rm -r dist
real-clean: clean
	test ! -d $(VENV) || rm -r $(VENV)
	test ! -d learnosity_sdk.egg-info || rm -r learnosity_sdk.egg-info

# Python environment and dependencies
venv: $(VENVPATH)
$(VENVPATH):
	$(VIRTUALENV) $(VENVPATH)
	$(call venv-activate); \
		pip install -e .

pip-requirements-dev:
	$(call venv-activate); \
		pip install -e ".[dev]"

pip-requirements-test:
	$(call venv-activate); \
		pip install -e ".[test]"

endif
.PHONY: dist venv pip-requirements-dev pip-requirements-test
