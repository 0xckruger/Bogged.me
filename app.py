from flask import Flask, redirect, url_for, render_template, request, session, flash
from pycoingecko import CoinGeckoAPI
from datetime import timedelta
import user_database as udb
import trader as td
from user_database import db
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

cg = CoinGeckoAPI()

app = Flask(__name__)
app.secret_key = "ShhhDon'tTellANYONE"
app.permanent_session_lifetime = timedelta(minutes=15)


@app.route('/index')
@app.route('/home')
@app.route('/')
def index():
    title = "home"
    return render_template('index.html', title=title)


@app.route('/about')
def about():
    title = "about"
    return render_template("about.html", title=title)


@app.route('/trade/findprice')
def find_price():
    return render_template("findprice.html")


@app.route('/trade/displayprice/')
def display_price():
    coin_id = request.args.get('coin_id', '')
    convert_currency = request.args.get('currency', '')
    coin_id = coin_id.lower()
    convert_currency = convert_currency.lower()
    if not td.check_coin(coin_id):
        flash("PRICE CHECK FAILED - UNKNOWN COIN", "warning")
        return redirect(url_for("trade"))
    elif convert_currency not in cg.get_supported_vs_currencies():
        flash("PRICE CHECK FAILED - UNKNOWN CURRENCY", "warning")
        return redirect(url_for("trade"))
    else:
        price = td.get_price(coin_id, convert_currency)
        msg = "The current price for ", coin_id.capitalize(), "is ", str(price), "in ", convert_currency.upper()
        msg = ' '.join(str(i) for i in msg)
        flash(msg, "success")
        return redirect(url_for("trade"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        email = request.form["email"]
        if email == '':
            email = "none@none"
        currency = request.form["currency"]
        starting_balance = request.form["starting_balance"]
        password = request.form["pw"]
        confirmed_password = request.form["cpw"]
        flag = udb.add_user(user, email, password, confirmed_password, currency, starting_balance)
        print(flag)
        if flag == "OK":
            flash("Registration successful", "success")
            return redirect(url_for("login"))
        else:
            flash(f"Error when registering: {flag}", "warning")
            return render_template("register.html")
    else:
        if "user" in session:
            return redirect(url_for("trade"))
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        password = request.form["pw"]
        user_data = udb.get_user(user, password)
        if not user_data:
            flash("Log in error", "danger")
            return redirect(url_for("login"))
        session["balance"] = user_data.get("balance")
        session["starting_balance"] = user_data.get("starting_balance")
        session["currency"] = user_data.get("currency")
        session["wallet"] = user_data.get("wallet")
        session["user"] = user_data.get("name")
        flash("Logged in", "success")
        return redirect(url_for("trade"))
    else:
        if "user" in session:
            return redirect(url_for("trade"))
        return render_template("login.html")


@app.route("/trade")
def trade():
    if "user" in session:
        user = session["user"]
        # print("balance: ", db.get(user).get("balance"))
        # print("wallet : ", db.get(user).get("wallet"))
        balance = db.get(user).get("balance")
        wallet = db.get(user).get("wallet")
        balance_total = td.calculate_profit(user)[0]
        percent_profit = td.calculate_profit(user)[1]

        return render_template(
            "trade.html", user=user, balance=round(balance, 2), wallet=wallet, balance_total=balance_total,
            percent_profit=percent_profit)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    try:
        # print(session["user"])
        user = session["user"]
        session.pop("user", None)
        flash("Logged out", "success")
        return redirect(url_for("index"))
    except:
        flash("You aren't logged in", "warning")
        return redirect(url_for("login"))


@app.route("/buy")
def buy():
    # balance = float(session["balance"])
    user = session["user"]
    coin_id = request.args.get('coin_id', '')
    coin_amount = float(request.args.get('coin_amount', ''))
    currency = db.get(user).get("currency")
    coin_id = coin_id.lower()
    currency = currency.lower()

    if not td.check_coin(coin_id):
        flash("TRADE FAILED - UNKNOWN COIN", "danger")
        return redirect(url_for("trade"))
    elif currency not in cg.get_supported_vs_currencies():
        flash("PRICE CHECK FAILED - UNKNOWN CURRENCY", "danger")
        return redirect(url_for("buy"))

    price = td.get_price(coin_id, currency)
    purchase = float(price) * coin_amount

    status = td.purchase(session["user"], purchase, coin_amount, coin_id)
    if status:
        return render_template(
            "executed_buy.html",
            coin_id=coin_id.capitalize(),
            coin_amount=coin_amount,
            price=price,
            purchase=round(purchase, 3))
    else:
        flash("TRADE FAILED - INSUFFICIENT FUNDS", "danger")
        print("Error")
        return redirect(url_for("trade"))


@app.route("/sell")
def sell():
    # balance = float(session["balance"])
    user = session["user"]
    coin_id = request.args.get('coin_id', '')
    coin_amount = float(request.args.get('coin_amount', ''))
    currency = db.get(user).get("currency")
    coin_id = coin_id.lower()
    currency = currency.lower()
    if not td.check_coin(coin_id):
        flash("TRADE FAILED - UNKNOWN COIN", "danger")
        return redirect(url_for("trade"))
    elif currency not in cg.get_supported_vs_currencies():
        flash("PRICE CHECK FAILED - UNKNOWN CURRENCY", "danger")
        return redirect(url_for("sell"))

    price = td.get_price(coin_id, currency)
    sold_price = float(price) * coin_amount

    status = td.sell(session["user"], sold_price, coin_amount, coin_id)
    if status:
        return render_template(
            "executed_sell.html",
            coin_id=coin_id.capitalize(),
            price=price,
            coin_amount=coin_amount,
            sold_price=round(sold_price, 3))
    else:
        flash("TRADE FAILED - INSUFFICIENT COIN BALANCE", "danger")
        print("Error")
        return redirect(url_for("trade"))


app.run('127.0.0.1', 8080, debug=True)
