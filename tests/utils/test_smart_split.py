import unittest
from utils import smart_split

class TestSmartSplit(unittest.TestCase):
    def test_no_quotes(self):
        self.assertEqual(smart_split("hello world"), ["hello", "world"])
        self.assertEqual(smart_split("split this string"), ["split", "this", "string"])
        self.assertEqual(smart_split("one two three"), ["one", "two", "three"])

    def test_single_quotes(self):
        self.assertEqual(smart_split("hello 'world'"), ["hello", "world"])
        self.assertEqual(smart_split("'split' this string"), ["split", "this", "string"])
        self.assertEqual(smart_split("one 'two' three"), ["one", "two", "three"])

    def test_double_quotes(self):
        self.assertEqual(smart_split('hello "world"'), ["hello", "world"])
        self.assertEqual(smart_split('"split this" string'), ["split this", "string"])
        self.assertEqual(smart_split('one "two" three'), ["one", "two", "three"])

    def test_mixed_quotes(self):
        self.assertEqual(smart_split('hello "world" and \'universe\''), ["hello", "world", "and", "universe"])
        self.assertEqual(smart_split('"split" this \'string\''), ["split", "this", "string"])
        self.assertEqual(smart_split('one "two" and \'three\''), ["one", "two", "and", "three"])

    def test_empty_string(self):
        self.assertEqual(smart_split(""), [])

    def test_whitespace_only(self):
        self.assertEqual(smart_split("   "), [])

    def test_no_quotes_include_quotes(self):
        self.assertEqual(smart_split("hello world", True), ["hello", "world"])
        self.assertEqual(smart_split("split this string", True), ["split", "this", "string"])
        self.assertEqual(smart_split("one two three", True), ["one", "two", "three"])
    
    def test_single_quotes_include_quotes(self):
        self.assertEqual(smart_split("hello 'world'", True), ["hello", "'world'"])
        self.assertEqual(smart_split("'split' this string", True), ["'split'", "this", "string"])
        self.assertEqual(smart_split("one 'two' three", True), ["one", "'two'", "three"])

    def test_double_quotes_include_quotes(self):
        self.assertEqual(smart_split('hello "world"', True), ["hello", '"world"'])
        self.assertEqual(smart_split('"split this" string', True), ['"split this"', "string"])
        self.assertEqual(smart_split('one "two" three', True), ["one", '"two"', "three"])

    def test_mixed_quotes_include_quotes(self):
        self.assertEqual(smart_split('hello "world" and \'universe\'', True), ["hello", '"world"', "and", "'universe'"])
        self.assertEqual(smart_split('"split" this \'string\'', True), ['"split"', "this", "'string'"])
        self.assertEqual(smart_split('one "two" and \'three\'', True), ["one", '"two"', "and", "'three'"])

    def test_empty_string_include_quotes(self):
        self.assertEqual(smart_split("", True), [])

    def test_whitespace_only_include_quotes(self):
        self.assertEqual(smart_split("   ", True), [])
        


if __name__ == '__main__':
    unittest.main()