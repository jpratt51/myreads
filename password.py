"""Functions for password reset routes for myreads app."""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User
from forms import SendCodeForm, VerifyEmailForm, ResetPasswordForm
import os
from register import send_code_email
from flask_bcrypt import Bcrypt

app = Flask(__name__)

bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# Password reset routes ********************************************************************************************************************************************************

def send_reset_code():
    """Generate form to verify user's email account. Sends six digit code to users email that will be used to complete password reset."""
    form = SendCodeForm()
    if form.validate_on_submit():

        u = User.query.filter_by(email=form.email.data).first()

        if u :               

            session["email"] = form.email.data
            user_email = session["email"]

            send_code_email()

            flash(f"Verification code sent to {user_email}", "success")
            return redirect('/password/verify-reset-code')
    return render_template('/password/reset-code.html', form=form)

def submit_reset_code():
    """Generate form to submit code for email verification for password reset."""
    form = VerifyEmailForm()

    if "code" in session:
        verify_code = session["code"]

    if form.validate_on_submit():
        if int(verify_code) == int(form.code.data):
            session["verified"] = True
            flash(f"Success! Email verified.", "success")
            return redirect("/password/reset-password")
        else :
            flash("Code is incorrect. Please enter verification code and resubmit.", "danger")
    return render_template('/password/verify-reset.html', form=form)

def submit_resent_code():
    """Resend verification code to user email for password reset."""
    try:
        send_code_email()
    except:
        flash("Something went wrong. Please submit your email for a new verification code.", "primary")
        return redirect('/password/reset-code')

    if "email" in session:
        user_email = session["email"]

    flash(f"Successfully re-sent verification code to {user_email}. Please enter the most recent verification code.", "success")
    return redirect('/password/verify-reset-code')

def password_reset():
    """Generate form to reset user password.

    Upon successful password reset, direct user to login page."""

    if "verified" in session:
        verified = session["verified"]

    if verified == True :
        form = ResetPasswordForm()
        if form.validate_on_submit():
            if "verified" in session:
                session.pop("verified")

            user_email = session["email"]

            user = User.query.filter_by(email=user_email).first()

            if user :
                password = form.password.data

                hashed = bcrypt.generate_password_hash(password)
                hashed_utf8 = hashed.decode("utf8")
                user.password = hashed_utf8

                db.session.commit()

                flash("Successfully reset password", "success")
                return redirect('/login')
            flash("Oops, something went wrong! Please enter your email address", "danger")
            return redirect("/password/reset-code")
        return render_template('/password/reset-password.html', form=form)
    return redirect("/password/reset-code")