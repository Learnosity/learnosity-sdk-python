# Contributing

Contribution in the form of [PRs] are welcome.

#Why We Are No Longer Accepting Public Issues
After careful consideration, we’ve decided to discontinue accepting issues via GitHub Issues for our public repositories.

Here’s why:

We have established support channels specifically designed to handle customer inquiries and issues. These channels are staffed 24/7, and we work diligently to ensure prompt responses and high-quality support. Maintaining and responding to GitHub Issues requires significant resources, and we are unable to provide the same level of support through this channel as we do through our dedicated support teams. By focusing on our dedicated support channels, we can streamline our processes and offer a more effective and responsive service to our users.

For any issues or support needs, please use the existing support channels. This will help us provide you with the best possible assistance in a timely manner.

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
