import unittest
from tests.utils import test_is_number, test_smart_split


def main() -> None:
    testLoader = unittest.TestLoader()
    tests = testLoader.loadTestsFromModule(test_is_number)
    tests = testLoader.loadTestsFromModule(test_smart_split)
    testRunner = unittest.TextTestRunner()
    testRunner.run(tests)


if __name__ == '__main__':
    main()
