"""Flask app for myreads."""

from flask import Flask, redirect, session, flash, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Book, Bookshelf, Review, Rating, ReadDate, Subject, Author, BookshelfBook
from forms import UserForm, LoginForm, SendCodeForm, VerifyEmailForm, SearchBooksForm, BookshelfForm, ReviewForm, RatingForm, ReadDatesForm, SubjectForm, AuthorForm, ResetPasswordForm, UpdateImgForm, BookForm
from flask_mail import Mail, Message
from random import randint
from search import book_search 
from colors import rand_dark_color, rand_primary_color, rand_universe_color, rand_pastel_color
from datetime import date
from flask_bcrypt import Bcrypt
import string
import os
from book import *
from bookshelf import *
from favorite import *
from account import *

app = Flask(__name__)

bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['MAIL_SERVER']='smtp-relay.sendinblue.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'myreadscode@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('SMTP_KEY')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

connect_db(app)

toolbar = DebugToolbarExtension(app)

API_BASE_URL = 'http://openlibrary.org/search.json'

# home page, login, and logout routes ********************************************************************************************************************************************************

@app.route('/')
def user_homepage():
    """Render myreads homepage for logged in/logged out user."""

    if "username" in session:
        username = session["username"]
        user = User.query.get_or_404(username)
        users = User.query.all()
        num_books = Book.query.filter_by(user_username=username).count()
        num_shelves = Bookshelf.query.filter_by(user_username=username).count()
        last_review = Review.query.filter_by(user_username=username).first()
        color_1 = rand_pastel_color()
        color_2 = rand_pastel_color()
        return render_template('/account/my-homepage.html', user=user, users=users, num_books=num_books, num_shelves=num_shelves, last_review=last_review, color_1=color_1, color_2=color_2)
    return render_template("/account/my-homepage.html")

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Generate form to handle user login."""

    if "username" in session :
        username = session["username"]
        flash("You are logged in", "primary")
        return redirect(f"/")

    else:
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.authenticate(username, password)
            if user:
                flash(f"Welcome back, {user.username}!", "primary")

                session['username'] = user.username
                return redirect(f'/')
            else:
                form.username.errors = ['Invalid username/password.']
        return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    """Logout current user."""

    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')

# account routes ********************************************************************************************************************************************************

@app.route('/account/my-account')
def account():
    """View user account info. Delete user account."""

    return my_account()

@app.route('/account/update-img/<username>', methods=["GET","POST"])
def update_img(username):
    """Generate and handle form to update user profile picture."""

    return edit_profile_pic(username)

@app.route('/account/delete-user/<username>', methods=["GET","DELETE"])
def delete_user(username):
    """Delete user account."""
    
    return delete_account(username)

# registration routes
# *************************************************************************
# *************************************************************************

@app.route('/register/register', methods=["GET", "POST"])
def register_user():
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
            session["verified"] = False

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
            session.pop("email")

            flash(f'Welcome {new_user.username}! Account creation successful!', "success")
            return redirect('/')
        return render_template('/register/register.html', form=form)
    return redirect("/register/send-code")

@app.route("/register/send-code", methods=["GET","POST"])
def send_code():
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

    msg = Message('Myreads email verification', sender = 'myreadsverify@gmail.com', recipients = [email])
    msg.body = f"Verification code: {verify_code}"
    mail.send(msg)

@app.route('/register/resend-code')
def resend_verification_code():
    """Resend verification code to user email for registration."""

    if "username" in session:
        flash("Must be logged out", "info")
        return redirect('/')

    try:
        send_code_email()
    except:
        flash("Something went wrong. Please submit your email for a new verification code.", "primary")
        return redirect('/register/send-code')

    flash(f"Successfully re-sent verification code to {user_email}. Please enter the most recent verification code.", "success")
    return redirect('/register/verify-code')

@app.route("/register/verify-code", methods=["GET","POST"])
def code_verification():
    """Generate form to submit code for email verification for registration."""
    form = VerifyEmailForm()

    if "code" in session:
        verify_code = session["code"]

    if form.validate_on_submit():
        if int(verify_code) == int(form.code.data):

            session["verified"] = True
            session.pop("code")

            flash(f"Success! Email verified.", "success")
            return redirect("/register/register")
        else :
            flash("Code is incorrect. Please enter verification code and resubmit.", "danger")
    return render_template('/register/verify.html', form=form)

# Password reset routes ********************************************************************************************************************************************************

@app.route("/password/reset-code", methods=["GET","POST"])
def reset_code():
    """Generate form to verify user's email account. Sends six digit code to users email that will be used to complete password reset."""
    form = SendCodeForm()
    if form.validate_on_submit():

        u = User.query.filter_by(email=form.email.data).first()

        if u :               

            session["email"] = form.email.data

            send_code_email()

            flash(f"Verification code sent to {user_email}", "success")
            return redirect('/password/verify-reset-code')
    return render_template('/password/reset-code.html', form=form)

@app.route("/password/verify-reset-code", methods=["GET","POST"])
def verify_reset_code():
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

@app.route('/password/resend-code')
def resend_reset_code():
    """Resend verification code to user email for password reset."""
    try:
        send_code_email()
    except:
        flash("Something went wrong. Please submit your email for a new verification code.", "primary")
        return redirect('/password/reset-code')

    flash(f"Successfully re-sent verification code to {user_email}. Please enter the most recent verification code.", "success")
    return redirect('/password/verify-reset-code')

@app.route('/password/reset-password', methods=["GET", "POST"])
def reset_password():
    """Generate form to reset user password.

    Upon successful password reset, direct user to login page."""

    if "verified" in session:
        verified = session["verified"]

    if verified == True :
        form = ResetPasswordForm()
        if form.validate_on_submit():
        
            session["verified"] = False

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

# Bookshelf routes
# **************************************************************************
# **************************************************************************

@app.route('/bookshelf/bookshelf-details/<int:bookshelf_id>', methods=['GET','POST'])
def bookshelf_details(bookshelf_id):
    """Show details about a specific bookshelf, including name and subject as well as books associated with that bookshelf."""

    return view_bookshelf_details(bookshelf_id)

@app.route('/bookshelf/add-bookshelf-book/<int:bookshelf_id>', methods=["GET", "POST"])
def add_bookshelf_book(bookshelf_id):
    """Display list of user books to add to bookshelf."""

    return bookshelf_add_book(bookshelf_id)

@app.route("/bookshelf/update-bookshelf/<int:bookshelf_id>/<int:book_id>", methods=["GET","POST"])
def update_bookshelf(bookshelf_id, book_id):
    """Add book to bookshelf."""

    return edit_bookshelf(bookshelf_id, book_id)

@app.route('/bookshelf/my-bookshelves', methods=['GET','POST'])
def bookshelves():
    """Render form to create new bookshelf and display list of user's current bookshelves. """
    
    return my_bookshelves()

# bookshelf delete routes ********************************************************************************************************************************************************

@app.route('/bookshelf/delete-bookshelf/<int:id>', methods=["GET","DELETE"])
def delete_bookshelf(id):
    """Delete user's bookshelf."""
    
    return remove_bookshelf(id)

@app.route('/bookshelf/delete-bookshelf-book/<bookshelfid>/<bookid>', methods=["GET","DELETE"])
def delete_bookshelf_book(bookshelfid, bookid):
    """Delete book from bookshelf."""
    
    return remove_bookshelf_book(bookshelfid, bookid)

# book routes ********************************************************************************************************************************************************

@app.route("/book/find-books", methods=['GET', 'POST'])
def find_books():
    """Render user mylibrary page. Generate book search form. Handle search form and pass to search results page."""

    return book_finder()

@app.route('/book/my-books', methods=['GET','POST'])
def user_books():
    """Shows list of books associated with user. 
    Generate book search form for user's books."""

    return my_books()

@app.route("/book/add-book", methods=["GET","POST"])
def manual_book_entry():
    """Generate and handle form to add book manually to database and update list of user's books."""

    return form_book_entry()

@app.route("/book/add-book/<book>", methods=["GET","POST"])
def add_book(book):
    """Generate and handle form to add book to database and update list of user's books."""

    return add_library_book(book)

@app.route('/book/book-details/<int:book_id>', methods=['GET','POST'])
def book_details(book_id):
    """Show book details. Render form to edit book by adding it to a bookshelf, deleting it, rating and leaving a review.
    """

    return edit_book(book_id)

@app.route("/book/review/<int:book_id>", methods=['GET','POST'])
def book_review(book_id):
    """Render and handle form to add/update user book review. """
    
    return edit_review(book_id)

@app.route("/book/rating/<int:book_id>", methods=['GET','POST'])
def book_rating(book_id):
    """Render and handle form to add/update user book rating. """
    
    return edit_rating(book_id)

@app.route("/book/add-rating/<int:book_id>/<book_rating>", methods=['GET','POST'])
def add_book_rating(book_id, book_rating):
    """Add/update book rating. """
    
    return add_rating(book_id, book_rating)

@app.route("/book/read-dates/<int:book_id>", methods=['GET','POST'])
def book_read_dates(book_id):
    """Render and handle form to add/update user book read dates. Accepts either start date or end date or both."""
    
    return edit_read_dates(book_id)

# book delete routes ********************************************************************************************************************************************************

@app.route('/book/delete-read-dates/<int:id>', methods=["GET","DELETE"])
def delete_read_dates(id):
    """Delete read dates for user's book."""
    
    return remove_dates(id)

@app.route('/book/delete-rating/<int:id>', methods=["GET","DELETE"])
def delete_rating(id):
    """Delete rating for user's book."""
    
    return remove_rating(id)

@app.route('/book/delete-review/<int:id>', methods=["GET","DELETE"])
def delete_review(id):
    """Delete review for user's book."""
    
    return remove_review(id)

@app.route('/book/delete-book/<int:id>', methods=["GET","DELETE"])
def delete_book(id):
    """Delete user's book."""
    
    return remove_book(id)

# Favorites routes ********************************************************************************************************************************************************

@app.route('/favorite/my-favorites', methods=["GET","POST"])
def favorites():
    """Render favorites page."""

    return my_favorites()

@app.route('/favorite/favorite-subject', methods=["GET","POST"])
def favorite_subject():
    """Generate favorite subject form and handle form submission."""

    return add_favorite_subject()

@app.route('/favorite/favorite-author', methods=["GET","POST"])
def favorite_author():
    """Generate favorite author form and handle form submission."""

    return add_favorite_author()

# favorite delete routes ********************************************************************************************************************************************************

@app.route('/favorite/delete-subject/<int:id>', methods=["GET","DELETE"])
def delete_subject(id):
    """Delete user favorite subject."""
    
    return remove_subject(id)

@app.route('/favorite/delete-author/<int:id>', methods=["GET","DELETE"])
def delete_author(id):
    """Delete user favorite author."""
    
    return remove_author(id)


