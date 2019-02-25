import unittest
import os.path
import shutil
from tempfile import mkdtemp
import sqlite3

from pynance.database import generate_sqlite_columns_definitions, \
    LowLevelConnection, InsertTable
from pynance.textimporter import read_csv
from pynance.dkb import SupportedCsvTypes

class TemporaryDirectory(object):
    def __enter__(self):
        self.dir = mkdtemp()
        return self.dir
    
    def __exit__(self, _1, _2, _3):
        shutil.rmtree(self.dir)

class ColumnsDefinitionsTestCase(unittest.TestCase):
    def test_it_produces_valid_string(self):
        result = generate_sqlite_columns_definitions()
        self.assertEqual(type(result), str)
        self.assertTrue(len(result) > 0)
    
    def test_it_produces_valid_sql_types(self):
        with TemporaryDirectory() as tmp_dir:
            conn = sqlite3.connect(os.path.join(tmp_dir, 'test.db'))
            with conn:
                column_definitions = generate_sqlite_columns_definitions()
                conn.execute('CREATE TABLE test ({})'.format(column_definitions))


class LowLevelConnectionTestCase(unittest.TestCase):
    def test_creates_database_file_if_not_exists(self):
        with TemporaryDirectory() as tmp_dir:
            db_file = os.path.join(tmp_dir, 'test.db')
            self.assertFalse(os.path.exists(db_file))
            with LowLevelConnection(1, db_file) as _:
                pass
            self.assertTrue(os.path.exists(db_file))
    
    def test_opens_connection(self):
        with TemporaryDirectory() as tmp_dir:
            with LowLevelConnection(1, os.path.join(tmp_dir, 'test.db')) as conn:
                self.assertIsNotNone(conn)
    
    def test_creates_expected_tables(self):
        with TemporaryDirectory() as tmp_dir:
            with LowLevelConnection(1, os.path.join(tmp_dir, 'test.db')) as conn:
                cursor = conn.cursor()
                tables = set(map(
                    lambda x: x[0],
                    cursor.execute('select name from sqlite_master where type="table"').fetchall()
                ))
                self.assertEqual(
                    tables,
                    set([LowLevelConnection.TABLE_SCHEMA_VERSION,LowLevelConnection.TABLE_TRANSACTIONS
                ]))
                self.assertEqual(
                    [(1,)],
                    cursor.execute('select count(*) from {}'.format(LowLevelConnection.TABLE_SCHEMA_VERSION)).fetchall()
                )
    
    def test_works_on_same_database_twice(self):
        with TemporaryDirectory() as tmp_dir:
            db_name = os.path.join(tmp_dir, 'test.db')
            with LowLevelConnection(1, db_name) as _:
                pass
            with LowLevelConnection(1, db_name) as conn:
                result = conn \
                    .execute('select count(*) from {}'.format(LowLevelConnection.TABLE_SCHEMA_VERSION)) \
                    .fetchall()
                self.assertEqual(1, result[0][0])

class InsertTableTestCase(unittest.TestCase):

    def test_create_temp_table_table_exists(self):
        with TemporaryDirectory() as tmp_dir:
            with LowLevelConnection(1, os.path.join(tmp_dir, 'test.db')) as conn:
                table_schema, table_name = InsertTable.create_temp_table(conn)
                # Fails if and only if table does not exist
                conn.cursor().execute('select count(*) from {}.{}'.format(table_schema, table_name))
    
    def test_create_temp_table_choses_other_table_if_exists(self):
        with TemporaryDirectory() as tmp_dir:
            with LowLevelConnection(1, os.path.join(tmp_dir, 'test.db')) as conn:
                conn.cursor().execute('CREATE TEMPORARY TABLE insert_df_0 (id INT)')
                table_schema, table_name = InsertTable.create_temp_table(conn)
                self.assertEqual(table_schema, 'temp')
                self.assertEqual(table_name, 'insert_df_1', 'expected table creation to fail exactly the first time')
    
    def test_it_removes_the_temporary_table(self):
        test_data_frame = read_csv(os.path.join('pynance', 'test_data', 'dkb_cash_sample.csv'), SupportedCsvTypes.DKBCash)
        # TODO: get rid of the 'drop' here
        test_data_frame = test_data_frame.drop(['origin'], axis=1)
        with TemporaryDirectory() as tmp_dir:
            with LowLevelConnection(1, os.path.join(tmp_dir, 'test.db')) as conn:
                insert_table_with_schema = ''

                def check_if_table_exists():
                    conn.cursor().execute('select count(*) from {}'.format(insert_table_with_schema))

                with InsertTable(conn, test_data_frame) as insert_table:
                    insert_table_with_schema = '{}.{}'.format(insert_table[0], insert_table[1])
                    check_if_table_exists()
                
                self.assertRaises(sqlite3.OperationalError, check_if_table_exists)

    def test_it_works_with_dataframes_from_text_importer(self):
        def run_test(csv_file, df_format):
            # Get the DataFrame
            self.assertTrue(os.path.isfile(csv_file))
            # TODO: Investigate what origin is good for and if we want to include it as column
            # in the database as well.
            data_frame = read_csv(csv_file, df_format).drop(['origin'], axis=1)
            self.assertTrue(len(data_frame.index) > 0)
    
            # Load it into the InserTable and test this
            with TemporaryDirectory() as tmp_dir:
                with LowLevelConnection(1, os.path.join(tmp_dir, 'test.db')) as conn:
                    with InsertTable(conn, data_frame) as insert_table:

                        data_frame_size = len(data_frame.index)
                        database_rows = conn.cursor() \
                            .execute('SELECT count(*) FROM {}.{}'.format(insert_table[0], insert_table[1])).fetchall()[0][0]

                        self.assertEqual(data_frame_size, database_rows, 'not all (or more?) rows written to database')

        run_test(os.path.join('pynance', 'test_data', 'dkb_cash_sample.csv'), SupportedCsvTypes.DKBCash)
        run_test(os.path.join('pynance', 'test_data', 'dkb_visa_sample.csv'), SupportedCsvTypes.DKBVisa)


def test_suite():
    "return the test suite"

    suite = unittest.makeSuite(LowLevelConnectionTestCase)
    suite.addTests(unittest.makeSuite(InsertTableTestCase))

    return suite