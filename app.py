'''import statements'''
from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response, \
    render_template_string, send_from_directory
from pycoingecko import CoinGeckoAPI
from datetime import timedelta
import csv
# import matplotlib.pyplot as plt #not needed right now
import user_database as udb
import trader as td
from user.models import User
from user_database import db
import os

cg = CoinGeckoAPI()

app = Flask(__name__)

# app.secret_key = os.environ.get("SESSION_SECRET")
app.secret_key = os.urandom(12).hex()
app.permanent_session_lifetime = timedelta(minutes=45)


@app.route('/.well-known/pki-validation/3F7F01F6277DCEADE61365A43DBA85C0.txt')
def pki():
    return send_from_directory('.well-known/pki-validation', '3F7F01F6277DCEADE61365A43DBA85C0.txt')


'''index/homepage route'''


@app.route('/index')
@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')


'''register route'''


@app.route('/register', methods=['POST', 'GET'])
def register():
    # Handles a user signup
    if "user" in session:
        flash("You are already logged in", "warning")
        return redirect("/trade")
    if request.method == 'POST':
        user = User()
        success_flag = user.signup()
        if success_flag == "OK":
            '''flash has 2 fields: first field is your message, 2nd is severity: 'danger', 'warning', 'success'''
            flash('Your account was created successfully!', "success")
            return redirect('/login')
        else:
            flash(f"Register error: {success_flag}", "danger")
            return redirect('/register')

            # Default GET route
    return render_template('register.html')


'''login route'''


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Handles a user login
    if "user" in session:
        flash("You are already logged in", "warning")
        return redirect("/trade")
    if request.method == 'POST':
        session["widget"] = 859
        user = User()
        success_flag = user.login()

        if success_flag:
            session.permanent = True
            user = session['user']
            session["username"] = udb.get_user_name(user)
            session["balance"] = udb.get_user_balance(user)
            session["id"] = udb.get_user_id(user)
            session["starting_balance"] = udb.get_user_starting_balance(user)
            session["currency"] = udb.get_user_currency(user)
            session["wallet"] = udb.get_user_wallet(user)
            flash('Your were logged in successfully!', "success")
            return redirect('/trade')
        else:
            flash("Log in error - Bad username/password", 'danger')
            return redirect('/login')

    # Default GET route
    return render_template('login.html')


'''logout route'''


@app.route('/logout')
def logout():
    # handles a user logout
    try:
        user = User()
        success_flag = user.logout()
        if success_flag:
            flash('Your were logged out successfully!', "success")
            return redirect(url_for('login'))
    except:
        flash("You are not logged in", "warning")
        return redirect(url_for('login'))


'''about page; for information on the bogdanoffs'''


# TODO: add more facts about boggs, fanart/videos.
@app.route('/about')
def about():
    return render_template("about.html")


'''find price page. not really used anymore
@app.route('/trade/findprice')
def find_price():
    return render_template("findprice.html")
'''

'''Display price page; this is where the user can lookup price/charts (through widget) of a cryptocurrency. Utilizes 
CoinGecko and Coinlib API'''


@app.route('/trade/displayprice/')
def display_price():
    coin_id = request.args.get('coin_id', '')
    convert_currency = session["currency"]
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
        msg = "The current price for ", coin_id.capitalize(
        ), "is ", str(price), "in ", convert_currency.upper()
        msg = ' '.join(str(i) for i in msg)
        flash(msg, "success")
        widget_id = find_coin_id(coin_id)
        session["widget"] = widget_id
        return redirect(url_for("trade"))


'''function used by findprice route to get coinlib id for use in coinlib widget'''


def find_coin_id(coin_name):
    return udb.find_coin_id(coin_name)
    # with open('output.csv') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     for row in csv_reader:
    #         if row[0] == coin_name:
    #             return row[1]


'''Trade route; main website utility for trading cryptocurrency'''


@app.route("/trade", methods=['GET', 'POST'])
def trade():
    if "user" in session:

        user = session["user"]
        widget_id = session["widget"]

        username = udb.get_user_name(user)
        balance = session["balance"]
        wallet = udb.get_user_wallet(user)
        currency = udb.get_user_currency(user)
        balance_total = td.calculate_profit(user)[0]
        percent_profit = td.calculate_profit(user)[1]

        if request.method == "POST":
            print("called from POST /trade")

            # Collects buy information from user
            coin_id = request.form["coin_id"]
            coin_id = coin_id.lower()
            coin_amount = request.form["coin_amount"]
            coin_amount = float(coin_amount)

            # #Info from sell form
            # coin_id_sell = request.form["coin_id_sell"]
            # coin_id_sell = coin_id_sell.lower()
            # coin_amount_sell = request.form["coin_amount_sell"]
            # coin_amount_sell = float(coin_amount_sell)

            # handles a buy
            if "confirm_buy" in request.form:
                print("performing a buy")
                if not td.check_coin(coin_id):
                    flash("TRADE FAILED - UNKNOWN COIN", "warning")
                    return redirect(url_for("trade"))
                elif currency not in cg.get_supported_vs_currencies():
                    flash("PRICE CHECK FAILED - UNKNOWN CURRENCY", "warning")
                    return redirect(url_for("trade"))

                price = td.get_price(coin_id, currency)
                purchase = float(price) * coin_amount
                status = td.purchase(
                    user, purchase, coin_amount, coin_id)

                if status:
                    flash(
                        f"Your purchase of {coin_amount} {coin_id.capitalize()} @ {price} totaling {round(purchase, 3)} has completed successfully",
                        "success")
                    return redirect(url_for("trade"))
                else:
                    flash("TRADE FAILED - INSUFFICIENT FUNDS", "danger")

                # handles a sell
            elif "confirm_sell" in request.form:
                print("Getting ready to perform a sell")
                if not td.check_coin(coin_id):
                    flash("TRADE FAILED - UNKNOWN COIN", "danger")
                    return redirect(url_for("trade"))
                elif currency not in cg.get_supported_vs_currencies():
                    flash("PRICE CHECK FAILED - UNKNOWN CURRENCY", "danger")
                    return redirect(url_for("sell"))

                price = td.get_price(coin_id, currency)
                sold_price = float(price) * coin_amount

                status = td.sell(
                    session["user"], sold_price, coin_amount, coin_id)
                if status:
                    flash(
                        f"Your sale of {coin_amount} {coin_id.capitalize()} @ {price} totalling {round(sold_price, 3)} has completed successfully",
                        "success")
                    return redirect(url_for("trade"))
                else:
                    flash(
                        "TRADE FAILED - INSUFFICIENT COIN BALANCE", "danger")
                    return redirect(url_for("trade"))

            return render_template(
                "trade.html", user=username, balance=round(balance, 2), wallet=wallet, balance_total=balance_total,
                percent_profit=percent_profit, widget_id=widget_id)
    if request.method == "GET":
        if "user" in session:
            return render_template(
                "trade.html", user=username, balance=round(balance, 2), wallet=wallet, balance_total=balance_total,
                percent_profit=percent_profit, widget_id=widget_id)
        else:
            flash("You are not logged in", "warning")
            return redirect('/home')

    else:
        return redirect(url_for("login"))


# ''' TODO Pie chart for displaying user's wallets dynamically,
# @app.route("/trade/piechart.png")
# def piechart():
#     #wallet = session["wallet"]
#     import datetime
#     from io import BytesIO
#     import random

# #     from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# #     from matplotlib.figure import Figure
# #     from matplotlib.dates import DateFormatter

# #     user = session["user"]
# #     wallet = session["wallet"]

# #     labels = []
# #     sizes = []
# #     for x, y in wallet.items():
# #         labels.append(x)
# #         sizes.append(y)
# #     plt.pie(sizes, labels=labels)
# #     plt.axis('equal')

#     canvas = FigureCanvas(plt)
#     png_output = BytesIO()
#     canvas.print_png(png_output)
#     response = make_response(png_output.getvalue())
#     response.headers['Content-Type'] = 'image/png'
#     return response
# '''

'''Leaderboard for all traders on the site. Ranks all users by percent profit determined by their total investments 
in wallet. O(N) run time, where N is the number of users in the database. '''


@app.route("/leaderboard")
def leaderboard():
    if "user" in session:
        user_ = session["username"]
    else:
        user_ = "Stranger"

    users = udb.get_all_users()
    # print(users)
    leaderboard = []

    # Add users and their respective information to the leaderboard
    for user in users:
        user_name = user.get("name")
        date_joined = user.get("date_joined")

        percent_profit = td.calculate_profit_leaderboard(
            user)[1]  # [balance, percent_profit]
        # print(user_name, "profit is", percent_profit, "balance is: ", td.calculate_profit_leaderboard(user)[0])
        percent_profit = round(percent_profit * 100 - 100, 2)

        user_info = {
            "user_name": user_name,
            "percent_profit": percent_profit,
            "date_joined": date_joined
        }

        leaderboard.append(user_info)

    # Rank the leaderboard in descending order
    # item[0] accesses percent profit in user_info object
    # dict(sorted(leaderboard.items(), key=lambda item: item[0]))
    def rank_by_percent_profit(lb):
        return lb['percent_profit']

    leaderboard.sort(key=rank_by_percent_profit, reverse=True)

    # Render template to all site visitors, regardless of login status
    return render_template(
        "leaderboard.html", users=users, leaderboard=leaderboard, user_=user_
    )


'''Buy modal that asks to confirm a user's purchase (displaying purchase quantity, price) before execution'''

'''
# TODO: implement buy/sell modal fully
@app.route("/trade#buyModal", methods=['GET', 'POST'])
def buyModal():
    print("called from /trade#buyModal")
    if request.method == 'POST':
        print("Called from /trade#buyModal")
        print("clicked buymodal")
        coin_id = request.form['coin_id']
        coin_amount = request.form['coin_amount']
        print(coin_id, coin_amount)
    else:
        print('get')
        
@app.route("/trade/preprice", methods=['GET', 'POST'])
def prebuy():
    print("preprice")
'''

'''Buy route for purchasing a cryptocurrency from the trade page. '''


# TODO: remove buying/selling from trade route and put into their own routes as defined here.
@app.route("/trade/buy", methods=['GET', 'POST'])
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
        return redirect(url_for("trade"))

    price = td.get_price(coin_id, currency)
    purchase = float(price) * coin_amount

    status = td.purchase(session["user"], purchase, coin_amount, coin_id)
    if status:
        flash(
            f"Your purchase of {coin_amount} {coin_id.capitalize()} @ {price} totaling {round(purchase, 3)} has completed successfully",
            "success")
        return redirect(url_for("trade"))
    else:
        flash("TRADE FAILED - INSUFFICIENT FUNDS", "danger")
        print("Error")
        return redirect(url_for("trade"))


'''sell route'''


@app.route("/trade/sell", methods=['GET', 'POST'])
def sell():
    print("/trade/sell")
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
        flash(
            f"Your sale of {coin_amount} {coin_id.capitalize()} @ {price} totalling {round(sold_price, 3)} has completed successfully",
            "success")
        return redirect(url_for("trade"))
    else:
        flash("TRADE FAILED - INSUFFICIENT COIN BALANCE", "danger")
        print("Error")
        return redirect(url_for("trade"))


print("Trying to connect to database...")
udb.find_coin_id("Dogecoin")
#app.run('127.0.0.1', 8080, debug=True)
