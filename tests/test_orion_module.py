import unittest
import orionapi as orion
import vcr


class TestBasics(unittest.TestCase):
    def test_class(self):
        assert issubclass(orion.OrionAPI().__class__,object) 

    @vcr.use_cassette()
    def test_good_login(self):
        pass

# build out proper tests and see how vcr works with Orion

if __name__ == '__main__':
    unittest.main()