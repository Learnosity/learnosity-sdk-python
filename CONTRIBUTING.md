# Contributing

Contribution in the form of [Issues] and [PRs] are welcome.

# Tests

To run the tests, run `tox` from the project directory. This will run tests several different versions of python.

If you don't have `tox` installed, run:

    pip install tox

This assumes that you have `pyenv` or a similar tool set up to provide python binaries for 2.7, 3.3, 3.4, 3.5 and 3.6.

Alternatively, if you only care about the version you're currently running, you can just:

    pip install -r requirements-dev.txt
    python setup.py test

# Deploying to PyPi

Run `make release` and follow the instructions to deploy the distributions to PyPi

You will need to be set up as a maintainer in order to do this.