from __future__ import absolute_import, print_function

import unittest
import os.path
import io

import numpy as np
from numpy.testing import assert_array_equal, \
    assert_array_almost_equal, assert_almost_equal

from .textimporter import read_csv, \
    COLUMNS, UnsupportedCsvFormatException, \
    CsvFileDescription, amounts_to_balances
from .dkb import SupportedCsvTypes, DKBFormatters, DKBCsvDialect


class CsvBalanceImportTestCase(unittest.TestCase):
    def read_dummy_file_dkbcash_small(self):
        dummyfile_dkbcash_small = os.path.join("pynance",
                                               "test_data",
                                               "dkb_cash_sample.csv")
        assert os.path.isfile(dummyfile_dkbcash_small)

        return read_csv(dummyfile_dkbcash_small,
                        SupportedCsvTypes.DKBCash)

    def read_dummy_file_dkbvisa_small(self):
        dummyfile_dkbvisa_small = os.path.join("pynance",
                                               "test_data",
                                               "dkb_visa_sample.csv")
        assert os.path.isfile(dummyfile_dkbvisa_small)

        return read_csv(dummyfile_dkbvisa_small,
                        SupportedCsvTypes.DKBVisa)

    def test_read_final_balance(self):
        """
        read total balance of an imported file
        after the last transaction of that file
        """
        dkb_cash_sample_df = self.read_dummy_file_dkbcash_small()
        final_balance_dkbcash = 248.54

        dkb_visa_sample_df = self.read_dummy_file_dkbvisa_small()
        final_balance_dkbvisa = 465.33

        # check if the balance at the end is equal to the value
        # given in the header
        self.assertEqual(final_balance_dkbcash,
                         dkb_cash_sample_df['total_balance'].iloc[-1])
        self.assertEqual(final_balance_dkbvisa,
                         dkb_visa_sample_df['total_balance'].iloc[-1])

    def test_read_all_balance_dkbcash(self):
        dkb_cash_sample_df = self.read_dummy_file_dkbcash_small()
        balances_dkbcash = [138.54, 258.54, 248.54]

        assert_array_almost_equal(balances_dkbcash,
                                  dkb_cash_sample_df['total_balance'].tolist())

    def test_read_balance_sanity(self):
        dkb_cash_sample_df = self.read_dummy_file_dkbcash_small()
        dkb_visa_sample_df = self.read_dummy_file_dkbvisa_small()

        for df in [dkb_cash_sample_df, dkb_visa_sample_df]:
            amounts = df['amount'].tolist()
            balances = df['total_balance'].tolist()

            for i in range(len(amounts)-1):
                assert_almost_equal(balances[i+1], balances[i]+amounts[i+1])

    def test_dkbcash_balance_regex_match(self):
        dummyfile_dkbcash_small = os.path.join("pynance",
                                               "test_data",
                                               "dkb_cash_sample.csv")

        csv_desc = SupportedCsvTypes.DKBCash
        expected_balance = 248.54

        balance = csv_desc.read_total_balance(dummyfile_dkbcash_small)

        self.assertEqual(expected_balance, balance)

    def test_dkbvisa_balance_regex_match(self):
        dummyfile_dkbvisa_small = os.path.join("pynance",
                                               "test_data",
                                               "dkb_visa_sample.csv")

        csv_desc = SupportedCsvTypes.DKBVisa
        expected_balance = 465.33

        balance = csv_desc.read_total_balance(dummyfile_dkbvisa_small)

        self.assertEqual(expected_balance, balance)

    def test_dkbvisa_StringIO_regex_match(self):
        csv_desc = SupportedCsvTypes.DKBVisa

        header = u"""
            "Kreditkarte:";"3546********6546";

            "Zeitraum:";"letzten 60 Tage";
            "Saldo:";"465,33 EUR";
            "Datum:";"28.01.2019";

            "Umsatz abgerechnet und nicht im Saldo enthalte
            """
        header_stream = io.StringIO(header)
        balance = csv_desc.read_total_balance(header_stream)

        self.assertEqual(465.33, balance)

    def test_dkbvisa_failing_regex_match(self):
        csv_desc = SupportedCsvTypes.DKBVisa

        invalid_header = u"""
            "Kreditkarte:";"3546********6546";

            "Zeitraum:";"letzten 60 Tage";
            "BALANCE:";"465,33 EUR";
            "Datum:";"28.01.2019";

            "Umsatz abgerechnet und nicht im Saldo enthalte
            """
        header_stream = io.StringIO(invalid_header)

        def parse_invald_header():
            csv_desc.read_total_balance(header_stream)

        self.assertRaises(UnsupportedCsvFormatException, parse_invald_header)

    def test_amounts_to_balances1(self):
        amounts = np.array([-12.23, 9.00, 453.23, -232.32])
        final_balance = 221.32
        expected_balances = np.array([-8.59, 0.41, 453.64, 221.32])

        balances = amounts_to_balances(amounts, final_balance)
        assert_array_almost_equal(expected_balances, balances)

    def test_amounts_to_balances2(self):
        np.random.seed(0)
        amounts = np.random.random(100)*1000 - np.random.randint(300, 500)
        final_balance = np.random.random()*10000
        balances = amounts_to_balances(amounts, final_balance)

        for i in range(len(amounts)-1):
            assert_almost_equal(balances[i+1], balances[i]+amounts[i+1])

        self.assertEqual(balances[-1], final_balance)


def test_suite():
    suite = unittest.makeSuite(CsvBalanceImportTestCase)
    return suite
