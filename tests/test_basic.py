import unittest


class TestBasic(unittest.TestCase):
    def test_simple_sum(self):
        self.assertEqual(2 + 2, 4)

    def test_string_upper(self):
        self.assertEqual("telegram".upper(), "TELEGRAM")

    def test_boolean_truth(self):
        self.assertTrue(10 > 1)
