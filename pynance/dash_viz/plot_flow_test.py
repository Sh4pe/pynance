
from __future__ import print_function, absolute_import

import unittest

from .plot_flow import app, csvtype_string2description, update_output,\
    onselect_csvtype, update_csvtype_store
from ..textimporter import SupportedCsvTypes

# see https://github.com/plotly/dash/issues/297


class DashTestCase(unittest.TestCase):
    def test_build_app(self):
        self.assertFalse(app is None)

    def test_csvtype_string2description(self):
        self.assertEqual(SupportedCsvTypes.DKBCash,
                         csvtype_string2description('DKBCash'))
        self.assertEqual(SupportedCsvTypes.DKBVisa,
                         csvtype_string2description('DKBVisa'))

    def test_update_output_None(self):
        self.assertFalse(update_output(None, "") is None)

    def test_onselect_csvtype(self):
        dropdown_values = [None, "DKBCash", "DKBVisa"]
        onselect_response = [False, True, True]

        for expected, selected in zip(onselect_response, dropdown_values):
            result = onselect_csvtype(selected)
            # TODO: how to test if propagation of value change
            # is performed correctly?


def test_suite():
    suite = unittest.makeSuite(DashTestCase)
    return suite
