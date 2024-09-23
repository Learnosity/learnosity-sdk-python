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

1. Add a new entry to the [Changelog.md](./ChangeLog.md)
1. Merge your pull request after approval.
2. Create a new Release[https://github.com/Learnosity/learnosity-sdk-python/releases] with a new tag, and this tag will
be used as the new library version. Please autogenerate release notes to show differences.

[Issues]: https://github.com/Learnosity/learnosity-sdk-python/issues/new
[PRs]: https://github.com/Learnosity/learnosity-sdk-python/compare