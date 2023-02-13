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

conn = sqlite3.connect("cats.db")
conn.isolation_level = None
c = conn.cursor()

async def inline_query(update, context):
    cat_number = -1
    user = update.inline_query.from_user

    cats_assigned_count = 0

    c.execute("SELECT MAX(cat_number) FROM Requests")
    result = c.fetchone()

    if result[0] is not None:
        cats_assigned_count = int(result[0])

    c.execute("SELECT cat_number FROM Requests WHERE user_id=? LIMIT 1", (user['id'],))
    result = c.fetchone()

    if result is not None:
        cat_number = int(result[0])
    elif cats_assigned_count < len(config):
        cat_number = cats_assigned_count + 1

    c.execute("INSERT INTO Requests (timestamp, cat_number, user_id, username) VALUES (?,?,?,?)",
        (int(time.time()), cat_number, user['id'], user['username']))

    cats_assigned_count = 0

    c.execute("SELECT MAX(cat_number) FROM Requests")
    result = c.fetchone()

    if result[0] is not None:
        cats_assigned_count = int(result[0])

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
        status = "" if cats_assigned_count == len(config) else ("\n\nНе поглаженных манулов: " + str(len(config) - cats_assigned_count) + ", чтобы погладить кликни в заголовок сообщения или напиши @ pet101bot без пробела")

        for cat in config:
            if cat['number'] == cat_number:
                await update.inline_query.answer([
                    InlineQueryResultPhoto(
                        id=id,
                        photo_url=str(cat['jpgUrl']),
                        thumb_url=str(cat['thumbnailUrl']),
                        caption=("["+str(cat_number)+" из "+str(len(config))+"] Мой манул по кличке " + cat['name'] + " поглажен" + status)
                    )
                ], cache_time=0)

c.execute("CREATE TABLE IF NOT EXISTS Requests (timestamp INTEGER, cat_number INTEGER, user_id INTEGER, username TEXT)")

application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
application.add_handler(InlineQueryHandler(inline_query))
application.run_polling()
