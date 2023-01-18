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

app = Flask(__name__)

bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///myreads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'verysecret')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'myreadsverify@gmail.com'
app.config['MAIL_PASSWORD'] = 'vvztohuzogykuahh'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

verify_code = 0
verified = False
user_email = ""

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
        return render_template('/account/my-homepage.html', user=user, users=users, num_books=num_books, num_shelves=num_shelves, last_review=last_review)
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

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)

    return render_template('/account/my-account.html', user=user)

@app.route('/account/update-img/<username>', methods=["GET","POST"])
def update_img(username):
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

@app.route('/account/delete-user/<username>', methods=["GET", "DELETE"])
def delete_user(username):
    """Delete user account."""
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    
    session.pop('username')
    flash("Account deleted. Goodbye!", "success")
    return redirect('/')

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

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    bookshelf = Bookshelf.query.get_or_404(bookshelf_id)
    username = session["username"]
    user = User.query.get_or_404(username)
    form = SearchBooksForm()

    if form.validate_on_submit():
        book_title = form.book_title.data or ""
        book_author = form.author.data or ""
        title = string.capwords(book_title)
        author = string.capwords(book_author)

        if len(title) == 0 and len(author) == 0:
            flash("Please enter book title and/or author", "danger")
            return redirect ("/book/my-books")

        elif len(title) > 0 and len(author) > 0:
            t = "%{}%".format(title)
            a = "%{}%".format(author)
            books = Bookshelf.query.filter(Bookshelf.user_username == username, Bookshelf.books.title.like(t), Bookshelf.books.author.like(a)).all()
            return render_template ("/bookshelf/bookshelf-search-results.html", user=user, books=books, bookshelf=bookshelf, form=form)

        elif len(title) > 0 and len(author) == 0:
            t = "%{}%".format(title)
            books = Book.query.filter(Book.user_username == username, Book.title.like(t)).all()
            print(t)
            return render_template ("/bookshelf/bookshelf-search-results.html", user=user, books=books, bookshelf=bookshelf, form=form)
        
        elif len(title) == 0 and len(author) > 0:
            a = "%{}%".format(author)
            books = Book.query.filter(Book.user_username == username, Book.author.like(a)).all()
            return render_template ("/bookshelf/bookshelf-search-results.html", user=user, books=books, bookshelf=bookshelf, form=form)
    return render_template("/bookshelf/bookshelf-details.html", bookshelf=bookshelf, user=user, form=form)

@app.route('/bookshelf/add-bookshelf-book/<int:bookshelf_id>', methods=["GET", "POST"])
def add_bookshelf_book(bookshelf_id):
    """Display list of user books to add to bookshelf."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    bookshelf = Bookshelf.query.get_or_404(bookshelf_id)
    username = session["username"]
    user = User.query.get_or_404(username)
    form = SearchBooksForm()

    if form.validate_on_submit():
        book_title = form.book_title.data or ""
        book_author = form.author.data or ""
        title = string.capwords(book_title)
        author = string.capwords(book_author)

        if len(title) == 0 and len(author) == 0:
            flash("Please enter book title and/or author", "danger")
            return redirect (f"/bookshelf/add-bookshelf-book/{bookshelf_id}")

        elif len(title) > 0 and len(author) > 0:
            t = "%{}%".format(title)
            a = "%{}%".format(author)
            books = Bookshelf.query.filter(Bookshelf.user_username == username, Bookshelf.books.title.like(t), Bookshelf.books.author.like(a)).all()
            return render_template("/bookshelf/add-bookshelf-book.html", user=user, books=books, bookshelf=bookshelf, form=form)

        elif len(title) > 0 and len(author) == 0:
            t = "%{}%".format(title)
            books = Book.query.filter(Book.user_username == username, Book.title.like(t)).all()
            print(t)
            return render_template("/bookshelf/add-bookshelf-book.html", user=user, books=books, bookshelf=bookshelf, form=form)
        
        elif len(title) == 0 and len(author) > 0:
            a = "%{}%".format(author)
            books = Book.query.filter(Book.user_username == username, Book.author.like(a)).all()
            return render_template("/bookshelf/add-bookshelf-book.html", user=user, books=books, bookshelf=bookshelf, form=form)
    return render_template("/bookshelf/add-bookshelf-book.html", bookshelf=bookshelf, user=user, form=form)

@app.route("/bookshelf/update-bookshelf/<int:bookshelf_id>/<int:book_id>", methods=["GET","POST"])
def update_bookshelf(bookshelf_id, book_id):
    """Add book to bookshelf."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')
    
    bookshelf = Bookshelf.query.get_or_404(bookshelf_id)
    book = Book.query.get_or_404(book_id)

    bookshelf_book = BookshelfBook(bookshelf_id=bookshelf_id, book_id=book_id)

    db.session.add(bookshelf_book)
    db.session.commit()
    flash(f"Successfully added book '{book.title}' to bookshelf '{bookshelf.name}'", "success")
    return redirect(f'/bookshelf/add-bookshelf-book/{bookshelf_id}')

@app.route('/bookshelf/my-bookshelves', methods=['GET','POST'])
def bookshelves():
    """Render form to create new bookshelf and display list of user's current bookshelves. """
    
    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)

    form = BookshelfForm()
    if form.validate_on_submit():

        name = form.name.data
        subject = form.subject.data or ""
        color = rand_primary_color()
        
        new_bookshelf = Bookshelf(user_username=username, name=name, subject=subject, color=color)

        db.session.add(new_bookshelf)
        db.session.commit()
        flash(f'Created bookshelf: {name}', "success")
        return redirect('/bookshelf/my-bookshelves')
    return render_template("/bookshelf/my-bookshelves.html", form=form, user=user)

@app.route("/book/add-book", methods=["GET","POST"])
def manual_book_entry():
    """Generate and handle form to add book manually to database and update list of user's books."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    form = BookForm()
    username = session["username"]
    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        username = session["username"]
        title = form.title.data
        author = form.author.data
        color = rand_pastel_color()

        if form.subject.data:
            subject = form.subject.data
        else:
            subject = ""
        
        if form.publish_year.data:
            publish_year = form.publish_year.data
        else:
            publish_year = ""

        cap_title = string.capwords(title)
        cap_author = string.capwords(author)

        new_book = Book(user_username=username, title=cap_title, author=cap_author, subject=subject, publish_year=publish_year, color=color)

        db.session.add(new_book)
        db.session.commit()
        flash(f'{title} added to library', "success")
        return redirect(f'/book/find-books')
    return render_template('/book/add-book.html', form=form, user=user)

@app.route("/bookshelf/add-book/<book>", methods=["GET","POST"])
def add_book(book):
    """Generate and handle form to add book to database and update list of user's books."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    try:
        dict = eval(book)
    except SyntaxError:
        flash("Oops, something went wrong! Please try again", "info")
        return redirect("/book/find-books")

    username = session["username"]
    title = dict['title']
    author = dict['author_name']
    subject = dict['subject']
    publish_year = dict['first_publish_year']
    color = dict['color']

    cap_title = string.capwords(title)
    cap_author = string.capwords(author)

    new_book = Book(user_username=username, title=cap_title, author=cap_author, subject=subject, publish_year=publish_year, color=color)

    db.session.add(new_book)
    db.session.commit()
    flash(f'{title} added to library', "success")
    return redirect(f'/book/find-books')

# bookshelf delete routes ********************************************************************************************************************************************************

@app.route('/bookshelf/delete-bookshelf/<int:id>', methods=["GET","DELETE"])
def delete_bookshelf(id):
    """Delete user's bookshelf."""
    bookshelf = Bookshelf.query.get_or_404(id)
    db.session.delete(bookshelf)
    db.session.commit()
    flash("Deleted bookshelf", "success")
    return redirect('/bookshelf/my-bookshelves')

@app.route('/bookshelf/delete-bookshelf-book/<bookshelfid>/<bookid>', methods=["GET","DELETE"])
def delete_bookshelf_book(bookshelfid, bookid):
    """Delete book from bookshelf."""
    bookshelf_book = BookshelfBook.query.filter_by(bookshelf_id=bookshelfid, book_id=bookid).one_or_none()
    db.session.delete(bookshelf_book)
    db.session.commit()
    flash("Book removed from bookshelf", "success")
    return redirect('/bookshelf/my-bookshelves')

# Book routes ********************************************************************************************************************************************************

@app.route("/book/find-books", methods=['GET', 'POST'])
def mylibrary():
    """Render user mylibrary page. Generate book search form. Handle search form and pass to search results page."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    else:
        form = SearchBooksForm()

        if form.validate_on_submit():
            book_title = form.book_title.data or ""
            author = form.author.data or ""

            if len(book_title) == 0 and len(author) == 0:
                flash("Please enter book title and/or author", "danger")
                return redirect ("/mylibrary")
  
            book_list = book_search(book_title, author)
            return render_template("/book/search-results.html", books=book_list, form=form)
            
        return render_template("/book/find-books.html", form=form)

@app.route('/book/my-books', methods=['GET','POST'])
def user_books():
    """Shows list of books associated with user. 
    Generate book search form for user's books."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)
    form = SearchBooksForm()

    if form.validate_on_submit():
        book_title = form.book_title.data or ""
        book_author = form.author.data or ""
        title = string.capwords(book_title)
        author = string.capwords(book_author)

        if len(title) == 0 and len(author) == 0:
            flash("Please enter book title and/or author", "danger")
            return redirect ("/book/my-books")

        elif len(title) > 0 and len(author) > 0:
            t = "%{}%".format(title)
            a = "%{}%".format(author)
            books = Book.query.filter(Book.user_username == username, Book.title.like(t), Book.author.like(a)).all()
            return render_template ("/book/my-books.html", user=user, books=books, form=form)

        elif len(title) > 0 and len(author) == 0:
            t = "%{}%".format(title)
            books = Book.query.filter(Book.user_username == username, Book.title.like(t)).all()
            print(t)
            return render_template ("/book/my-books.html", user=user, books=books, form=form)
        
        elif len(title) == 0 and len(author) > 0:
            a = "%{}%".format(author)
            books = Book.query.filter(Book.user_username == username, Book.author.like(a)).all()
            return render_template ("/book/my-books.html", user=user, books=books, form=form)
    return render_template("/book/my-books.html", user=user, form=form)

@app.route('/book/book-details/<int:book_id>', methods=['GET','POST'])
def edit_book(book_id):
    """Show book details. Render form to edit book by adding it to a bookshelf, deleting it, rating and leaving a review.
    """

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    book = Book.query.get_or_404(book_id)

    return render_template("/book/book-details.html", book=book)

@app.route("/book/review/<int:book_id>", methods=['GET','POST'])
def book_review(book_id):
    """Render and handle form to add/update user book review. """
    
    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)
    book = Book.query.get_or_404(book_id)

    form = ReviewForm()
    if form.validate_on_submit():
        if book.review:
            book_review = book.review
            for review in book_review :
                review.text = form.review.data
            db.session.commit()
            flash('Review updated successfully', "success")
            return redirect(f'/book/book-details/{book_id}')
        text = form.review.data
        review = Review(user_username=username, book_id=book_id, text=text)
        db.session.add(review)
        db.session.commit()
        flash('Review created successfully', "success")
        return redirect(f'/book/book-details/{book_id}')
    return render_template("/book/review.html", form=form, user=user, book=book)

@app.route("/book/rating/<int:book_id>", methods=['GET','POST'])
def book_rating(book_id):
    """Render and handle form to add/update user book rating. """
    
    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)
    book = Book.query.get_or_404(book_id)

    form = RatingForm()
    if form.validate_on_submit():
        if book.rating:
            book_rating = book.rating
            for rating in book_rating :
                rating.rating = form.rating.data
            db.session.add(book)
            db.session.commit()
            flash('Rating updated successfully', "success")
            return redirect(f'/book/book-details/{book_id}')
        rating = form.rating.data
        rating = Rating(user_username=username, book_id=book_id, rating=rating)
        db.session.add(rating)
        db.session.commit()
        flash('Review created successfully', "success")
        return redirect(f'/book/book-details/{book_id}')
    return render_template("/book/rating.html", form=form, user=user, book=book)

@app.route("/book/add-rating/<int:book_id>/<book_rating>", methods=['GET','POST'])
def add_rating(book_id, book_rating):
    """Add/update book rating. """
    
    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    book = Book.query.get_or_404(book_id)


    if book.rating:
        for rating in book.rating:
            rating.rating = str(book_rating)
            print(rating, "*******************************************************")
            db.session.commit()
            flash('Rating updated successfully', "success")
            return redirect(f'/book/book-details/{book_id}')
    new_rating = Rating(user_username=username, book_id=book_id, rating=book_rating)
    db.session.add(new_rating)
    db.session.commit()
    flash('Rating created successfully', "success")
    return redirect(f'/book/book-details/{book_id}')


@app.route("/book/read-dates/<int:book_id>", methods=['GET','POST'])
def book_read_dates(book_id):
    """Render and handle form to add/update user book read dates. Accepts either start date or end date or both."""
    
    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)
    book = Book.query.get_or_404(book_id)

    form = ReadDatesForm()
    if form.validate_on_submit():
        today = date.today()
        if form.start_date.data and form.end_date.data:
            if form.end_date.data > today :
                flash("End date must be on or before current date", "danger")
                return redirect(f"/book/read-dates/{book_id}")
            elif form.start_date.data > form.end_date.data :
                flash("Start date must be on or before end date", "danger")
                return redirect(f"/book/read-dates/{book_id}")
        if book.read_dates:
            book_read_dates = book.read_dates
            for read_date in book_read_dates :
                if form.start_date.data:
                    read_date.start_date = str(form.start_date.data)
                if form.end_date.data:
                    read_date.end_date = str(form.end_date.data)

            db.session.commit()

            flash('Read dates updated successfully', "success")
            return redirect(f'/book/book-details/{book_id}')

        if form.start_date.data:
            start_date = str(form.start_date.data)
        else:
            start_date = ""
        if form.end_date.data:
            end_date = str(form.end_date.data)
        else:
            end_date = ""
        
        rating = ReadDate(user_username=username, book_id=book_id, start_date=start_date, end_date=end_date)

        db.session.add(rating)
        db.session.commit()
        flash('Read dates created successfully', "success")
        return redirect(f'/book/book-details/{book_id}')
    return render_template("/book/read-dates.html", form=form, user=user, book=book)

# book delete routes ********************************************************************************************************************************************************

@app.route('/book/delete-read-dates/<int:id>', methods=["GET","DELETE"])
def delete_read_dates(id):
    """Delete read dates for user's book."""
    read_date = ReadDate.query.get_or_404(id)
    db.session.delete(read_date)
    db.session.commit()
    flash("Read dates deleted", "success")
    return redirect('/book/my-books')

@app.route('/book/delete-rating/<int:id>', methods=["GET","DELETE"])
def delete_rating(id):
    """Delete rating for user's book."""
    rating = Rating.query.get_or_404(id)
    db.session.delete(rating)
    db.session.commit()
    flash("Rating deleted", "success")
    return redirect('/book/my-books')

@app.route('/book/delete-review/<int:id>', methods=["GET","DELETE"])
def delete_review(id):
    """Delete review for user's book."""
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted", "success")
    return redirect('/book/my-books')

@app.route('/book/delete-book/<int:id>', methods=["GET","DELETE"])
def delete_book(id):
    """Delete user's book."""
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted from library", "success")
    return redirect('/book/my-books')

# Favorites routes ********************************************************************************************************************************************************

@app.route('/favorite/my-favorites', methods=["GET","POST"])
def favorites():
    """Render favorites page."""

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    username = session["username"]
    user = User.query.get_or_404(username)

    return render_template("/favorite/my-favorites.html", user=user)

@app.route('/favorite/favorite-subject', methods=["GET","POST"])
def favorite_subject():
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
    return render_template("favorite-subject.html", user=user, form=form)

@app.route('/favorite/favorite-author', methods=["GET","POST"])
def favorite_author():
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

@app.route('/favorite/delete-subject/<int:id>', methods=["GET","DELETE"])
def delete_subject(id):
    """Delete user favorite subject."""
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Deleted subject from favorites", "success")
    return redirect('/favorites')

@app.route('/favorite/delete-author/<int:id>', methods=["GET","DELETE"])
def delete_author(id):
    """Delete user favorite author."""
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    flash("Deleted author from favorites", "success")
    return redirect('/favorites')




