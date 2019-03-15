import unittest
import os

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from .database import Storage
from .textimporter import read_csv
from .dkb import SupportedCsvTypes
from .definitions import COLUMNS


class StorageTestCase(unittest.TestCase):
    def _read_dummy_file_dkbcash_small(self):
        dummyfile_dkbcash_small = os.path.join("pynance",
                                               "test_data",
                                               "dkb_cash_sample.csv")
        assert os.path.isfile(dummyfile_dkbcash_small)

        return read_csv(dummyfile_dkbcash_small,
                        SupportedCsvTypes.DKBCash)

    def _read_dummy_file_dkbvisa_small(self):
        dummyfile_dkbvisa_small = os.path.join("pynance",
                                               "test_data",
                                               "dkb_visa_sample.csv")
        assert os.path.isfile(dummyfile_dkbvisa_small)

        return read_csv(dummyfile_dkbvisa_small,
                        SupportedCsvTypes.DKBVisa)

    def _assert_frame_relevant_columns_equal(self, df1, df2):
        assert_frame_equal(df1[COLUMNS], df2[COLUMNS])

    def _delete_temp_db_file(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def setUp(self):
        self.db_file = os.path.join("test_data", "test.sqlite")

    def test_init_storage(self):
        storage = Storage(self.db_file)
        assert storage is not None

    def test_init_storage_creates_file(self):
        # delete file to make sure starting from scratch
        self._delete_temp_db_file()

        _ = Storage(self.db_file)
        assert os.path.exists(self.db_file)

    def test_append_dataframe_dkb_cash_small(self):
        # delete file to make sure starting from scratch
        self._delete_temp_db_file()

        storage = Storage(self.db_file)
        df = self._read_dummy_file_dkbcash_small()
        newdf = storage.append_dataframe(df)

        self._assert_frame_relevant_columns_equal(df, newdf)

    def test_append_dataframe_dkb_cash_and_visa(self):
        # delete file to make sure starting from scratch
        self._delete_temp_db_file()

        storage = Storage(self.db_file)
        df_cash = self._read_dummy_file_dkbcash_small()
        df_visa = self._read_dummy_file_dkbcash_small()

        storage.append_dataframe(df_cash)
        storage.append_dataframe(df_visa)

        df_loaded = storage.load_dataframe()

        df_expected = df_cash.append(df_visa).sort_values(by="date",
                                                          ascending=False)

        self._assert_frame_relevant_columns_equal(df_loaded, df_expected)

    def test_load_dataframe(self):
        # delete file to make sure starting from scratch
        self._delete_temp_db_file()

        storage = Storage(self.db_file)
        df = self._read_dummy_file_dkbcash_small()
        newdf = storage.append_dataframe(df)
        loaded_df = storage.load_dataframe()

        self._assert_frame_relevant_columns_equal(df, loaded_df)

    def test_append_dataframe_ignores_duplicates(self):
        # delete file to make sure starting from scratch
        self._delete_temp_db_file()

        storage = Storage(self.db_file)
        df = self._read_dummy_file_dkbcash_small()

        # appending twice
        newdf = storage.append_dataframe(df)
        newdf2 = storage.append_dataframe(df)

        loaded_df = storage.load_dataframe()

        self._assert_frame_relevant_columns_equal(df, loaded_df)

    def test_append_invalid_dataframe_fails(self):
        random_df = pd.DataFrame(np.random.randn(100, 2),
                                 columns=['colA', 'colB'])

        storage = Storage(self.db_file)

        def append_invalid():
            return storage.append_dataframe(random_df)

        self.assertRaises(Exception, append_invalid)

    def tearDown(self):
        # remove temporary db file
        self._delete_temp_db_file()
