#!/usr/bin/env python

import unittest
import doctest
import pynance.dummy_test
import pynance.textimporter_test

def doc_test_suite():
    "Returns the testsuite doctests for all modules. Please don't forget to add new modules here."

    # Every module that doctests should be run on needs to present in the scope of the function.
    # And they need to be added below.
    import pynance
    import pynance.dummy
    import pynance.textimporter

    # ... here:
    doctest_suite = doctest.DocTestSuite(pynance.textimporter_test)
    doctest_suite.addTest(doctest.DocTestSuite(pynance.dummy_test))
    doctest_suite.addTest(doctest.DocTestSuite(pynance.dummy))
    doctest_suite.addTest(doctest.DocTestSuite(pynance.textimporter))

    return doctest_suite

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(pynance.dummy_test.test_suite())
    suite.addTests(pynance.textimporter_test.test_suite())

    suite.addTest(doc_test_suite())

    return suite


def run_all_unit_tests():
    test_runner = unittest.TextTestRunner()
    return len(test_runner.run(test_suite()).failures) == 0

if __name__ == "__main__":
    run_all_unit_tests()
