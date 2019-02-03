#!/usr/bin/env python

import unittest
import doctest
import pynance.dummy_test
import pynance.textimporter_test

def doc_test_suite():
    "Returns the testsuite doctests for all modules. Please don't forget to add new modules here."

    import pkgutil
    import importlib
    import pynance

    doctest_suite = unittest.TestSuite()
    def add_doctests_for_module(package):
        "Recursively walks `package` and adds doctests for all submodules and subpackages to `doctest_suite`"
        for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
            sub_module = importlib.import_module('{}.{}'.format(package.__name__, name))
            if is_pkg:
                add_doctests_for_module(sub_module)
            else:
                doctest_suite.addTest(doctest.DocTestSuite(sub_module))

    add_doctests_for_module(pynance)
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
    import sys
    if run_all_unit_tests():
        sys.exit(0)
    else:
        sys.exit(1)