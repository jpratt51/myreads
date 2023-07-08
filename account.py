"""Functions for account routes for myreads app."""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User
from forms import UpdateImgForm
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# account routes ********************************************************************************************************************************************************

def my_account():
    """View user account info. Delete user account."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)

    return render_template('/account/my-account.html', user=user)

def edit_profile_pic(username):
    """Generate and handle form to update user profile picture."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    form = UpdateImgForm()
    username = session["username"]
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first() 

        user.img_url = form.img_url.data

        db.session.commit()
        flash("Updated user profile picture", "success")
        return redirect ("/account/my-account")
    return render_template("/account/update-img.html", form=form) 

def delete_account(username):
    """Delete user account."""
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    
    session.pop('username')
    if "code" in session:
        session.pop('code')
    if "email" in session:
        session.pop('email')
    if "verified" in session:
        session.pop('verified')
    flash("Account deleted. Goodbye!", "success")
    return redirect('/')