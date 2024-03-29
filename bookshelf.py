"""Functions for bookshelf routes for myreads app."""

from flask import Flask, redirect, session, flash, render_template
from models import db, connect_db, User, Book, Bookshelf, BookshelfBook
from forms import SearchBooksForm, BookshelfForm
from colors import rand_primary_color
import string
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL_URL', 'postgresql:///myreads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# Bookshelf functions
# **************************************************************************
# **************************************************************************

def view_bookshelf_details(bookshelf_id):
    """Show details about a specific bookshelf, including name and subject as well as books associated with that bookshelf.
    
    Handle form to search for books on user bookshelf and display results."""

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

def bookshelf_add_book(bookshelf_id):
    """Display list of user books to add to bookshelf. Display search form for user books.
    
    Handle search form submission and display search results."""

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
            return redirect (f"/bookshelf/add-book/{bookshelf_id}")

        elif len(title) > 0 and len(author) > 0:
            t = "%{}%".format(title)
            a = "%{}%".format(author)
            books = Bookshelf.query.filter(Bookshelf.user_username == username, Bookshelf.books.title.like(t), Bookshelf.books.author.like(a)).all()
            return render_template("/bookshelf/add-book.html", user=user, books=books, bookshelf=bookshelf, form=form)

        elif len(title) > 0 and len(author) == 0:
            t = "%{}%".format(title)
            books = Book.query.filter(Book.user_username == username, Book.title.like(t)).all()
            print(t)
            return render_template("/bookshelf/add-book.html", user=user, books=books, bookshelf=bookshelf, form=form)
        
        elif len(title) == 0 and len(author) > 0:
            a = "%{}%".format(author)
            books = Book.query.filter(Book.user_username == username, Book.author.like(a)).all()
            return render_template("/bookshelf/add-book.html", user=user, books=books, bookshelf=bookshelf, form=form)
    return render_template("/bookshelf/add-book.html", bookshelf=bookshelf, user=user, form=form)

def add_to_bookshelf(bookshelf_id, book_id):
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
    return redirect(f'/bookshelf/add-book/{bookshelf_id}')

def my_bookshelves():
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

# bookshelf delete routes ********************************************************************************************************************************************************

def remove_bookshelf(id):
    """Delete user's bookshelf."""
    bookshelf = Bookshelf.query.get_or_404(id)
    db.session.delete(bookshelf)
    db.session.commit()
    flash("Deleted bookshelf", "success")
    return redirect('/bookshelf/my-bookshelves')

def remove_bookshelf_book(bookshelfid, bookid):
    """Delete book from bookshelf."""
    bookshelf_book = BookshelfBook.query.filter_by(bookshelf_id=bookshelfid, book_id=bookid).one_or_none()
    db.session.delete(bookshelf_book)
    db.session.commit()
    flash("Book removed from bookshelf", "success")
    return redirect(f'/bookshelf/bookshelf-details/{bookshelfid}')