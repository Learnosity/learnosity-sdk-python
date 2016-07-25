import setuptools

VERSION = '0.0.5'

setup = dict(
    author='Cera Davies',
    author_email='cera.davies@learnosity.com',
    url='https://github.com/Learnosity/learnosity-sdk-python',
    version=VERSION,
    name='learnosity_sdk',
    description='Learnosity SDK for Python',
    packages=setuptools.find_packages(exclude=('tests')),
    test_suite='learnosity_sdk.tests'
)

setuptools.setup(**setup)
