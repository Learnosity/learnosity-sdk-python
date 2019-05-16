try: # for pip >= 10
       from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
       from pip.req import parse_requirements
import setuptools

# Loads __version__ using exec as setup.py can't import its own package
version = {}
version_file = 'learnosity_sdk/_version.py'
exec(open(version_file).read(), { '__builtins__': None }, version)
if '__version__' not in version:
    raise Exception('__version__ not found in file %s' % version_file)

def test_reqs():
    reqs = parse_requirements('requirements-dev.txt', session=False)
    reqs = [str(ir.req) for ir in reqs]

    return reqs


setuptools.setup(
    author='Learnosity',
    author_email='sdk@learnosity.com',
    url='https://github.com/Learnosity/learnosity-sdk-python',
    version=version['__version__'],
    name='learnosity_sdk',
    description='Learnosity SDK for Python',

    packages=setuptools.find_packages(exclude=('tests')),

    install_requires=[
        'requests>=2.21.0',
        'urllib3>=1.24.3',
    ],
    tests_require=test_reqs(),
)
