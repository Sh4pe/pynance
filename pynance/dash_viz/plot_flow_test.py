
from __future__ import print_function, absolute_import

import unittest

import pandas as pd

from .plot_flow import app, csvtype_string2description, update_output,\
    onselect_csvtype, update_csvtype_store, make_cashflow_figure, \
    parse_contents
from ..textimporter import SupportedCsvTypes


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

    def test_parse_contents_fail(self):
        def try_parse_invalid_input():
            return parse_contents("invalid", "DKBCash")

        def try_parse_invalid_input2():
            return parse_contents("invalid, invalid", "DKBCash")

        self.assertRaises(IOError, try_parse_invalid_input)
        self.assertRaises(IOError, try_parse_invalid_input2)

    def test_make_figure(self):
        amounts = [12.34,
                   -20,
                   0,
                   456.32]
        dates = ["2018-10-02",
                 "2018-12-03",
                 "2019-01-22",
                 "2019-02-27"]
        texts = ["payback 1",
                 "text2",
                 "cash text",
                 "your money"]

        df = pd.DataFrame([{"amount": a, "date": d, "text": t}
                           for a, d, t in zip(amounts, dates, texts)])

        result_fig = make_cashflow_figure(df)
        res_charts = result_fig._data

        # there should be two charts
        self.assertEqual(2, len(res_charts))

        all_y_values = []

        for res_chart in res_charts:
            # incoming should be all positive
            # outgoing all negative
            # there should be no other chart
            if res_chart['name'] == 'incoming':
                self.assertTrue(all(res_chart['y'] >= 0))
            elif res_chart['name'] == 'outgoing':
                self.assertTrue(all(res_chart['y'] < 0))
            else:
                self.fail('unkown chart label')

            # no unknown values should appear
            for y_value in res_chart['y']:
                self.assertIn(y_value, amounts)

            # chart should be a bar chart
            self.assertEqual('bar', res_chart['type'])

            all_y_values += list(res_chart['y'])

        # total number of y values should be the number
        # of values in amounts
        self.assertEqual(len(all_y_values), len(amounts))


def test_suite():
    """test suite for plot_flow"""
    suite = unittest.makeSuite(DashTestCase)
    return suite
