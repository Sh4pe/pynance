import unittest
from hypothesis import given
from datetime import date

from .transactions import dataframe
from .dataframe_util import hash_row, create_id_hash


class DataframeUtilTestcase(unittest.TestCase):

    @given(df=dataframe(min_size=1, max_date=date(2000, 1, 1)))
    def test_hash_row(self, df):
        for i, row in df.iterrows():
            hash_result = hash_row(row)
            self.assertEqual(type(hash_result), str)
            self.assertEqual(type(hash_result), str)
