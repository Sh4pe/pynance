
from __future__ import print_function, absolute_import

import unittest
import os.path
import base64
import json

import pandas as pd
import numpy as np
from numpy.testing import assert_array_equal

from .plot_flow import app, csvtype_string2description, update_bar_chart,\
    onselect_csvtype, update_csvtype_store, make_cashflow_figure, \
    make_line_figure, parse_contents
from ..dkb import SupportedCsvTypes
from ..textimporter import amounts_to_balances


class DashTestCase(unittest.TestCase):
    def test_build_app(self):
        self.assertFalse(app is None)

    def test_csvtype_string2description(self):
        self.assertEqual(SupportedCsvTypes.DKBCash,
                         csvtype_string2description('DKBCash'))
        self.assertEqual(SupportedCsvTypes.DKBVisa,
                         csvtype_string2description('DKBVisa'))

    def test_onselect_csvtype(self):
        dropdown_values = [None, "DKBCash", "DKBVisa"]
        onselect_response = [False, True, True]

        for expected, selected in zip(onselect_response, dropdown_values):
            response = onselect_csvtype(selected)
            response_dict = json.loads(response.data.decode())
            is_enabled = not response_dict["response"]["props"]["disabled"]

            self.assertEqual(expected, is_enabled)

    def test_parse_contents_fail(self):
        def parse_invalid_input():
            return parse_contents("invalid", "DKBCash")

        def parse_invalid_input2():
            return parse_contents("invalid, invalid", "DKBCash")

        self.assertRaises(IOError, parse_invalid_input)
        self.assertRaises(IOError, parse_invalid_input2)

    def _read_sample_file_like_uploaded(self):
        """
        This helper function reads the test file like the dash uploader
        component does
        """
        sample_csv_filepath = os.path.join("pynance",
                                           "test_data",
                                           "dkb_cash_sample.csv")

        with open(sample_csv_filepath, "rb") as csvfile:
            b64encoded = base64.b64encode(csvfile.read())
            bstr = str(b'data:application/octet-stream;base64,'+b64encoded)
        return bstr

    def test_parse_contents_decode(self):
        # read a valid csv from file to string,
        # encode it and pass it to parse

        expected_amount = np.array([-12.16,
                                    120.0,
                                    -10.0]).astype(np.float64)
        expected_sender = ["DE39500105174461799382",
                           "DE63500105173984825797",
                           "DE75500105178797957724"]

        bytestr = self._read_sample_file_like_uploaded()

        result_df = parse_contents(bytestr, "DKBCash")

        assert_array_equal(expected_amount, result_df["amount"].values)
        self.assertListEqual(expected_sender,
                             list(result_df["sender_account"].values))

    def test_make_bar_chart(self):
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

    def test_make_balance_line_chart(self):
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

        final_balance = 1000.00

        balances = amounts_to_balances(amounts, final_balance)

        df = pd.DataFrame([{"total_balance": b, "date": d, "text": t}
                           for b, d, t in zip(balances, dates, texts)])

        result_fig = make_line_figure(df)
        res_chart = result_fig._data[0]

        assert_array_equal(balances, res_chart['y'])
        self.assertEqual(final_balance, res_chart['y'][-1])

    def test_update_output_None(self):
        self.assertFalse(update_bar_chart(None, "") is None)

    def test_update_output(self):
        expected_amount = np.array([-12.16,
                                    120.0,
                                    -10.0]).astype(np.float64)

        bytestr = self._read_sample_file_like_uploaded()

        response = update_bar_chart(bytestr, "DKBCash")
        response_dict = json.loads(response.data.decode())

        res_charts = response_dict["response"]["props"]["figure"]["data"]

        all_y_values = []

        for res_chart in res_charts:
            all_y_values += list(res_chart['y'])

        assert_array_equal(np.sort(all_y_values),
                           np.sort(expected_amount))


def test_suite():
    """test suite for plot_flow"""
    suite = unittest.makeSuite(DashTestCase)
    return suite
