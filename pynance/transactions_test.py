import unittest
from .transactions import dataframe
from hypothesis import given
import numpy as np
from datetime import date

from pynance.definitions import COLUMNS


class DataframeTestCase(unittest.TestCase):

    @given(df=dataframe(min_size=1, max_size=1))
    def test_has_expected_columns(self, df):
        types = dict(df.dtypes)
        self.assertEqual(len(types), len(COLUMNS))
        for col in COLUMNS:
            self.assertTrue(col in types)

    @given(df=dataframe(min_size=1, min_date=date(2000, 1, 1)))
    def test_respects_min_date(self, df):
        remaining = df['date'][df['date'] < date(2000, 1, 1)]
        self.assertEqual(remaining.size, 0)

    @given(df=dataframe(min_size=1, max_date=date(2000, 1, 1)))
    def test_respects_max_date(self, df):
        remaining = df['date'][df['date'] > date(2000, 1, 1)]
        self.assertEqual(remaining.size, 0)

    @given(df=dataframe(min_size=10))
    def test_respects_min_size(self, df):
        self.assertGreaterEqual(len(df), 10)

    @given(dataframe(max_size=10))
    def test_respects_max_size(self, df):
        self.assertLessEqual(len(df), 10)
