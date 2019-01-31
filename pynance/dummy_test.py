#!/usr/bin/env python

import unittest

from pynance.dummy import my_dummy_function


class DummyTestCase(unittest.TestCase):
    def test_my_dummy_function(self):
        self.assertEqual(my_dummy_function(2), 4)
        self.assertEqual(my_dummy_function(4), 8)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DummyTestCase('test_my_dummy_function'))
    return suite
