import random
import string
import sqlite3
import time
import json
import os
from telegram import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler

with open('config.json', 'r') as file:
    config = json.load(file)

cats_config = {}

for cat in config:
    cats_config[cat['number']] = {
        'photo_url': str(cat['jpgUrl']),
        'thumb_url': str(cat['thumbnailUrl']),
        'caption': ("["+str(cat['number'])+" из "+str(len(config))+"] Мой манул по кличке " + cat['name'] + " поглажен")
    }

conn = sqlite3.connect("cats.db")
conn.isolation_level = None
c = conn.cursor()

c.execute("SELECT cat_number, user_id FROM ( SELECT *, MIN(timestamp) OVER (PARTITION BY cat_number) AS min_timestamp FROM Requests) WHERE timestamp = min_timestamp")
result = c.fetchall()
cats = {key: value for value, key in result}

async def inline_query(update, context):
    user = update.inline_query.from_user
    cat_number = cats[user['id']] if user['id'] in cats else -1
    
    c.execute("INSERT INTO Requests (timestamp, cat_number, user_id, username) VALUES (?,?,?,?)",
        (int(time.time()), cat_number, user['id'], user['username']))

    id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    if cat_number == -1:
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=id,
                title='Всех манулов уже погладили',
                input_message_content=InputTextMessageContent('Всех манулов уже погладили')
            )
        ], cache_time=0)
    else:
        print()
        await update.inline_query.answer([
            InlineQueryResultPhoto(
                id=id,
                photo_url=cats_config[cat_number]['photo_url'],
                thumb_url=cats_config[cat_number]['thumb_url'],
                caption=cats_config[cat_number]['caption'],
            )
        ], cache_time=0)

application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
application.add_handler(InlineQueryHandler(inline_query))
application.run_polling()
