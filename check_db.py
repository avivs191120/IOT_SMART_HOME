import sqlite3

conn = sqlite3.connect("smart_greenhouse.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM measurements")
rows = cursor.fetchall()

print("Number of rows:", len(rows))

for row in rows:
    print(row)

conn.close()