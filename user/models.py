from flask import Flask, jsonify, request, render_template, redirect, flash, url_for, session
from passlib.hash import pbkdf2_sha256
import uuid
import user_database as db

class User:

    def signup(self):
        """Signs a user up by creating a new entry to the database. Main use
        is with the registration page.
        """
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": pbkdf2_sha256.encrypt(request.form.get('password'))
        }

        # Check for duplicate entries
        if db.check_for_user(user["email"]):
            return False
        else:
            db.add_user(user)
            return True


    def login(self):
        """Checks for user on database and assigns a session for them accordignly.
        """
        # Get user from database by email
        user_exists = db.check_for_user(request.form.get('email'))
        user = db.get_user(request.form.get('email'))
        
        # Check user credentials
        if user_exists and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            session['username'] = request.form.get('name')
            return True
        else:
            return False

    def logout(self):
        if 'username' in session:
            session.pop('username')
            return True
        else:
            return False
