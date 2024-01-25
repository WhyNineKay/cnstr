import unittest
from src.utils import is_number

class TestIsNumber(unittest.TestCase):
    def test_valid_numbers(self):
        self.assertTrue(is_number("123"))
        self.assertTrue(is_number("3.14"))
        self.assertTrue(is_number("-5"))
        self.assertTrue(is_number("0"))
        self.assertTrue(is_number("1e3"))
        self.assertTrue(is_number("1E-5"))

    def test_invalid_numbers(self):
        self.assertFalse(is_number("abc"))
        self.assertFalse(is_number("1.2.3"))
        self.assertFalse(is_number("1,000"))
        self.assertFalse(is_number("1e-"))
        self.assertFalse(is_number("1E+"))
        self.assertFalse(is_number("infinity"))
        self.assertFalse(is_number("-infinity"))
        self.assertFalse(is_number("nan"))

if __name__ == '__main__':
    unittest.main()