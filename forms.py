"""Flask-wtforms for myreads."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, DateField, RadioField
from wtforms.validators import InputRequired, Email, Length, ValidationError, Optional


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8)])
    img_url = StringField("Image URL (Optional, direct link only)")

class UpdateImgForm(FlaskForm):
    img_url = StringField("Image URL", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class BookshelfForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    subject = StringField("Subject (optional)", validators=[Length(max=30)])

class BookForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(message="Must provide book title")])
    author = StringField("Author", validators=[InputRequired(message="Must provide book author")])
    subject = StringField("Subject (optional)")
    publish_year = StringField("Publish Year (optional)")

class SubjectForm(FlaskForm):
    name = StringField("Subject", validators=[InputRequired(), Length(max=30)])

class AuthorForm(FlaskForm):
    name = StringField("Author Name", validators=[InputRequired(), Length(max=30)])

class ReviewForm(FlaskForm):
    review = StringField("Review")

class RatingForm(FlaskForm):
    rating = RadioField("Rating(1-5)", choices=[1,2,3,4,5], validators=[InputRequired()])

class ReadDatesForm(FlaskForm):
    start_date = DateField("Start Date", format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField("End Date", format='%Y-%m-%d', validators=[Optional()])

    def validate_enddate_field(form, field):
        if field.end_date.data < form.startdate_field.data:
            raise ValidationError("End date must not be earlier than start date.")

class SendCodeForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(message="Must provide valid email")])

class VerifyEmailForm(FlaskForm):
    code = IntegerField("Code", validators=[InputRequired()])

class SearchBooksForm(FlaskForm):
    book_title = StringField("Book Title")
    author = StringField("Author")

class ResetPasswordForm(FlaskForm):
    password = StringField("New Password")
    



