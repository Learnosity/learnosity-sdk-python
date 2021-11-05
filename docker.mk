PYTHON_VERSION = 3.9
PWD = $(shell pwd -P)
DKR = docker container run -t --rm \
		-v $(PWD):/srv/sdk/python \
		-v lrn-sdk-python_cache:/root/.cache:z,delegated \
		-w /srv/sdk/python \
		-e PYTHON_VERSION=$(PYTHON_VERSION) \
		-e ENV -e REGION -e VER \
		python:$(PYTHON_VERSION)

%:
	$(DKR) make -e $@
