from pycoingecko import CoinGeckoAPI
from user_database import db
cg = CoinGeckoAPI()




def get_price(coin_id, currency):
    if not (coin_id)[0].isdigit():
        coin_id = coin_id.lower()
    currency = currency.lower()
    if coin_id == '':
        coin_id = "bitcoin"
    if currency == '':
        currency = "usd"
    price = cg.get_price(ids = coin_id, vs_currencies = currency)
    price = price.get(coin_id).get(currency)
    return price



def purchase(user, purchase, coin_amount, coin_id):
    balance = db.get(user).get("balance")
    wallet = db.get(user).get("wallet")
    if balance < purchase:
        print("Error: Balance cannot be less than purchase")
        return False
    else:
        balance -= purchase
        if (coin_id in wallet):
            wallet[coin_id] += coin_amount
        else:
            wallet[coin_id] = coin_amount
        
        user_data_temp = db.get(user)
        user_data_temp["balance"] = balance
        user_data_temp["wallet"] = wallet
        db.set(user, user_data_temp)
        #db.dump()
        return True

def sell(user, purchase, coin_amount, coin_id):
    balance = db.get(user).get("balance")
    wallet = db.get(user).get("wallet")
    coin_balance = wallet.get(coin_id)
    if (coin_amount > coin_balance):
        print("Error: Not enough coins")
        return False
    else:
        coin_balance -= coin_amount
        wallet[coin_id] = coin_balance
        balance += purchase

        user_data_temp = db.get(user)
        user_data_temp["balance"] = balance
        user_data_temp["wallet"] = wallet
        db.set(user, user_data_temp)
        #db.dump()
        return True

def calculate_profit(user):
    balance = db.get(user).get("balance")
    wallet = db.get(user).get("wallet")
    coin_balance = 0
    for coin in wallet:
        temp_coin_balance = wallet[coin]
        temp_coin_balance *= cg.get_price(ids=coin, vs_currencies='usd').get(coin).get('usd')
        #print(temp_coin_balance)
        coin_balance += temp_coin_balance
    balance += coin_balance
    percent_profit = balance / 100000
    return [balance, percent_profit]


def check_coin(coin_id):
    try:
        data = cg.get_coin_by_id(coin_id)
        print("good coin")
        return True
    except ValueError:
        print('bad coin')
        return False
        
