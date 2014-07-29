# -*- coding: utf-8 -*-
from flask import Blueprint, request, make_response, render_template, flash, redirect, url_for, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from app.mod_users.models import User, ROLE_USER, ROLE_ADMIN
from app.database import db, bcrypt


# Define the blueprint: 'auth', set its url prefix: app.url/auth
users = Blueprint('users', __name__, url_prefix='/users')

# Instantiate login
login_manager = LoginManager()
login_manager.login_view = 'login'

# Load user into each response
@login_manager.user_loader
def load_user(id):
        return User.query.get(int(id))

##login views
def login_view():
    if request.method == 'GET':
        return render_template('users/login.html')
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('authenticated.home'))
    username = request.form['username']
    user = User.query.filter(User.username==username).first()
    if user is None:
        flash('No such user. Please try again')
        return render_template('users/login.html')
    pw_check = bcrypt.check_password_hash(user.pw_hash, request.form['password'])
    if not pw_check:
        flash('Incorrect password. Please try again')
        return render_template('users/login.html')
    login_user(user)
    flash("Logged in successfully")
    return redirect(url_for('authenticated.home'))

def user_create():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter(User.username==username).first():
            flash('User already exists. Please log in.')
            return redirect(url_for('users.login'))
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        user = User(username=username, pw_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
        flash('User successfully registered. Please log in.')
        return redirect(url_for('users.login'))
    return render_template('users/user_create.html')

def logout_view():
    logged_out = logout_user()
    if logged_out:
        flash('User logged out')
        return render_template(url_for('users.logout'), msg="User logged out")
    msg = 'No user to log out.'
    return render_template(url_for('users.logout'), msg=msg)


# URLs
users.add_url_rule('/login/', 'login', login_view, methods=['GET', 'POST'])
users.add_url_rule('/create/', 'user_create', user_create, methods=['GET', 'POST'])
users.add_url_rule('/logout/', 'logout', logout_view)
