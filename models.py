"""SQLAlchemy models for myreads."""

import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

email_code = None

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.Text)

    # Relationships
    # If a user is deleted, erase all bookshelves, books, favorite subjects, and favorite authors associated with that user.

    bookshelves = db.relationship("Bookshelf", backref="user", cascade="all, delete-orphan")

    books = db.relationship("Book", backref="user", cascade="all, delete-orphan")

    subjects = db.relationship("Subject", backref="user", cascade="all, delete-orphan")

    authors = db.relationship("Author", backref="user", cascade="all, delete-orphan")

    # @property
    # def full_name(self):
    #     """Return full name of user."""

    #     return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls, username, first_name, last_name, email, password, img_url):
        """Register user w/hashed password & return user."""

        # Generate hashed password so user password is stored securly in database
        hashed = bcrypt.generate_password_hash(password)
        
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, first_name=first_name, last_name=last_name, email=email, password=hashed_utf8, img_url=img_url)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()
        test = User.query.filter_by(password=pwd).first()

        if (user and not test):
            if user and bcrypt.check_password_hash(user.password, pwd):
                # return user instance
                return user
        if (user and test):
            return test
        else:
            return False


class Bookshelf(db.Model):
    """User's bookshelf."""

    __tablename__ = "bookshelves"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    name = db.Column(db.String(30), nullable=False)
    subject = db.Column(db.String(30))
    color = db.Column(db.Text)

    books = db.relationship('Book', secondary="bookshelves_books", backref="bookshelf")

class Book(db.Model):
    """User's books."""

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    subject = db.Column(db.Text)
    publish_year = db.Column(db.Text)
    color = db.Column(db.Text)

    # If a user removes a book, erase all reviews, ratings, and read_dates associated with that book

    review = db.relationship("Review", backref="book", cascade="all, delete-orphan")

    rating = db.relationship("Rating", backref="book", cascade="all, delete-orphan")

    read_dates = db.relationship("ReadDate", backref="book", cascade="all, delete-orphan")

class BookshelfBook(db.Model):
    """Book on a bookshelf."""

    __tablename__ = "bookshelves_books"

    bookshelf_id = db.Column(db.Integer, db.ForeignKey('bookshelves.id', ondelete="CASCADE"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="CASCADE"), primary_key=True)

class Subject(db.Model):
    """User's favorite reading subjects."""

    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    name = db.Column(db.String(30), nullable=False)
    color = db.Column(db.Text)

class Author(db.Model):
    """User's favorite authors."""

    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    name = db.Column(db.String(30), nullable=False)
    color = db.Column(db.Text)

class Review(db.Model):
    """Reviews for user's books."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now)
    
    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p")

class Rating(db.Model):
    """Ratings for user's books."""

    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    rating = db.Column(db.Integer, nullable=False)

class ReadDate(db.Model):
    """Read dates for user's books."""

    __tablename__ = "read_dates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.Text, db.ForeignKey('users.username'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)