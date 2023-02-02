import unittest


class MyTestCase(unittest.TestCase):
    def test_one_plus_one_should_be_two(self):
        self.assertEqual(1 + 1, 2)


if __name__ == '__main__':
    unittest.main()
