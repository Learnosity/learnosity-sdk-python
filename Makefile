PYTHON=python3
VENV=.venv
VENVPATH=$(VENV)/$(shell uname)-$(shell uname -m)-sdk-python

define venv-activate
	. $(VENVPATH)/bin/activate; \
	unset PYTHONPATH
endef

build: venv
	$(call venv-activate); \
		pip wheel .
devbuild: pip-requirements-dev build
prodbuild: build

test-unit: venv pip-requirements-dev
	$(call venv-activate); \
		$(PYTHON) setup.py test

test-integration-dev: venv pip-tox
	$(call venv-activate); \
		tox

build-clean: real-clean

clean:
	find . -path __pycache__ -delete
	test ! -d $(VENVPATH) || rm -r $(VENVPATH)
	test ! -d .tox || rm -r .tox
real-clean: clean
	test ! -d $(VENV) || rm -r $(VENV)
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
