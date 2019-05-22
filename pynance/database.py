"""
Explain the classes briefly. Elaborate on Storage
"""

import sqlite3
import numpy as np
from .definitions import COLUMNS


def exists_table(conn, table_name):
    """
    Returns True if and only if 'table_name' is an existing table.
    """

    result = conn.execute(
        'select count(*) from sqlite_master where type="table" and name="{}"'.format(table_name)
    ).fetchall()
    return result[0][0] == 1


def generate_sqlite_columns_definitions():
    """
    Converts definitions.COLUMNS into the column definitions of a sqlite table. By column definitions,
    we mean the part of a CREATE TABLE statement that defines the columns:

      CREATE TABLE my_table_name (<column definitions here>)

    Returns the column definitions as string
    """

    type_lookup_dict = {
        str: 'TEXT',
        np.datetime64: 'TEXT',
        np.float64: 'REAL'
    }

    def name_type_to_string(x):
        col_name, col_type = x
        if col_type not in type_lookup_dict:
            raise ValueError(
                "Don't know which sqlite type '{}' is".format(col_type))
        return '{} {}'.format(col_name, type_lookup_dict[col_type])

    return ', '.join(map(name_type_to_string, COLUMNS.items()))


class LowLevelConnection(object):
    """
    Class that handles low-level database connection. Makes sure the expected table strucutre exists.
    Should be used in with-statements.
    """

    # Schema evolution should be handled later once it is needed
    SUPPORTED_SCHEMA_VERSIONS = [1]

    TABLE_SCHEMA_VERSION = 'schema'
    TABLE_TRANSACTIONS = 'transactions'
    TABLE_TRANSACTIONS_ID = 'id INTEGER PRIMARY KEY'

    def _get_db_conn(self):
        """
        Get the connection to the sqlite database. We use the 'DEFERRED' isolation level. This
        is the default in Python 3 anyways, in Python 2 the default is autocommit mode. The DEFERRED
        isolation level seems appropriate in this case. See also
        * https://www.sqlite.org/lang_transaction.html
        """
        return sqlite3.connect(
            self.db_file_name,
            isolation_level='DEFERRED'
        )

    def __init__(self, schema_version, db_file_name):
        """
        Parameters:
         * `schema_version`: Integer denoting the schema version.
         * `db_file_name`: This DB file will be created if it does not yet exist.
        """
        assert schema_version in LowLevelConnection.SUPPORTED_SCHEMA_VERSIONS
        self.db_file_name = db_file_name

        connection = self._get_db_conn()
        with connection:
            if not exists_table(connection, LowLevelConnection.TABLE_SCHEMA_VERSION):
                connection.execute('CREATE TABLE IF NOT EXISTS {} (version INTEGER)'.format(
                    LowLevelConnection.TABLE_SCHEMA_VERSION))
                connection.execute('INSERT INTO {} VALUES (1)'.format(
                    LowLevelConnection.TABLE_SCHEMA_VERSION))

            if not exists_table(connection, LowLevelConnection.TABLE_TRANSACTIONS):
                connection.execute('CREATE TABLE IF NOT EXISTS {} ({}, {})'.format(
                    LowLevelConnection.TABLE_TRANSACTIONS,
                    LowLevelConnection.TABLE_TRANSACTIONS_ID,
                    generate_sqlite_columns_definitions()
                ))
                connection.execute('CREATE INDEX date_index ON {} ({})'.format(
                    LowLevelConnection.TABLE_TRANSACTIONS, 'date'))

    def __enter__(self):
        self.conn = self._get_db_conn()
        return self.conn

    def __exit__(self, _1, _2, _3):
        self.conn.close()


class InsertTable(object):
    """
    This class makes sure that a DataFrame is inserted into a temporary table of a sqlite databases.
    It also makes sure that the temporary table is created in a safe way and disposed afterwards. For
    this purpuse, instances of this class should be used in with statements.
    """

    @staticmethod
    def create_temp_table(conn):
        """Creates temporary table suitable for inserting the DataFrame and returns its name."""

        cursor = conn.cursor()
        i, table_name, go_on = 0, '', True

        while go_on:
            go_on = False
            table_name = 'insert_df_{}'.format(i)
            try:
                cursor.execute('CREATE TEMPORARY TABLE {} ({})'.format(
                    table_name,
                    generate_sqlite_columns_definitions()
                ))
            except sqlite3.OperationalError:
                go_on = True
                i += 1

        return 'temp', table_name

    def __init__(self, conn, data_frame):
        "uses conn, fetches everything from 'data_frame' into a temporary table"

        self.conn = conn
        self.temp_table_schema, self.temp_table_name = InsertTable.create_temp_table(
            conn)
        data_frame.to_sql(
            name=self.temp_table_name,
            schema=self.temp_table_schema,
            index=False,
            con=conn,
            chunksize=5000
        )

    def __enter__(self):
        return (self.temp_table_schema, self.temp_table_name)

    def __exit__(self, _1, _2, _3):
        "Make sure the table is gone."
        self.conn.cursor().execute('DROP TABLE {}.{}'.format(
            self.temp_table_schema, self.temp_table_name
        ))


class Storage(object):

    def __init__(self, db_file):
        self.db_file = db_file

    @classmethod
    def validate_dataframe_shape(cls, data_frame):
        """
        asserts that the correct columns are present. 
        Tolerates that additional columns are present
        """
        pass

    def append_dataframe(self, data_frame):
        """
        asserts that the shape of the dataframe is correct
        returns the part of the dataframe that is new. This part has also an ID column
        """
        if not self.validate_dataframe_shape(data_frame):
            raise Exception('Invalid dataframe')

        with LowLevelConnection(1, self.db_file) as conn:
            with InsertTable(conn, data_frame) as insert_table:
                # add existing data to insert_table
                with conn:
                    conn.cursor().execute('INSERT INTO %s ')
                # but only non-duplicates
                # replace existing table by insert_table
                pass

    def load_dataframe(self):
        """
        loads from db. contains ID column
        """
        pass
