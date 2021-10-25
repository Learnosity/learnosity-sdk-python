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




TO BE UPDATED FULLY BELOW THIS LINE \/
=========================================



## Development

You can ask [Composer] to download the latest sources

    composer create-project --prefer-source learnosity/learnosity-sdk-php

or get it manually with Git.

    git clone git@github.com:Learnosity/learnosity-sdk-php.git

If you don't have an SSH key loaded into github you can clone via HTTPS (not recommended)

    git clone https://github.com/Learnosity/learnosity-sdk-php.git

In the second case, you'll need to install the dependencies afterwards.

    composer install

## Tests

Test can be run from a development checkout with

     ./vendor/bin/phpunit

[Issues]: https://github.com/Learnosity/learnosity-sdk-php/issues/new
[PRs]: https://github.com/Learnosity/learnosity-sdk-php/compare
[Composer]: https://getcomposer.org/

## Creating a new release

Run `make release`.

This requires GNU-flavoured UNIX tools (particularly `gsed`). If those are not the default on your system, you'll need to install them, e.g. for OS X,

    brew install gsed coreutils