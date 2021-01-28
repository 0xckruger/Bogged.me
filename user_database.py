import pymongo
from pymongo import MongoClient
import os
import pickledb as pdb
from datetime import datetime

secret = os.environ.get("DB_pass")
username = os.environ.get("USERNAME")
# Remember to copy the connection string from the atlas client :) 
cluster = pymongo.MongoClient(f"mongodb+srv://{username}:{secret}@cluster0.oykhk.mongodb.net/pymongo_auth?retryWrites=true&w=majority")
# Name of created cluster
db = cluster["pymongo_auth"]
# Name of crated collection
collection = db["users"]

def add_user(user):
    return collection.insert_one(user)

def check_for_user(email):
    if collection.find_one({"email" : email}):
        return True
    else:
        return False
    
def get_user(email):
    return collection.find_one({"email" : email})

#import currency

# db = pdb.load('bogged_user_database.db', True)
# accepted_currencies = ['usd', 'ars', 'aud', 'cad', 'chf', 'clp', 'cny', 'czk', 'dkk', 'eur', 'gbp', 'hkd', 'inr',
#                        'jpy', 'krw', 'kwd', 'mmk', 'mxn', 'myr', 'ngn', 'nok', 'nzd', 'pkr', 'pln', 'rub', 'sar',
#                        'sek', 'sgd', 'thb', 'try', 'twd', 'uah', 'vef', 'vnd', 'zar']


# def add_user(name, email, password, confirmed_password, user_currency, balance):
#     if db.exists(name):
#         return "USER_EXISTS"
#     if user_currency.lower() not in accepted_currencies:
#         return "BAD_CURRENCY"
#     if password != confirmed_password:
#         return "BAD_PASSWORD"
#     if "@" not in email:
#         return "BAD_EMAIL"
#     else:
#         now = datetime.now()
#         regtime = now.strftime("%m/%d/%Y, %H:%M:%S")
#         _id = len(db.getall()) + 1
#         wallet = {
#             "bitcoin": 0,
#             "litecoin": 0,
#             "ethereum": 0
#         }
#         user_info = {
#             "name": name,
#             "id": int(_id),
#             "email": email,
#             "password": password,
#             "currency": user_currency.lower(),
#             "wallet": wallet,
#             "starting_balance": int(balance),
#             "balance": int(balance),
#             "date_joined": regtime
#         }
#         # print(now.strftime("%m/%d/%Y, %H:%M:%S"))
#         db.set(name, user_info)
#         return "OK"

# def get_id(name):
#         return db.get(name).get("id")
    
# def get_username(name):
#         return db.get(name).get("name")

# def get_user(name, given_password):
#     if not db.exists(name):
#         print("This user does not exist.")
#         return False
#     else:
#         if db.get(name).get("password") != given_password:
#             print("Incorrect password")
#             return False
#         else:
#             return db.get(name)

# def get_all_users():
#     all_user_keys = db.getall()
#     return all_user_keys
    
