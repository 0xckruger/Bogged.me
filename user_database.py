import pickledb as pdb
from datetime import datetime
import currency

db = pdb.load('bogged_user_database.db', True)


def add_user(name, email, password, confirmed_password, user_currency, balance):
    accepted_currencies = ['usd', 'ars', 'aud', 'cad', 'chf', 'clp', 'cny', 'czk', 'dkk', 'eur', 'gbp', 'hkd', 'inr',
                           'jpy', 'krw', 'kwd', 'mmk', 'mxn', 'myr', 'ngn', 'nok', 'nzd', 'pkr', 'pln', 'rub', 'sar',
                           'sek', 'sgd', 'thb', 'try', 'twd', 'uah', 'vef', 'vnd', 'zar']
    if db.exists(name):
        return "USER_EXISTS"
    if user_currency.lower() not in accepted_currencies:
        return "BAD_CURRENCY"
    if password != confirmed_password:
        return "BAD_PASSWORD"
    if "@" not in email:
        return "BAD_EMAIL"
    else:
        now = datetime.now()
        regtime = now.strftime("%m/%d/%Y, %H:%M:%S")
        wallet = {
            "bitcoin": 0,
            "litecoin": 0,
            "ethereum": 0
        }
        user_info = {
            "name": name,
            "email" : email,
            "password": password,
            "currency": user_currency.lower(),
            "wallet": wallet,
            "balance": int(balance),
            "date_joined": 1
        }
        print(now.strftime("%m/%d/%Y, %H:%M:%S"))
        db.set(name, user_info)
        return "OK"


def get_user(name, given_password):

    if not db.exists(name):
        print("This user does not exist.")
        return False
    else:
        if db.get(name).get("password") != given_password:
            print("Incorrect password")
            return False
        else:
            return db.get(name)
