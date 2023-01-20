# myreads.

A personal library app to keep a record of books you've read/want to read. 

## Project Description

myreads. allows users to: 

- Users can register an account and log in
- search for books utlizing the open library API
- add and delete books from mylibrary.
- create and delete reviews, ratings, and read dates for books in mylibrary.
- create and delete bookshelves
- add and remove books from those bookshelves
- create and delete favorite authors and subjects
- edit and delete user account

## End Points
### Account End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/      | Homepage      |
| GET\/login  | Display user login form|
| POST\/login  | Login user on validate submit with correct credentials |
| GET\/logout  | Logout user |
| GET\/account/my-account  | Display user account details |
| GET\/account/update-img/<username>  | Display form to update user profile image |
| POST\/account/update-img/<username>  | Update user profile image to database |
| DELETE\/account/delete-user/<username>  | Delete user account |

### Registration End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/register/register      | Display form to register user if email has been validated, otherwise redirect to send-code form to validate email   |
| GET\/register/send-code  | Display form for user to submit email address and receive validation code |
| POST\/register/send-code  | Submit form and email validation code to user's email |
| GET\/register/verify-code  | Display form for user to enter validation code |
| POST\/register/verify-code  | Display form for user to enter validation code |
| GET\/account/my-account  | Display user account details |
| GET\/account/update-img/<username>  | Display form to update user profile image |
| POST\/account/update-img/<username>  | Update user profile image to database |
| DELETE\/account/delete-user/<username>  | Delete user account |

## Getting Started

### Dependencies

This app is a Python app that uses Flask web framework, Flask-SQLAlchemy, and Flask-WTF. Postgresql is used for the database server. For password encryption, this app utilizes Bcrypt. For email verification, myreads. uses Flask mail. All dependency specifics are listed in the requirements.txt file.

## Author

Joel Pratt
contact: joel.a.pratt@gmail.com