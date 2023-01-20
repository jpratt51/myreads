"""Functions for book routes for myreads app."""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User, Book, Review, Rating, ReadDate
from forms import SearchBooksForm, ReviewForm, RatingForm, ReadDatesForm, BookForm
from colors import rand_pastel_color
from search import book_search 
from datetime import date
import string
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# Book functions ********************************************************************************************************************************************************

def book_finder():
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

def my_books():
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

def form_book_entry():
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

def edit_book(book_id):
    """Show book details. Render form to edit book by adding it to a bookshelf, deleting it, rating and leaving a review.
    """

    if "username" not in session:
        flash("Must be logged in", "danger")
        return redirect('/login')

    book = Book.query.get_or_404(book_id)

    return render_template("/book/book-details.html", book=book)

def edit_review(book_id):
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

def edit_rating(book_id):
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

def edit_read_dates(book_id):
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

# Book delete functions ********************************************************************************************************************************************************

def remove_dates(id):
    """Delete read dates for user's book."""
    read_date = ReadDate.query.get_or_404(id)
    db.session.delete(read_date)
    db.session.commit()
    flash("Read dates deleted", "success")
    return redirect('/book/my-books')

def remove_rating(id):
    """Delete rating for user's book."""
    rating = Rating.query.get_or_404(id)
    db.session.delete(rating)
    db.session.commit()
    flash("Rating deleted", "success")
    return redirect('/book/my-books')

def remove_review(id):
    """Delete review for user's book."""
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted", "success")
    return redirect('/book/my-books')

def remove_book(id):
    """Delete user's book."""
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted from library", "success")
    return redirect('/book/my-books')