import setuptools

VERSION = '0.0.2'

setup = dict(
    author='Daniel Bryan',
    author_email='daniel.bryan@learnosity.com',
    url='https://github.com/Learnosity/learnosity-sdk-python',
    version=VERSION,
    name='learnosity_sdk',
    description='Learnosity SDK for Python',
    packages=[
        'learnosity_sdk',
        'learnosity_sdk.tests'
    ],

    test_suite='learnosity_sdk.tests'
)

setuptools.setup(**setup)
