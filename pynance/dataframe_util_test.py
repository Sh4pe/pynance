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
            self.assertEqual(len(hash_result), 32)

    @given(df=dataframe(min_size=1, max_date=date(2000, 1, 1)))
    def test_create_id_hash(self, df):
        result_hash_column = create_id_hash(df)
        self.assertEqual(len(result_hash_column), len(df))

        for item in result_hash_column:
            self.assertEqual(type(item), str)
            self.assertEqual(len(item), 32)
