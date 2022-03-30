from flask import Blueprint, request, escape, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_required, login_user


auth = Blueprint('auth', __name__)

from main import db, User


@auth.route('/signup', methods=['POST', 'GET'])
def Signup():
    if request.method == 'POST':
        new_user = escape(request.form['login'])
        new_password = escape(request.form['password'])
        user = User.query.filter_by(login=new_user).first()
        if user:
            flash('User already exists!')
            return redirect('/signup')
        new_record = User(login=new_user, password=generate_password_hash(new_password, method='sha256'))
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('auth.Login'))
    else:
        return render_template('signup.html')


@auth.route('/login', methods=['POST', 'GET'])
def Login():
    if request.method == 'POST':
        login = escape(request.form['login'])
        password = escape(request.form['password'])
        user = User.query.filter_by(login=login).first()
        if not user or not check_password_hash(user.password, password):
            flash('Your credentials do not match!')
            return redirect('/login')
        login_user(user, remember=True)
        return redirect(url_for('Main'))
    else:
        return render_template('login.html')


@auth.route('/logout')
@login_required
def Logout():
    logout_user()
    return redirect(url_for('Main'))
