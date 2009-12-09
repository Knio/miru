# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
import os
try:
    from twisted.trial import unittest
    _twisted = True
    #from twisted.python import log
    #import sys
    #log.startLogging(sys.stdout)
except ImportError:
    import unittest
    _twisted = False


def path(basename):
    return os.path.join(os.path.dirname(__file__), basename)

window = None
# A psuedo-decorator to ensure window is intialized before running test
def require_window(f=None):
    global window
    if not window:
        from miru.ui import TestWindow
        window = TestWindow()
    return f

def get_window():
    return window


def reportFtest(test, answer=None):
    import pickle
    answer = answer is not None and answer or raw_input("Did it work? [y/N] ")
    fh = None
    try:
        fname = os.path.join(os.path.dirname(__file__), '_examples.pickle')
        fh = open(fname)
        pickled = pickle.load(fh)
    except IOError:
        pickled = {}
    if fh: fh.close()
    pickled[test] = answer.lower() in ('y', 'yes') and 'pass' or 'fail'
    fh = open(fname, 'w')
    pickle.dump(pickled, fh)
    fh.close()


