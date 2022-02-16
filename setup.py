import setuptools

# Loads __version__ using exec as setup.py can't import its own package
version = {}
version_file = 'learnosity_sdk/_version.py'
exec(open(version_file).read(), { '__builtins__': None }, version)
if '__version__' not in version:
    raise Exception('__version__ not found in file %s' % version_file)

INSTALL_REQUIRES = [
    'requests >=2.21.0',
]

DEV_REQUIRES = [
    'setuptools',
    'twine',
    'wheel',
]

TEST_REQUIRES = [
    'pytest >=4.6.6',
    'pytest-cov >=2.8.1',
    'pytest-subtests',
    'responses >=0.8.1',
]

# Extract the markdown content of the README to be sent to Pypi as the project description page.
with open("README.md", "r") as f:
    readmeText = f.read()

setuptools.setup(
    author='Learnosity',
    author_email='sdk@learnosity.com',
    url='https://github.com/Learnosity/learnosity-sdk-python',
    version=version['__version__'],
    license='Apache 2.0 license. See LICENSE.md for details.',
    name='learnosity_sdk',
    description='Learnosity SDK for Python',
    long_description=readmeText, # Pulled from README.me on line 28
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(exclude=('tests')),
    install_requires=INSTALL_REQUIRES,
    extras_require={
        'dev': DEV_REQUIRES,
        'test': TEST_REQUIRES,
        'quickstart': ['jinja2'],
    },
    entry_points={
    'console_scripts': [
        'learnosity-sdk-assessment-quickstart=docs.quickstart.assessment.standalone_assessment:main [quickstart]',
    ],
    },
)
