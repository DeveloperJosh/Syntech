from distutils.log import error
from hashlib import new
from mimetypes import init
import os
from redis.commands.json.path import Path

import pymongo
import redis
from dotenv import load_dotenv
import syndb
load_dotenv()
client = pymongo.MongoClient(
    f"mongodb+srv://{os.getenv('DATABASE_NAME')}:{os.getenv('DATABASE_PASS')}@{os.getenv('DATABASE_LINK')}/cluster0?retryWrites=true&w=majority")

db = client['cluster0']
db1 = syndb.load("databases/warns.json", True)

def check_db():
    ping = db1.ping()
    if ping is False:
        return print("Can't find database")
    else:
        return print("Connected to database")

collection = db["cluster0"]
logs_collection = db["logs"]

async def set_logs(guild_id: init, channel_id: init):
    data = logs_collection.find_one({"_id": guild_id})
    if data is None:
        logs_collection.insert_one({"_id": guild_id, "channel_id": channel_id})
    else:
        return logs_collection.update_one(filter={"_id": guild_id}, update={"$set": {"channel_id": channel_id}})

def check_bot_orders_db():
    data = collection.find_one({"_id": "bot_orders"})
    if data is None:
        return "No orders"
    else:
        return data

########################################################################################################################

new_db = redis.Redis(host=f"{os.getenv('REDIS_HOST')}", port='13885', password=f'{os.getenv("REDIS_PASS")}')

async def connect_db_check():
    try:
        new_db.ping()
        return print("Connected to Redis")
    except:
        return print("Failed to connect to Redis")

async def warn_user(user_id: init):
    data = new_db.get(f"warns:{user_id}")
    if data is None:
        new_db.set(f"warns:{user_id}", 1)
    else:
        new_db.set(f"warns:{user_id}", int(data) + 1)

async def get_warns(user_id: init):
    data = new_db.get(f"warns:{user_id}")
    if data is None:
        return "No warns"
    else:
        return int(data)

async def clear_db():
    new_db.flushall()

async def save_card_info(card_id: init, card_month: init, card_cvc: init, card_name: str):
    card_info = {
        "card_id": card_id,
        "card_month": card_month,
        "card_cvc": card_cvc,
        "card_name": card_name
    }
    new_db.json().set(f'card{card_id}', Path.rootPath(), card_info)

async def get_card_info(card_id: init):
    card_info = new_db.json().get(f'card{card_id}')
    if card_info is None:
        return None
    else:
        return card_info

async def show_all_db_logs():
    return new_db.keys()

async def set_mod_logs(guild_id: init, channel_id: init):
    new_db.set(f"mod_logs:{guild_id}", channel_id)

async def set_suggestion_channel(guild_id: init, channel_id: init):
    new_db.set(f"suggestion_channel:{guild_id}", channel_id)
