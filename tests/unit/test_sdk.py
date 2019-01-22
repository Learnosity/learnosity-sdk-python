import collections
import unittest

SdkTestSpec = collections.namedtuple(
    "TestSpec", ["import_line", "object"])

SdkImportTests = [
    SdkTestSpec(
        "import learnosity_sdk", "learnosity_sdk.request.Init"
    ),
    SdkTestSpec(
        "from learnosity_sdk import *", "request.Init"
    ),
    SdkTestSpec(
        "import learnosity_sdk.request", "learnosity_sdk.request.Init"
    ),
]

SdkModuleTests = [
    SdkTestSpec(
        "from learnosity_sdk import *", "exceptions"
    ),
    SdkTestSpec(
        "from learnosity_sdk.exceptions import *", "ValidationException"
    ),
    SdkTestSpec(
        "from learnosity_sdk.exceptions import *", "DataApiException"
    ),
    SdkTestSpec(
        "from learnosity_sdk.request import *", "Init"
    ),
    SdkTestSpec(
        "from learnosity_sdk.request import *", "DataApi"
    ),
]

def _run_test(t):
    globals = {}
    locals = {}
    exec(t.import_line, globals, locals)
    eval(t.object, globals, locals)

class TestSdkImport(unittest.TestCase):
    """
    Tests importing the SDK
    """

    def test_sdk_imports(self):
        for t in SdkImportTests:
            _run_test(t)

class TestSdkImport(unittest.TestCase):
    """
    Tests importing the modules
    """

    def test_sdk_imports(self):
        for t in SdkModuleTests:
            _run_test(t)
