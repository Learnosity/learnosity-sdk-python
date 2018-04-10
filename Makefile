PYTHON=python3
VENV=.venv
VENVPATH=$(VENV)/$(shell uname)-$(shell uname -m)-sdk-python

define venv-activate
	. $(VENVPATH)/bin/activate; \
	unset PYTHONPATH
endef

build:
	$(error build not implemented)
devbuild: pip-requirements-dev build
prodbuild: build

test-unit: venv pip-requirements-dev
	$(call venv-activate); \
		$(PYTHON) setup.py test

test-integration-python: venv pip-tox
	$(call venv-activate); \
		tox

build-clean: clean
	test ! -d learnosity_sdk.egg-info/ || rm -r learnosity_sdk.egg-info/

clean:
	find . -name __pycache__ -delete
	test ! -d $(VENVPATH) || rm -r $(VENVPATH)
	test ! -d .tox || rm -r .tox
real-clean:
	test ! -d $(VENV) || rm -r $(VENV)

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
