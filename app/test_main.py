import unittest
from main import get_greeting

class TestMain(unittest.TestCase):
    def test_generate_pipeline(self):
        self.assertEqual(get_greeting(), "The Python library says: 'Hello, world!'")
