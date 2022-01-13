import unittest
import orion_module as orion


class TestBasics(unittest.TestCase):
    def test_version(self):
        assert orion.__version__ == '0.1.0'

    def test_class(self):
        assert issubclass(orion.OrionAPI().__class__,object) 


if __name__ == '__main__':
    unittest.main()