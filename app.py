"""Flask app for myreads."""

from flask import Flask, redirect, session, flash, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Book, Bookshelf, Review
from forms import LoginForm
from colors import rand_pastel_color
import os
from book import *
from bookshelf import *
from favorite import *
from account import *
from register import *
from password import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

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
    if "code" in session:
        session.pop('code')
    if "email" in session:
        session.pop('email')
    if "verified" in session:
        session.pop('verified')
    flash("Goodbye!", "info")
    return redirect('/')

# account routes (account functions located in account.py) ********************************************************************************************************************************************************

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

# registration routes (registration functions located in register.py)
# *************************************************************************
# *************************************************************************

@app.route('/register/register', methods=["GET", "POST"])
def register_user():
    """Generate form to register new user.

    Upon successful registration add new user username to session for login."""

    return register_account()

@app.route("/register/send-code", methods=["GET","POST"])
def send_code():
    """Generate form to verify user's email account. Sends six digit code to user's email for verification."""

    return send_verification_code()

@app.route('/register/resend-code')
def resend_verification_code():
    """Resend verification code to user email for registration."""

    return resend_email_code()

@app.route("/register/verify-code", methods=["GET","POST"])
def code_verification():
    """Generate form to submit code for email verification for registration."""
    
    return submit_code()

# Password reset routes (password reset functions located in password.py) ********************************************************************************************************************************************************

@app.route("/password/reset-code", methods=["GET","POST"])
def reset_code():
    """Generate form to verify user's email account. Sends six digit code to users email that will be used to complete password reset."""
    
    return send_reset_code()

@app.route("/password/verify-reset-code", methods=["GET","POST"])
def verify_reset_code():
    """Generate form to submit code for email verification for password reset."""
    
    return submit_reset_code()

@app.route('/password/resend-code')
def resend_reset_code():
    """Resend verification code to user email for password reset."""
    
    return submit_resent_code()

@app.route('/password/reset-password', methods=["GET", "POST"])
def reset_password():
    """Generate form to reset user password.

    Reset user password in database and redirect user to login page."""

    return password_reset()

# Bookshelf routes (bookshelf functions located in bookshelf.py)
# **************************************************************************
# **************************************************************************

@app.route('/bookshelf/bookshelf-details/<int:bookshelf_id>', methods=['GET','POST'])
def bookshelf_details(bookshelf_id):
    """Show details about a specific bookshelf, including name and subject as well as books associated with that bookshelf.
    
    Handle form to search for books on user bookshelf and display results."""

    return view_bookshelf_details(bookshelf_id)

@app.route('/bookshelf/add-book/<int:bookshelf_id>', methods=["GET", "POST"])
def add_bookshelf_book(bookshelf_id):
    """Display list of user books to add to bookshelf.
    
    Handle search form submission and display search results."""

    return bookshelf_add_book(bookshelf_id)

@app.route("/bookshelf/update-bookshelf/<int:bookshelf_id>/<int:book_id>", methods=["GET","POST"])
def update_bookshelf(bookshelf_id, book_id):
    """Add book to bookshelf."""

    return add_to_bookshelf(bookshelf_id, book_id)

@app.route('/bookshelf/my-bookshelves', methods=['GET','POST'])
def bookshelves():
    """Render form to create new bookshelf and display list of user's current bookshelves. """
    
    return my_bookshelves()

# bookshelf delete routes ********************************************************************************************************************************************************

@app.route('/bookshelf/delete-bookshelf/<int:id>', methods=["GET","DELETE"])
def delete_bookshelf(id):
    """Delete user's bookshelf."""
    
    return remove_bookshelf(id)

@app.route('/bookshelf/delete-book/<bookshelfid>/<bookid>', methods=["GET","DELETE"])
def delete_bookshelf_book(bookshelfid, bookid):
    """Delete book from bookshelf."""
    
    return remove_bookshelf_book(bookshelfid, bookid)

# book routes (book functions located in book.py) ********************************************************************************************************************************************************

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

@app.route("/book/add-book/<book>", methods=["POST"])
def add_book(book):
    """Add book to database."""

    return add_library_book(book)

@app.route('/book/book-details/<int:book_id>', methods=['GET'])
def book_details(book_id):
    """Show book details. Render form to edit book by adding it to a bookshelf, deleting it, rating and leaving a review.
    """

    return book_details_page(book_id)

@app.route("/book/review/<int:book_id>", methods=['GET','POST'])
def book_review(book_id):
    """Render and handle form to add/update user book review. """
    
    return edit_review(book_id)

@app.route("/book/add-rating/<int:book_id>/<book_rating>", methods=['GET','POST'])
def add_book_rating(book_id, book_rating):
    """Add/update book rating. """
    
    return add_rating(book_id, book_rating)

@app.route("/book/rating/<int:book_id>", methods=['GET','POST'])
def edit_book_rating(book_id):
    """Render and handle form to add/update user book rating. """
    
    return edit_rating(book_id)

@app.route("/book/read-dates/<int:book_id>", methods=['GET','POST'])
def book_read_dates(book_id):
    """Render and handle form to add/update user book read dates. Accepts either start date or end date or both."""
    
    return edit_read_dates(book_id)

# book delete routes ********************************************************************************************************************************************************

@app.route('/book/delete-read-dates/<int:id>', methods=["GET","DELETE"])
def delete_read_dates(id):
    """Find and delete read dates for user's book."""
    
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

# Favorites routes (favorites functions located in favorite.py) ********************************************************************************************************************************************************

@app.route('/favorite/my-favorites', methods=["GET"])
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


