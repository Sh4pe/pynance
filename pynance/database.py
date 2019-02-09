import sqlite3

class LowLevelConnection(object):
    """
    Class that handles low-level database connection. Should be used in with-statements.
    """


    # Schema evolution should be handled later once it is needed
    SUPPORTED_SCHEMA_VERSIONS = [1]

    TABLE_SCHEMA_VERSION = 'schema'
    TABLE_TRANSACTIONS = 'transactions'
    TABLE_TRANSACTIONS_FIELDS = [
        'id INTEGER PRIMARY KEY',
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
                ', '.join(LowLevelConnection.TABLE_TRANSACTIONS_FIELDS)
            ))

            cursor.execute('COMMIT')
            conn.commit()
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file_name)
        return self.conn
    
    def __exit__(self, _1, _2, _3):
        self.conn.close()