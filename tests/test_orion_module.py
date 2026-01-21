import unittest

import vcr

import orionapi as orion


class TestBasics(unittest.TestCase):
    def test_class(self):
        assert issubclass(orion.OrionAPI().__class__, object)

    @vcr.use_cassette()
    def test_good_login(self):
        pass


# build out proper tests and see how vcr works with Orion

if __name__ == "__main__":
    unittest.main()
