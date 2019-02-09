import unittest
import os.path
import shutil
from tempfile import mkdtemp

from pynance.database import LowLevelConnection

class TemporaryDirectory(object):
    def __enter__(self):
        self.dir = mkdtemp()
        return self.dir
    
    def __exit__(self, _1, _2, _3):
        shutil.rmtree(self.dir)

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



def test_suite():
    "return the test suite"
    suite = unittest.TestSuite()
    suite.addTest(LowLevelConnectionTestCase('test_creates_database_file_if_not_exists'))
    suite.addTest(LowLevelConnectionTestCase('test_opens_connection'))
    suite.addTest(LowLevelConnectionTestCase('test_creates_expected_tables'))
    return suite