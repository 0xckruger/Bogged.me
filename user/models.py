from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect, flash, url_for, session
from passlib.context import CryptContext
import uuid
import user_database as db

pwd_context = CryptContext(
    schemes=["pbkdf2_sha512", "pbkdf2_sha256"],
    deprecated="auto",
    )

accepted_currencies = ['usd', 'ars', 'aud', 'cad', 'chf', 'clp', 'cny', 'czk', 'dkk', 'eur', 'gbp', 'hkd', 'inr',
                       'jpy', 'krw', 'kwd', 'mmk', 'mxn', 'myr', 'ngn', 'nok', 'nzd', 'pkr', 'pln', 'rub', 'sar',
                       'sek', 'sgd', 'thb', 'try', 'twd', 'uah', 'vef', 'vnd', 'zar']
now = datetime.now()
default_wallet = {
    "bitcoin": 0,
    "litecoin": 0,
    "ethereum": 0
}


class User:

    def signup(self):
        """Signs a user up by creating a new entry to the database. Main use
        is with the registration page.
        """
        name = request.form.get('username')
        email = request.form.get('email')
        currency = request.form.get('currency').lower()
        date_joined = now.strftime("%m/%d/%Y, %H:%M:%S")
        starting_balance = int(request.form.get('starting_balance'))
        password = pwd_context.hash(request.form.get('password'))
        # Check for duplicate entries
        if db.check_for_user(name):
            return "USER_EXISTS"
        if currency.lower() not in accepted_currencies:
            return "BAD_CURRENCY"
        if starting_balance < 10:
            return "BALANCE_TOO_LOW"


        # TODO: sanitize for password/username input (no spaces, etc)
        else:
            user = {
                "_id": uuid.uuid4().hex,
                "name": name,
                "email": email,
                "currency": currency.lower(),
                "date_joined": date_joined,
                "starting_balance": starting_balance,
                "balance": starting_balance,
                "wallet": default_wallet,
                "password": password
            }
            db.add_user(user)
            #print(now.strftime("%m/%d/%Y, %H:%M:%S"))
            return "OK"

    def login(self):
        """Checks for user on database and assigns a session for them accordingly.
        """
        # Get user from database by name
        user_exists = db.check_for_user(request.form.get('user'))
        user = db.get_user(request.form.get('user'))
        # Check user credentials
        if user_exists and pwd_context.verify(request.form.get('password'), user['password']):
            session['user'] = user
            return True
        else:
            return False

    def logout(self):
        if 'user' in session:
            session.pop('user')
            return True
        else:
            return False
