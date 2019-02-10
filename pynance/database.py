import sqlite3

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
    TABLE_TRANSACTIONS_FIELDS = [
        'imported_at INTEGER', # unix timestamp
        'date TEXT', # format: YYYY-MM-DD
        'sender_account TEXT', 
        'receiver_account TEXT',
        'text TEXT',
        'amount REAL',
        'total_balance REAL',
        'currency TEXT',
        'category TEXT',
        'tags TEXT'
    ]

    def __init__(self, schema_version, db_file_name):
        """
        Parameters:
         * `schema_version`: Integer denoting the schema version.
         * `db_file_name`: This DB file will be created if it does not yet exist.
        """
        assert schema_version in LowLevelConnection.SUPPORTED_SCHEMA_VERSIONS
        self.db_file_name = db_file_name

        with sqlite3.connect(self.db_file_name) as conn:
            cursor = conn.cursor()
            cursor.execute('BEGIN TRANSACTION')

            cursor.execute('CREATE TABLE IF NOT EXISTS {} (version INTEGER)'.format(LowLevelConnection.TABLE_SCHEMA_VERSION))
            cursor.execute('INSERT INTO {} VALUES (1)'.format(LowLevelConnection.TABLE_SCHEMA_VERSION))

            cursor.execute('CREATE TABLE IF NOT EXISTS {} ({})'.format(
                LowLevelConnection.TABLE_TRANSACTIONS,
                ', '.join(
                    [LowLevelConnection.TABLE_TRANSACTIONS_ID] + LowLevelConnection.TABLE_TRANSACTIONS_FIELDS
                )
            ))
            cursor.execute('CREATE INDEX date_index ON {} ({})'.format(LowLevelConnection.TABLE_TRANSACTIONS, 'date'))

            cursor.execute('COMMIT')
            conn.commit()
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file_name)
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
                cursor.execute('CREATE TEMPORARY TABLE {} ({})'.format( table_name, ', '.join(LowLevelConnection.TABLE_TRANSACTIONS_FIELDS)))
            except sqlite3.OperationalError:
                go_on = True
                i += 1
        
        return 'temp', table_name

    def __init__(self, conn, data_frame):
        "uses conn, fetches everything from 'data_frame' into a temporary table"
        
        self.conn = conn
        self.temp_table_schema, self.temp_table_name = InsertTable.create_temp_table(conn)
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