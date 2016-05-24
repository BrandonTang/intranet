from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..db_helpers import authenticate_login
# from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    email = None
    if form.validate_on_submit():
        if "@" in form.email.data:
            email = form.email.data
            user = User.query.filter_by(email=form.email.data).first()
        else:
            print form.email.data
            email = User.query.filter_by(username=str(form.email.data)).first().email
            print 'email', User.query.filter_by(username=form.email.data).first().email
            user = User.query.filter_by(email=email).first()
        user_to_login = authenticate_login(email, form.password.data)
        if user_to_login:
            if user:
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                return redirect(url_for('auth.register'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_to_login = authenticate_login(form.email.data, form.password.data)
        if user_to_login:
            user = User(email=form.email.data, username=form.username.data)
            db.session.add(user)
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        else:
            flash('You are not an authorized user. Please recheck your email and password and try again.')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)
