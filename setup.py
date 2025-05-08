import sqlite3

def setup_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            song_id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_name TEXT UNIQUE NOT NULL,
            file_path TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash_value TEXT NOT NULL, -- Or INTEGER if your hashes are numeric
            song_id INTEGER NOT NULL,
            offset REAL NOT NULL, -- Store time in seconds
            FOREIGN KEY (song_id) REFERENCES songs (song_id)
        )
    ''')
    # Create an index for fast hash lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_hash_value ON fingerprints (hash_value)
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    setup_db('limittest_database.db')