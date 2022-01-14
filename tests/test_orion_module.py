import unittest
import orionapi as orion
import vcr


class TestBasics(unittest.TestCase):
    def test_version(self):
        assert orion.__version__ == '0.1.3'
  
    def test_class(self):
        assert issubclass(orion.OrionAPI().__class__,object) 

    @vcr.use_cassette()
    def test_good_login(self):
        pass


if __name__ == '__main__':
    unittest.main()