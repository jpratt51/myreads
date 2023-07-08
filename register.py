"""Functions for registration routes for myreads app."""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User
from forms import UserForm, SendCodeForm, VerifyEmailForm
from flask_mail import Mail, Message
from random import randint
import os

app = Flask(__name__)
print(os.getenv('SECRET_KEY'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['MAIL_SERVER']= os.getenv('SMTP_RELAY')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('SMTP_ACCT')
app.config['MAIL_PASSWORD'] = os.getenv('SMTP_KEY')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

connect_db(app)

# registration routes
# *************************************************************************
# *************************************************************************

def register_account():
    """Generate form to register new user.

    Upon successful registration add new user username to session for login."""

    if "username" in session:
        flash("Must be logged out", "info")
        return redirect("/")

    if "verified" in session:
        verified = session["verified"]
    else:
        verified = False

    if verified == True :
        form = UserForm()
        if form.validate_on_submit():
            if "verified" in session:
                session.pop("verified")

            u = User.query.filter_by(username=form.username.data).first()

            if u :
                flash(f"Username already in use", "info")
                session["verified"] = True
                return redirect('/register/register')

            email = session["email"]

            username = form.username.data
            password = form.password.data
            email = email
            first_name = form.first_name.data
            last_name = form.last_name.data
            img_url = form.img_url.data
            new_user = User.register(username, first_name, last_name, email,password, img_url)

            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            if "email" in session:
                session.pop("email")

            flash(f'Welcome {new_user.username}! Account creation successful!', "success")
            return redirect('/')
        return render_template('/register/register.html', form=form)
    return redirect("/register/send-code")

def send_verification_code():
    """Generate form to verify user's email account. Sends six digit code to user's email for verification."""

    if "username" in session:
        flash("Must be logged out", "info")
        return redirect('/')

    form = SendCodeForm()
    if form.validate_on_submit():

        email = form.email.data
        u = User.query.filter_by(email=email).first()

        if u :
            flash(f"Email already in use", "warning")
            return redirect('/login')

        session["email"] = email
        
        send_code_email()

        flash(f"Verification code sent to {email}", "success")
        return redirect('/register/verify-code')
    return render_template('/register/send-code.html', form=form)

def send_code_email():
    """Send verification code to user email address"""

    verify_code = randint(100000,999999)
    session["code"] = verify_code
    if "email" in session:
        email = session["email"]
    else:
        flash("Oops, something went wrong", "danger")
        return redirect("/register/send-code")
    msg = Message('Myreads email verification', sender = 'myreadscode@gmail.com', recipients = [email])
    msg.body = f"Verification code: {verify_code}"
    mail.send(msg)

def resend_email_code():
    """Resend verification code to user email for registration."""

    if "username" in session:
        flash("Must be logged out", "info")
        return redirect('/')

    try:
        send_code_email()
    except:
        flash("Something went wrong. Please submit your email for a new verification code.", "primary")
        return redirect('/register/send-code')

    user_email = session["email"]

    flash(f"Successfully re-sent verification code to {user_email}. Please enter the most recent verification code.", "success")
    return redirect('/register/verify-code')


def submit_code():
    """Generate form to submit code for email verification for registration."""
    form = VerifyEmailForm()

    if "code" in session:
        verify_code = session["code"]

    if form.validate_on_submit():
        if int(verify_code) == int(form.code.data):

            session["verified"] = True
            if "code" in session:
                session.pop("code")

            flash(f"Success! Email verified.", "success")
            return redirect("/register/register")
        else :
            flash("Code is incorrect. Please enter verification code and resubmit.", "danger")
    return render_template('/register/verify.html', form=form)