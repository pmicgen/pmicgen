import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import genutils

class TestLDOSpecToParam(unittest.TestCase):
    def test_foo(self):
        converter = LDOSpecToParam("""specs""")
        converter.generate()

if __name__ == "__main__":
    unittest.main()
