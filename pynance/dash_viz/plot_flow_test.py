from __future__ import print_function, absolute_import

import unittest

from .plot_flow import app, csvtype_string2description
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
