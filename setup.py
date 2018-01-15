import pip.req
import setuptools

VERSION = '0.1.0'


def test_reqs():
    reqs = pip.req.parse_requirements('requirements-dev.txt', session=False)
    reqs = [str(ir.req) for ir in reqs]

    return reqs


setuptools.setup(
    author='Cera Davies',
    author_email='cera.davies@learnosity.com',
    url='https://github.com/Learnosity/learnosity-sdk-python',
    version=VERSION,
    name='learnosity_sdk',
    description='Learnosity SDK for Python',

    packages=setuptools.find_packages(exclude=('tests')),

    install_requires=[
        'requests>=2'
    ],
    tests_require=test_reqs(),
)
