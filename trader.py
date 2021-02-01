from flask import session
from pycoingecko import CoinGeckoAPI
from user_database import db
import user_database as udb

cg = CoinGeckoAPI()


def get_price(coin_id, currency):
    if not coin_id[0].isdigit():
        coin_id = coin_id.lower()
    currency = currency.lower()
    if coin_id == '':
        coin_id = "bitcoin"
    if currency == '':
        currency = "usd"
    price = cg.get_price(ids=coin_id, vs_currencies=currency)
    price = price.get(coin_id).get(currency)
    return price


def purchase(user, purchase, coin_amount, coin_id):
    balance = session["balance"]
    wallet = udb.get_user_wallet(user)
    _id = udb.get_user_id(user)
    if balance < purchase:
        print("Error: Balance cannot be less than purchase")
        return False
    else:
        new_balance = balance - purchase
        if coin_id in wallet:
            wallet[coin_id] += coin_amount
        else:
            wallet[coin_id] = coin_amount

        udb.collection.update_one(
            {"_id": _id},
            {
                "$set": {
                    "balance": new_balance,
                    "wallet": wallet
                }
            }
        )
        session["balance"] = new_balance
        return True


def sell(user, sold_price, coin_amount, coin_id):
    balance = session["balance"]
    wallet = udb.get_user_wallet(user)
    _id = udb.get_user_id(user)
    coin_balance = wallet.get(coin_id)
    if coin_amount > coin_balance:
        print("Error: Not enough coins")
        return False
    else:
        coin_balance -= coin_amount
        wallet[coin_id] = coin_balance
        new_balance = balance + sold_price
        udb.collection.update_one(
            {"_id": _id},
            {
                "$set": {
                    "balance": new_balance,
                    "wallet": wallet
                }
            }
        )
        session["balance"] = new_balance
        return True


def calculate_profit(user):
    balance = session["balance"]
    currency = udb.get_user_currency(user).lower()
    starting_balance = udb.get_user_starting_balance(user)
    wallet = udb.get_user_wallet(user)
    coin_balance = 0
    for coin in wallet:
        temp_coin_balance = wallet[coin]
        temp_coin_balance *= cg.get_price(ids=coin, vs_currencies=currency).get(coin).get(currency)
        coin_balance += temp_coin_balance
    balance += coin_balance
    percent_profit = balance / starting_balance
    return [balance, percent_profit]


def calculate_profit_leaderboard(user):
    balance = udb.get_user_balance(user)
    currency = udb.get_user_currency(user).lower()
    starting_balance = udb.get_user_starting_balance(user)
    wallet = udb.get_user_wallet(user)
    coin_balance = 0
    for coin in wallet:
        temp_coin_balance = wallet[coin]
        temp_coin_balance *= cg.get_price(ids=coin, vs_currencies=currency).get(coin).get(currency)
        coin_balance += temp_coin_balance
    balance += coin_balance
    percent_profit = balance / starting_balance
    return [balance, percent_profit]


def check_coin(coin_id):
    # if not coin_id[0].isdigit():
    # coin_id = coin_id.lower()
    try:

        data = cg.get_coin_by_id(coin_id)
        print("good coin")
        return True
    except ValueError:
        print('bad coin')
        return False
