PYTHON=python3
VENV=.venv
VENVPATH=$(VENV)/$(shell uname)-$(shell uname -m)-sdk-python

PKG_VER=$(shell sed -n "s/^.*VERSION\s\+=\s\+'\([^']\+\)'.*$$/\1/p" setup.py)

define venv-activate
	. $(VENVPATH)/bin/activate; \
	unset PYTHONPATH
endef

prodbuild: test-version build
devbuild: build
build: venv
	$(call venv-activate); \
		$(PYTHON) setup.py sdist

test-unit: venv pip-requirements-dev
	$(call venv-activate); \
		$(PYTHON) setup.py test

test-integration-dev: venv pip-tox
	$(call venv-activate); \
		tox

test-version:
	git describe --tags | grep -q $(PKG_VER) || (echo Version number $(PKG_VER) in setup.py does not match git tag; false)


build-clean: real-clean

clean:
	find . -path __pycache__ -delete
	test ! -d $(VENVPATH) || rm -r $(VENVPATH)
	test ! -d .tox || rm -r .tox
real-clean: clean
	test ! -d $(VENV) || rm -r $(VENV)
	test ! -d dist || rm -r dist
	test ! -d learnosity_sdk.egg-info/ || rm -r learnosity_sdk.egg-info/

# Python environment and dependencies
venv: $(VENVPATH)
$(VENVPATH):
	virtualenv -p$(PYTHON) $(VENVPATH)
	$(call venv-activate); \
		pip install -e .

pip-requirements-dev: venv
	$(call venv-activate); \
		pip install -r requirements-dev.txt

pip-tox: venv
	$(call venv-activate); \
		pip install tox
