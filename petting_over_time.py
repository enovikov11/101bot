import matplotlib.pyplot as plt
import pandas as pd
import datetime
import sqlite3

conn = sqlite3.connect("cats.db")
conn.isolation_level = None
c = conn.cursor()

c.execute("SELECT timestamp FROM ( SELECT *, MIN(timestamp) OVER (PARTITION BY cat_number) AS min_timestamp FROM Requests) WHERE timestamp = min_timestamp")

result = c.fetchall()
events = [row[0] for row in result]

events = [datetime.datetime.fromtimestamp(event) for event in events]
df = pd.DataFrame({"timestamp": events})

df["timestamp"] = df["timestamp"].apply(lambda x: x.strftime("%H:%M"))

plt.plot_date(df["timestamp"], df.index, linestyle="solid")

for i, event in enumerate(events):
    plt.text(event.strftime("%H:%M"), i, '', ha="left", va="center")

plt.xlabel("Время (UTC)")
plt.title("Манулов поглажено")

positions = list(range(0, len(df), 10))
labels = df["timestamp"][::10]

plt.xticks(positions, labels)

plt.savefig("petting_over_time.png")
