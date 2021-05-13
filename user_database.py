import pymongo
from pymongo import MongoClient
import os
import pickledb as pdb
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
secret = os.environ.get("DB_PASS")
username = os.environ.get("USERNAME")
# Remember to copy the connection string from the atlas client :)

cluster = pymongo.MongoClient(
    f"mongodb+srv://{username}:{secret}@cluster0.kxem4.mongodb.net/bogged?retryWrites=true&w=majority")
# Name of created cluster
db = cluster["bogged"]
# Name of created collection
collection = db["bogged-users"]
coin_list = db["supported_coins"]


def find_coin_id(coin_name):
    coin = coin_list.find_one({"Coin name": coin_name})
    return coin.get("Coin ID")


def get_all_users():
    all_user_keys = collection.find({})
    return list(all_user_keys)


def add_user(user):
    return collection.insert_one(user)


def check_for_user(name):
    if collection.find_one({"name": name}):
        return True
    else:
        return False


def get_user(name):
    return collection.find_one({"name": name})


def get_user_name(name):
    return name.get("name")


def get_user_id(user):
    return user.get("_id")


def get_user_balance(user):
    return user.get("balance")


def get_user_wallet(user):
    return user.get("wallet")


def get_user_currency(user):
    return user.get("currency")


def get_user_starting_balance(user):
    return user.get("starting_balance")
