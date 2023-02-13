
import sqlite3
import json

with open('config.json', 'r') as file:
    config = json.load(file)

conn = sqlite3.connect("cats.db")
conn.isolation_level = None
c = conn.cursor()

c.execute("SELECT cat_number, username FROM ( SELECT *, MIN(timestamp) OVER (PARTITION BY cat_number) AS min_timestamp FROM Requests) WHERE timestamp = min_timestamp")
result = c.fetchall()

users = [{'cat_number': row[0], 'telegram_username': row[1]} for row in result]

print(users)