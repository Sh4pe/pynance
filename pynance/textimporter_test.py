from __future__ import absolute_import, print_function

import unittest
import os.path
import io

import numpy as np
from numpy.testing import assert_array_equal, \
    assert_array_almost_equal, assert_almost_equal

from .textimporter import read_csv, SupportedCsvTypes, \
    COLUMNS, UnsupportedCsvFormatException, \
    CsvFileDescription, DKBFormatters, \
    DKBCsvDialect, amounts_to_balances


class CsvImportTestCase(unittest.TestCase):

    # helper
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

    # test construction of an invalid CsvFileDescription
    def test_create_invalid_CsvFileDescription(self):

        def construction_missing_formatter():
            bad_formatter_map = DKBFormatters.formatter_map()
            del bad_formatter_map[str]

            CsvFileDescription(column_map={
                "date": "Wertstellung",
                "sender_account": "Kontonummer",
                "text": "Verwendungszweck",
                "amount": "Betrag (EUR)",
            },
                csv_dialect=DKBCsvDialect(),
                formatters=bad_formatter_map,
                skiprows=6,
                encoding="iso-8859-1",
                total_balance_re_pattern=r'(?<=Kontostand vom '
                                         r'\d{2}.\d{2}.\d{4}:";")'
                                         r'(\d+,\d+)')
        self.assertRaises(AssertionError, construction_missing_formatter)

    # tests DKB

    def test_csv_importer_read_dkbcash(self):
        self.read_dummy_file_dkbcash_small()

    def test_csv_importer_read_dkbcash_empty_columns(self):
        """
        some colummns should be NAN on all entries
        all others should not be NAN on any entry
        """
        result_df = self.read_dummy_file_dkbcash_small()

        expected_empty_column_names = ["receiver_account",
                                       "category",
                                       "tags",
                                       "origin",
                                       "currency"]
        expected_nonempty_column_names = ["date",
                                          "sender_account",
                                          "text",
                                          "amount"]
        # self check if all columns are tested to be either expected to be
        # empty or full
        self.assertTrue(all([c in COLUMNS
                             for c in
                             expected_empty_column_names +
                             expected_nonempty_column_names]))

        # verify all empty columns are in fact empty
        for empty_col_name in expected_empty_column_names:
            self.assertTrue(np.all(result_df[empty_col_name].isna()))

        # verify all nonempty columns are in fact not empty nowhere
        for nonempty_col_name in expected_nonempty_column_names:
            self.assertFalse(np.any(result_df[nonempty_col_name].isna()))

    def test_csv_importer_read_dkbcash_headers(self):
        result_df = self.read_dummy_file_dkbcash_small()

        result_df_col_names = list(result_df.columns.values)

        for col_name, col_type in COLUMNS.items():
            # check value
            self.assertTrue(col_name in result_df_col_names)
            result_col_type = result_df[col_name].dtype

            # check type
            if col_type == str:
                self.assertEqual(np.dtype(object), result_col_type)
            elif col_type == np.datetime64:
                # ugly problem when comparing datetime types
                # https://stackoverflow.com/questions/29206612/difference-between-data-type-datetime64ns-and-m8ns
                self.assertTrue(np.issubdtype(result_col_type, col_type))
            else:
                self.assertEqual(col_type, result_col_type)

    def test_csv_importer_read_dkbcash_amounts(self):
        result_df = self.read_dummy_file_dkbcash_small()
        expected = np.array([-12.16,
                             120.0,
                             -10.0]).astype(np.float64)
        assert_array_equal(expected, result_df["amount"].values)

    def test_csv_importer_read_dkbcash_senderIBANs(self):
        result_df = self.read_dummy_file_dkbcash_small()
        expected = ["DE39500105174461799382",
                    "DE63500105173984825797",
                    "DE75500105178797957724"]
        self.assertListEqual(expected,
                             list(result_df["sender_account"].values))

    def test_csv_importer_read_dkbcash_date(self):
        result_df = self.read_dummy_file_dkbcash_small()
        expected = np.array(['2018-12-04',
                             '2018-12-03',
                             '2018-12-03']).astype(np.datetime64)
        assert_array_equal(expected, result_df["date"].values)

    def test_csv_importer_read_dkbcash_text(self):
        result_df = self.read_dummy_file_dkbcash_small()
        expected = ["PP.4882.PP . FLIXBUS, Ihr Einkauf bei FLIXBUS",
                    "Miete 2017",
                    "Vers.-Nr.0065435465, Helene Musterfrau"]
        self.assertListEqual(expected, list(result_df["text"].values))

    def test_csv_importer_read_exception(self):
        def call_broken():
            broken_file = os.path.join("pynance",
                                       "test_data",
                                       "dkb_cash_sample_broken.csv")
            assert os.path.isfile(broken_file)

            return read_csv(broken_file,
                            SupportedCsvTypes.DKBCash)

        self.assertRaises(UnsupportedCsvFormatException, call_broken)

    def test_csv_importer_wrong_header(self):
        def call_broken():
            broken_file = os.path.join("pynance",
                                       "test_data",
                                       "dkb_cash_sample_wrong_col.csv")
            assert os.path.isfile(broken_file)

            return read_csv(broken_file,
                            SupportedCsvTypes.DKBCash)

        self.assertRaises(UnsupportedCsvFormatException, call_broken)

    def test_dkb_float_formatting1(self):
        formatter = DKBFormatters.to_float64

        self.assertEqual(12.54, formatter("12,54"))
        self.assertTrue(np.isnan(formatter("")))
        self.assertEqual(-1200.54, formatter("-1200,54"))

    # Tests VISA

    def test_csv_importer_read_dkbvisa_empty_columns(self):
        """
        some colummns should be NAN on all entries
        all others should not be NAN on any entry
        """
        result_df = self.read_dummy_file_dkbvisa_small()

        expected_empty_column_names = ["sender_account",
                                       "receiver_account",
                                       "category",
                                       "tags",
                                       "origin",
                                       "currency"]
        expected_nonempty_column_names = ["date",
                                          "text",
                                          "amount"]
        # self check if all columns are tested to be either expected to be
        # empty or full
        self.assertTrue(all([c in COLUMNS
                             for c in
                             expected_empty_column_names +
                             expected_nonempty_column_names]))

        # verify all empty columns are in fact empty
        for empty_col_name in expected_empty_column_names:
            self.assertTrue(np.all(result_df[empty_col_name].isna()))

        # verify all nonempty columns are in fact not empty nowhere
        for nonempty_col_name in expected_nonempty_column_names:
            self.assertFalse(np.any(result_df[nonempty_col_name].isna()))

    def test_csv_importer_read_dkbvisa_headers(self):
        result_df = self.read_dummy_file_dkbvisa_small()

        result_df_col_names = list(result_df.columns.values)

        for col_name, col_type in COLUMNS.items():
            # check value
            self.assertTrue(col_name in result_df_col_names)
            result_col_type = result_df[col_name].dtype

            # check type
            if col_type == str:
                self.assertEqual(np.dtype(object), result_col_type)
            elif col_type == np.datetime64:
                # ugly problem when comparing datetime types
                # https://stackoverflow.com/questions/29206612/difference-between-data-type-datetime64ns-and-m8ns
                self.assertTrue(np.issubdtype(result_col_type, col_type))
            else:
                self.assertEqual(col_type, result_col_type)

    def test_csv_importer_read_dkbvisa_amounts(self):
        result_df = self.read_dummy_file_dkbvisa_small()
        expected = np.array([-65.00,
                             -14.33,
                             -11.42,
                             -126.45]).astype(np.float64)
        assert_array_equal(expected, result_df["amount"].values)

    def test_csv_importer_read_dkbvisa_date(self):
        result_df = self.read_dummy_file_dkbvisa_small()
        expected = np.array(['2019-01-18',
                             '2019-01-16',
                             '2019-01-14',
                             '2019-01-14']).astype(np.datetime64)
        assert_array_equal(expected, result_df["date"].values)

    def test_csv_importer_read_dkbvisa_text(self):
        result_df = self.read_dummy_file_dkbvisa_small()
        expected = ["SPORT",
                    "FRISCHEM.ABC",
                    "FRISCHEM.ABC",
                    "REWE Markt GmbH ZW"]
        self.assertListEqual(expected, list(result_df["text"].values))

    def test_dkbvisa_StringIO_import(self):
        csv_desc = SupportedCsvTypes.DKBVisa

        content = u"""
            "Kreditkarte:";"3546********6546";

            "Zeitraum:";"letzten 60 Tage";
            "Saldo:";"465,33 EUR";
            "Datum:";"28.01.2019";
            """\
            u'"Umsatz abgerechnet und nicht im Saldo enthalten";'\
            u'"Wertstellung";"Belegdatum";"Beschreibung";"Betrag'\
            u' (EUR)";"Ursprünglicher Betrag";'\
            u"""
            "Ja";"18.01.2019";"17.01.2019";"SPORT";"-65,00";"";
            "Ja";"16.01.2019";"15.01.2019";"FRISCHEM.ABC";"-14,33";"";
            "Ja";"14.01.2019";"11.01.2019";"FRISCHEM.ABC";"-11,42";"";
            "Ja";"14.01.2019";"12.01.2019";"REWE Markt GmbH ZW";"-126,45";"";
            """
        header_stream = io.StringIO(content)
        df = read_csv(header_stream, csv_desc)

        expected = ["SPORT",
                    "FRISCHEM.ABC",
                    "FRISCHEM.ABC",
                    "REWE Markt GmbH ZW"]
        self.assertListEqual(expected, df["text"].tolist())

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

        header = """
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

        invalid_header = """
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


def test_suite():
    suite = unittest.makeSuite(CsvImportTestCase)
    return suite
