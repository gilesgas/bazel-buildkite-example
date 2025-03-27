import unittest
from main import hi_there

class TestMain(unittest.TestCase):
    def test_generate_pipeline(self):
        self.assertEqual(hi_there(), "Hey! There's a message from the Python library: 'Hello, world!'")
