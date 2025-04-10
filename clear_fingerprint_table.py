import sqlite3

conn = sqlite3.connect('fingerprints_committee.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM fingerprints;")
cursor.execute("DELETE FROM songs;")

conn.commit()

conn.close()
