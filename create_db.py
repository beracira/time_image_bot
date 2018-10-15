import sqlite3
conn = sqlite3.connect('timezone.db')

c = conn.cursor()

c.execute('''CREATE TABLE timezone (chatid integer primary key, timezone text)''')


conn.commit()

conn.close()
