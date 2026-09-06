# db_setup.py
import sqlite3

conn = sqlite3.connect('climate_data.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL
    )
''')

conn.commit()
conn.close()