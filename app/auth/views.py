"""
.. module:: auth.views.

   :synopsis: Handles all authentication URL endpoints for the
   timeclock application
"""
from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
from .. import db
from ..models import User, Role
from ..decorators import admin_required
from ..email import send_email
from ..utils import InvalidResetToken
from .forms import (
    LoginForm,
    RegistrationForm,
    AdminRegistrationForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    ChangePasswordForm
)
from .modules import check_password_requirements
from datetime import datetime
from werkzeug.security import check_password_hash
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Renders the HTML page where users can register new accounts. If the RegistrationForm meets criteria, a new user is
    written into the database.

    :return: HTML page for registration.
    """
    current_app.logger.info('Start function register() [VIEW]')
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=(form.email.data).lower(),
                    password=form.password.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    validated=True)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info('Successfully registered user {}'.format(user.email))
        flash('User successfully registered', category='success')
        current_app.logger.info('End function register() [VIEW]')
        return redirect(url_for('auth.login'))
    current_app.logger.info('End function register() [VIEW]')
    return render_template('auth/register.html', form=form)


@auth.route('/admin_register', methods=['GET', 'POST'])
@admin_required
def admin_register():
    """
    Renders a form for admins to register new users.

    :return: HTML page where admins can register new users
    """
    current_app.logger.info('Start function admin_register() [VIEW]')
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        temp_password = datetime.today().strftime('%A%-d')

        # Default tag set to 6: Other
        tag_id = 6
        if 'tag' in form:
            tag_id = form.tag.data
        user = User(email=(form.email.data).lower(),
                    password=temp_password,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    division=form.division.data,
                    role=Role.query.filter_by(name=form.role.data).first(),
                    tag_id=tag_id
                    )
        db.session.add(user)
        db.session.commit()
        current_app.logger.info('{} successfully registered user with email {}'.format(current_user.email, user.email))

        send_email(user.email,
                   'DORIS Intranet - New User Registration',
                   'auth/email/new_user',
                   user=user,
                   temp_password=temp_password)

        current_app.logger.info('Sent login instructions to {}'.format(user.email))
        flash('User successfully registered\nAn email with login instructions has been sent to {}'.format(user.email),
              category='success')

        current_app.logger.info('End function admin_register() [VIEW]')
        return redirect(url_for('main.index'))

    current_app.logger.info('End function admin_register() [VIEW]')
    return render_template('auth/admin_register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    View function to login a user. Redirects the user to the index page on successful login.

    :return: Login page.
    """
    current_app.logger.info('Start function login() [VIEW]')
    # Redirect to index if already logged in
    # if current_user.is_authenticated:
    #     # current_app.logger.info('{} is already authenticated: redirecting to index'.format(current_user.email))
    #     current_app.logger.info('End function login() [VIEW]')
    #     return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=(form.email.data).lower()).first()

        if user and user.login_attempts > 3:
            # Too many invalid attempts
            current_app.logger.info('{} has been locked out'.format(user.email))
            flash('You have too many invalid login attempts. You must reset your password.',
                  category='error')
            current_app.logger.info('End function login() [VIEW]')
            return redirect(url_for('auth.password_reset_request'))

        if user is not None and user.verify_password(form.password.data):
            # Credentials successfully submitted
            login_user(user)
            user.login_attempts = 0
            db.session.add(user)
            db.session.commit()
            current_app.logger.info('{} successfully logged in'.format(current_user.email))

            # Check to ensure password isn't outdated
            if (datetime.today() - current_user.password_list.last_changed).days > 90:
                # If user's password has expired (not update in 90 days)
                current_app.logger.info('{}\'s password hasn\'t been updated in 90 days: account invalidated.'
                                        .format(current_user.email))
                current_user.validated = False
                db.session.add(current_user)
                db.session.commit()
                flash('You haven\'t changed your password in 90 days. You must re-validate your account',
                      category='error')
                current_app.logger.info('End function login() [VIEW]')
                return redirect(url_for('auth.change_password'))

            if (datetime.today() - current_user.password_list.last_changed).days > 75:
                # If user's password is about to expire (not updated in 75 days)
                days_to_expire = (datetime.today() - current_user.password_list.last_changed).days
                flash('Your password will expire in {} days.'.format(days_to_expire), category='warning')
            current_app.logger.error('{} is already logged in. Redirecting to main.index'.format(current_user.email))
            current_app.logger.info('End function login() [VIEW]')
            return redirect(request.args.get('next') or url_for('main.index'))

        if user:
            current_app.logger.info('{} failed to log in: Invalid username or password'.format(user.email))
            user.login_attempts += 1
            db.session.add(user)
            db.session.commit()
        flash('Invalid username or password', category='error')
    current_app.logger.info('End function login() [VIEW]')
    return render_template('auth/login.html', form=form, reset_url=url_for('auth.password_reset_request'))


@auth.route('/logout')
@login_required
def logout():
    """
    View function to logout a user.

    :return: Index page.
    """
    current_app.logger.info('Start function logout() [VIEW]')
    current_user_email = current_user.email
    logout_user()
    current_app.logger.info('{} logged out'.format(current_user_email))
    flash('You have been logged out.', category='success')
    current_app.logger.info('End function logout() [VIEW]')
    return redirect(url_for('auth.login'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    View function for changing a user password.

    :return: Change Password page.
    """
    current_app.logger.info('Start function change_password() [VIEW]')
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if (
            check_password_hash(pwhash=current_user.password_list.p1,
                                password=form.password.data) or
            check_password_hash(pwhash=current_user.password_list.p2,
                                password=form.password.data) or
            check_password_hash(pwhash=current_user.password_list.p3,
                                password=form.password.data) or
            check_password_hash(pwhash=current_user.password_list.p4,
                                password=form.password.data) or
            check_password_hash(pwhash=current_user.password_list.p5,
                                password=form.password.data)
        ):
            # If the inputted password is one of the user's last five passwords
            current_app.logger.info('{} tried to change password. Failed: Used old password.'.format(
                current_user.email))
            flash('Your password cannot be the same as the last 5 passwords', category='error')
            return render_template("auth/change_password.html", form=form)

        elif check_password_requirements(
                current_user.email,
                form.old_password.data,
                form.password.data,
                form.password2.data):
            # If password security requirements are met
            current_user.password_list.update(current_user.password_hash)
            current_user.password = form.password.data
            current_user.validated = True
            db.session.add(current_user)
            db.session.commit()
            current_app.logger.info('{} changed their password.'.format(current_user.email))
            flash('Your password has been updated.', category='success')
            current_app.logger.info('End function logout() [VIEW]')
            return redirect(url_for('main.index'))

    current_app.logger.info('End function logout() [VIEW]')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """
    View function for requesting a password reset.

    :return: HTML page in which users can request a password reset.
    """
    current_app.logger.info('Start function password_reset_request() [VIEW]')
    if not current_user.is_anonymous:
        current_app.logger.info('Current user ({}) is already signed in. Redirecting to index...'.
                                format(current_user.email))
        return redirect(url_for('main.index'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        current_app.logger.info('Tried to submit a password reset request with account email {}'.format(
            form.email.data))
        current_app.logger.info('Querying for user with given email: {}'.format(form.email.data))
        user = User.query.filter_by(email=(form.email.data).lower()).first()
        current_app.logger.info('Finished querying for user with given email')
        if user:
            token = user.generate_reset_token()
            send_email(user.email,
                       'Reset Your Password',
                       'auth/email/reset_password',
                       user=user,
                       token=token,
                       next=request.args.get('next'))
            current_app.logger.info('Sent password reset instructions to {}'.format(form.email.data))
            flash('An email with instructions to reset your password has been sent to you.', category='success')
        else:
            current_app.logger.info('Requested password reset for e-mail %s but no such account exists' %
                                    form.email.data)
            flash('An account with this email was not found in the system.', category='error')
        current_app.logger.info('Redirecting to /auth/login...')
        current_app.logger.info('End function password_reset_request() [VIEW]')
        return redirect(url_for('auth.login'))
    current_app.logger.info('End function password_reset_request() [VIEW]')
    return render_template('auth/request_reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """
    View function after a user has clicked on a password reset link in their inbox.

    :param token: The token that is checked to verify the user's credentials.
    :return: HTML page in which users can reset their passwords.
    """
    current_app.logger.info('Start function password_reset [VIEW]')
    if not current_user.is_anonymous:
        # If a user is signed in already, redirect them to index
        current_app.logger.info('{} is already signed in. redirecting to /index...'.format(current_user.email))
        current_app.logger.info('End function password_reset')
        return redirect(url_for('main.index'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            # Token has timed out
            current_app.logger.error('EXCEPTION (ValueError): Token no longer valid')
            flash('This token is no longer valid.', category='warning')
            current_app.logger.info('End function password_reset')
            return redirect(url_for('auth.login'))

        current_app.logger.error('Querying for user that corresponds to given token')
        user = User.query.filter_by(id=data.get('reset')).first()
        current_app.logger.error('Finished querying for user')

        if user is None:
            # If the user associated with the token does not exist, log an error and redirect user to index
            current_app.logger.error('Requested password reset for invalid account.')
            current_app.logger.info('End function password_reset')
            return redirect(url_for('main.index'))

        elif (
            check_password_hash(pwhash=user.password_list.p1,
                                password=form.password.data) or
            check_password_hash(pwhash=user.password_list.p2,
                                password=form.password.data) or
            check_password_hash(pwhash=user.password_list.p3,
                                password=form.password.data) or
            check_password_hash(pwhash=user.password_list.p4,
                                password=form.password.data) or
            check_password_hash(pwhash=user.password_list.p5,
                                password=form.password.data)
        ):
            # If user tries to set password to one of last five passwords, flash an error and reset the form
            current_app.logger.error('{} tried to change password. Failed: Used old password.'.format(
                user.email))
            flash('Your password cannot be the same as the last 5 passwords', category='error')
            current_app.logger.info('End function password_reset')
            return render_template("auth/reset_password.html", form=form)
        else:
            try:
                if 'reset_token' in session and session['reset_token']['valid'] and user.reset_password(token, form.password.data):
                    # If the token has not been used and the user submits a proper new password, reset users password
                    # and login attempts
                    user.login_attempts = 0
                    db.session.add(user)
                    db.session.commit()
                    session['reset_token']['valid'] = False  # Now that the token has been used, invalidate it
                    current_app.logger.error('Successfully changed password for {}'.format(user.email))
                    flash('Your password has been updated.', category='success')
                    current_app.logger.info('End function password_reset... redirecting to login')
                    return redirect(url_for('auth.login'))

                elif 'reset_token' in session and not session['reset_token']['valid']:
                    # If the token has already been used, flash an error message
                    current_app.logger.error('Failed to change password for {}: token invalid (already used)'
                                             .format(user.email))
                    flash('You can only use a reset token once. Please generate a new reset token.', category='error')
                    current_app.logger.info('End function password_reset')
                    return render_template('auth/reset_password.html', form=form)

                else:
                    # New password didn't meet minimum security criteria
                    current_app.logger.error(
                        'Entered invalid new password for {}'.format(user.email))
                    flash('Password must be at least 8 characters with at least 1 Uppercase Letter and 1 Number',
                          category='error')
                    current_app.logger.info('End function password_reset')
                    return render_template('auth/reset_password.html', form=form)

            except InvalidResetToken:
                current_app.logger.error('EXCEPTION (InvalidResetToken): Token no longer valid')
                flash('This token is no longer valid.', category='warning')
                current_app.logger.info('End function password_reset')
                return login()

    current_app.logger.info('End function password_reset')
    return render_template('auth/reset_password.html', form=form)