PYTHON=python3
VENV=.venv
VENVPATH=$(VENV)/$(shell uname)-$(shell uname -m)-sdk-python

ENV=prod
REGION=.learnosity.com
# Data API
VER=v1

define venv-activate
	. $(VENVPATH)/bin/activate; \
	unset PYTHONPATH
endef

prodbuild: dist-check-version build
devbuild: build
build: venv
	$(call venv-activate); \
		$(PYTHON) setup.py sdist

release:
	@./release.sh
	@echo '*** You can now use \`make dist-upload\` to publish the new version to PyPI'

freeze-deps:
	$(call venv-activate); \
               $(PYTHON) -m pip freeze | grep -v learnosity_sdk > requirements.txt

test: test-unit test-integration-dev dist-check-version
test-unit: venv pip-requirements-dev
	$(call venv-activate); \
		$(PYTHON) setup.py test  --addopts '--pyargs tests.unit'

test-integration-env: venv pip-requirements-dev
	$(call venv-activate); \
		ENV=$(ENV) \
		$(PYTHON) setup.py test  --addopts '--pyargs tests.integration'

test-integration-dev: venv pip-tox
	$(call venv-activate); \
		tox

build-clean: real-clean

dist: distclean
	$(call venv-activate); \
		$(PYTHON) setup.py sdist; \
		$(PYTHON) setup.py bdist_wheel --universal
dist-upload: dist-check-version clean test dist-upload-twine
dist-check-version: PKG_VER=v$(shell sed -n "s/^.*VERSION\s\+=\s\+'\([^']\+\)'.*$$/\1/p" setup.py)
dist-check-version: GIT_TAG=$(shell git describe --tags)
dist-check-version:
ifeq ('$(shell echo $(GIT_TAG) | grep -qw "$(PKG_VER)")', '')
	$(error Version number $(PKG_VER) in setup.py does not match git tag $(GIT_TAG))
endif
dist-upload-twine: pip-requirements-dev dist # This target doesn't do any safety check!
	$(call venv-activate); \
		twine upload dist/*

clean: test-clean distclean
	test ! -d build || rm -r build
	find . -path __pycache__ -delete
	find . -name *.pyc -delete
test-clean:
	test ! -d .tox || rm -r .tox
distclean:
	test ! -d dist || rm -r dist
real-clean: clean
	test ! -d $(VENV) || rm -r $(VENV)
	test ! -d learnosity_sdk.egg-info || rm -r learnosity_sdk.egg-info

# Python environment and dependencies
venv: $(VENVPATH)
$(VENVPATH):
	unset PYTHONPATH; virtualenv -p$(PYTHON) $(VENVPATH)
	$(call venv-activate); \
		pip install -e .

pip-requirements-dev: venv
	$(call venv-activate); \
		pip install -r requirements-dev.txt

pip-tox: venv
	$(call venv-activate); \
		pip install tox

.PHONY: dist
