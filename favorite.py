"""Functions for favorites routes for myreads app."""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User, Subject, Author
from forms import SubjectForm, AuthorForm
from colors import rand_dark_color, rand_universe_color
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# Favorites routes ********************************************************************************************************************************************************

def my_favorites():
    """Render favorites page."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)

    return render_template("/favorite/my-favorites.html", user=user)

def add_favorite_subject():
    """Generate favorite subject form and handle form submission."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    form = SubjectForm()

    username = session["username"]
    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        subject_name = form.name.data
        color = rand_dark_color()

        subject = Subject(user_username=username, name=subject_name, color=color)

        db.session.add(subject)
        db.session.commit()
        flash('Favorite subject added successfully', "success")
        return redirect('/favorite/my-favorites')
    return render_template("/favorite/favorite-subject.html", user=user, form=form)

def add_favorite_author():
    """Generate favorite author form and handle form submission."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)

    form = AuthorForm()

    if form.validate_on_submit():
        author_name = form.name.data
        color = rand_universe_color()

        author = Author(user_username=username, name=author_name, color=color)

        db.session.add(author)
        db.session.commit()
        flash('Favorite author added successfully', "success")
        return redirect('/favorite/my-favorites')
    return render_template("/favorite/favorite-author.html", user=user, form=form)

# favorite delete routes ********************************************************************************************************************************************************

def remove_subject(id):
    """Delete user favorite subject."""
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Deleted subject from favorites", "success")
    return redirect('/favorite/my-favorites')

def remove_author(id):
    """Delete user favorite author."""
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    flash("Deleted author from favorites", "success")
    return redirect('/favorite/my-favorites')