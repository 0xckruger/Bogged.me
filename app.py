from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response, render_template_string
from pycoingecko import CoinGeckoAPI
from datetime import timedelta
import csv
#import matplotlib.pyplot as plt
import user_database as udb
import trader as td
from user_database import db
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

cg = CoinGeckoAPI()

app = Flask(__name__)


# User Login Configurations
# login_manager = LoginManager()
# login_manager.init_app(app)
app.secret_key = "ShhhDon'tTellANYONE"
app.permanent_session_lifetime = timedelta(minutes=45)


# class User(UserMixin):
#     id = len(db.getall()) + 1


# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

# Routes Section


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
    user = session["user"]
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
        #return render_template("trade.html", widget_id=widget_id)

def find_coin_id(coin_name):
    with open('output.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0] == coin_name:
                return(row[1])

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        email = request.form["email"]
        if email == '':
            email = "none@none"
        currency = request.form["currency"]
        starting_balance = request.form["starting_balance"]
        password = request.form["password"]
        confirmed_password = request.form["password_repeat"]
        flag = udb.add_user(user, email, password,
                            confirmed_password, currency, starting_balance)
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
        session["widget"] = 859
        user = request.form["user"]
        password = request.form["password"]
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


@app.route("/trade", methods=['GET', 'POST'])
def trade():

    print("called from /trade")
    if "user" in session:

        user = session["user"]
        widget_id = session["widget"]
        # print("balance: ", db.get(user).get("balance"))
        # print("wallet : ", db.get(user).get("wallet"))
        balance = db.get(user).get("balance")
        wallet = db.get(user).get("wallet")
        balance_total = td.calculate_profit(user)[0]
        percent_profit = td.calculate_profit(user)[1]

        if(request.method == "POST"):
            print("called from POST /trade")

            # Collects buy information from user
            print(request.form)
            coin_id = request.form["coin_id"]
            coin_id = coin_id.lower()
            coin_amount = request.form["coin_amount"]
            coin_amount = float(coin_amount)
            currency = db.get(user).get("currency")

            # #Info from sell form
            # coin_id_sell = request.form["coin_id_sell"]
            # coin_id_sell = coin_id_sell.lower()
            # coin_amount_sell = request.form["coin_amount_sell"]
            # coin_amount_sell = float(coin_amount_sell)

            

            # handles a buy
            if("confirm_buy" in request.form):
                print("performing a buy")
                if not td.check_coin(coin_id):
                        flash("TRADE FAILED - UNKNOWN COIN", "danger")
                        return redirect(url_for("trade"))
                elif currency not in cg.get_supported_vs_currencies():
                    flash("PRICE CHECK FAILED - UNKNOWN CURRENCY", "danger")
                    return redirect(url_for("trade"))

                price = td.get_price(coin_id, currency)
                purchase = float(price) * coin_amount
                status = td.purchase(
                    session["user"], purchase, coin_amount, coin_id)
                if status:
                    flash(
                        f"Your purchase of {coin_amount} {coin_id.capitalize()} @ {price} totaling {round(purchase, 3)} has completed successfully", "success")
                    return redirect(url_for("trade"))
                else:
                    flash("TRADE FAILED - INSUFFICIENT FUNDS", "danger")
                    print("Error")

                # handles a sell
            elif("confirm_sell" in request.form):
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
                        f"Your sale of {coin_amount} {coin_id.capitalize()} @ {price} totalling {round(sold_price, 3)} has completed successfully", "success")
                    return redirect(url_for("trade"))
                else:
                    flash(
                        "TRADE FAILED - INSUFFICIENT COIN BALANCE", "danger")
                    print("Error")
                    return redirect(url_for("trade"))
                    
                        

            return render_template(
                            "trade.html", user=user, balance=round(balance, 2), wallet=wallet, balance_total=balance_total,
                            percent_profit=percent_profit, widget_id=widget_id)
    if(request.method == "GET"):
        print("called from GET /trade")

        return render_template(
            "trade.html", user=user, balance=round(balance, 2), wallet=wallet, balance_total=balance_total,
            percent_profit=percent_profit, widget_id=widget_id)

    else:
        return redirect(url_for("login"))
'''
@app.route("/trade/piechart.png")
def piechart():
    #wallet = session["wallet"]
    import datetime
    from io import BytesIO
    import random

#     from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#     from matplotlib.figure import Figure
#     from matplotlib.dates import DateFormatter

#     user = session["user"]
#     wallet = session["wallet"]

#     labels = []
#     sizes = []
#     for x, y in wallet.items():
#         labels.append(x)
#         sizes.append(y)
#     plt.pie(sizes, labels=labels)
#     plt.axis('equal')

    canvas = FigureCanvas(plt)
    png_output = BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
'''

@app.route("/leaderboard")
# Ranks all users by percent profit determined by their total investments in wallet.
# O(N) run time, where N is the number of users in the database.
def leaderboard():
    if "user" in session:
        user_ = session["user"]
    else:
        user_ = "Stranger"

    users = udb.get_all_users()
    leaderboard = []

    # Add users and their respective information to the leaderboard
    for user in users:
        user_name = db.get(user).get("name")
        date_joined = db.get(user).get("date_joined")
        percent_profit = td.calculate_profit(
            user)[1]  # [balance, percent_profit]
        percent_profit = round(percent_profit * 100 - 100, 2)

        user_info = {
            "user_name": user_name,
            "percent_profit": percent_profit,
            "date_joined": date_joined
        }

        leaderboard.append(user_info)

    # Rank the leaderboard in descending order
    # item[0] accesses percent profit in user_info object
    #dict(sorted(leaderboard.items(), key=lambda item: item[0]))
    def rank_by_percent_profit(lb):
        return lb['percent_profit']

    leaderboard.sort(key=rank_by_percent_profit, reverse=True)

    # Render template to all site visitors, regardless of login status
    return render_template(
        "leaderboard.html", users=users, leaderboard=leaderboard, user_ = user_
    )


@app.route("/logout")
def logout():
    try:
        # print(session["user"])
        user = session["user"]
        session.pop("user", None)
        flash("Logged out", "success")
        return redirect(url_for("login"))
    except:
        flash("You aren't logged in", "warning")
        return redirect(url_for("login"))


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

@app.route("/trade/buy", methods=['GET', 'POST'])
def buy():
    print("called from /trade/buy")
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
            f"Your purchase of {coin_amount} {coin_id.capitalize()} @ {price} totaling {round(purchase, 3)} has completed successfully", "success")
        return redirect(url_for("trade"))
    else:
        flash("TRADE FAILED - INSUFFICIENT FUNDS", "danger")
        print("Error")
        return redirect(url_for("trade"))


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
            f"Your sale of {coin_amount} {coin_id.capitalize()} @ {price} totalling {round(sold_price, 3)} has completed successfully", "success")
        return redirect(url_for("trade"))
    else:
        flash("TRADE FAILED - INSUFFICIENT COIN BALANCE", "danger")
        print("Error")
        return redirect(url_for("trade"))


#app.run('127.0.0.1', 8080, debug=True)
