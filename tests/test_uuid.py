import unittest
import re
from learnosity_sdk.utils import Uuid

class TestUuid(unittest.TestCase):
    def test_generate(self):
        """
        Tests correctness of the generate() method in Uuid.
        """

        generated = Uuid.generate()
        prog = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        result = prog.match(generated)

        assert result != None
        assert result.group() == generated
