from twisted.trial import unittest

import os

_here = os.path.dirname(__file__)
FTESTS_RESULT = os.path.join(_here, '_examples.pickle')

class FunctionalTest(unittest.TestCase):

    def testRanExamples(self):
        if not os.path.exists(FTESTS_RESULT):
            self.fail("Run functional tests (examples/ex*.py) first ...")

def testMethod(name, result):
    def _test(self):
        self.assertEquals('pass', result)
    _test.__name__ = 'test_' + name
    return _test

if os.path.exists(FTESTS_RESULT):
    import pickle
    results = pickle.load(open(FTESTS_RESULT))
    for (name, result) in results.iteritems():
        m = testMethod(name, result)
        setattr(FunctionalTest, m.__name__, m)



