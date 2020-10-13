#!/usr/bin/env python

import setuptools

# Loads __version__ using exec as setup.py can't import its own package
version = {}
version_file = 'learnosity_sdk/_version.py'
exec(open(version_file).read(), {'__builtins__': None}, version)
if '__version__' not in version:
    raise Exception('__version__ not found in file %s' % version_file)


INSTALL_REQUIRES = [
    'click>=7',
    'requests >=2.21.0',

    # lrn-cli-only requirements
    'pygments >= 2',
]

DEV_REQUIRES = [
    'setuptools',
    'tox',
    'twine',
    'wheel',
]

TEST_REQUIRES = [
    'pytest >=4.6.6, <6.0',
    'pytest-cov >=2.8.1, <3.0',
    'responses >=0.8.1, <1.0',
]


setuptools.setup(
    author='Learnosity',
    author_email='sdk@learnosity.com',
    url='https://github.com/Learnosity/learnosity-sdk-python',
    version=version['__version__'],
    name='learnosity_sdk',
    description='Learnosity SDK for Python',

    packages=setuptools.find_packages(exclude=('tests')),

    entry_points={
        'console_scripts': [
            'lrn-cli = learnosity_sdk.scripts.lrn_cli:cli',
        ],
    },

    install_requires=INSTALL_REQUIRES,
    extras_require={
        'dev': DEV_REQUIRES,
        'test': TEST_REQUIRES,
    },
)
