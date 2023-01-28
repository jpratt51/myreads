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

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/      | Homepage      |
| GET\/login  | Display user login form|
| POST\/login  | Login user on validate submit with correct credentials |
| GET\/logout  | Logout user |

### Account End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
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
| GET\/register/resend-code  | Resend verification code |
| POST\/register/register  | Add new user to database and login upon successful registration |

### Password Reset End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/password/reset-code     | Display form to verify user's email account for password reset |
| POST\/password/reset-code     | Send verification code to user's email |
| GET\/password/verify-reset-code  | Display form to submit email verification code |
| POST\/password/verify-reset-code  | Submit verification code and redirect to password reset form if verified |
| POST\/password/resend-code'  | Resend verification code to user email for password reset. |
| GET\/password/reset-password  | Display password reset form |
| POST\/password/reset-password  | Reset user password and redirect to login page |

### Book End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/book/find-books | Render user mylibrary page. Generate book search form.  |
| POST\/book/find-books | Handle search form and pass to search results page. |
| GET\/book/my-books | Generate book search form for user's books. |
| POST\/book/my-books | Display search results on html page. |
| GET\/book/add-book | Generate form to manually add book  to database. |
| POST\/book/add-book | Handle form submission, add book to database and update list of user's books. |
| POST\/book/add-book/<book> | Handle form submission, add book to database and update list of user's books. |
| GET\/book/book-details/<book_id> | Show book details. Render form to edit book. |
| GET\/book/review/<book_id> | Render book add/edit review form. |
| POST\/book/review/<book_id> | Handle book review form submission and update database. |
| GET\/book/add-rating/<book_id> | Render book add rating form. |
| POST\/book/add-rating/<book_id> | Handle book rating form submission and update database. |
| GET\/book/rating/<book_id> | Render book edit rating form. |
| POST\/book/rating/<book_id> | Handle book rating form submission and update database. |
| GET\/book/read-dates/<book_id> | Render book add/edit read dates form. |
| POST\/book/read-dates/<book_id> | Handle book read dates form submission and update database. |
| DELETE\/book/delete-read-dates/<id> | Delete selected book read dates. |
| DELETE\/book/delete-rating/<id> | Delete selected book rating. |
| DELETE\/book/delete-review/<id> | Delete selected book review. |
| DELETE\/book/delete-book/<id> | Delete selected user's book. |

### Bookshelf End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/bookshelf/bookshelf-details/<int:bookshelf_id>    | Show details about a specific bookshelf, including name and subject as well as books associated with that bookshelf |
| POST\/bookshelf/bookshelf-details/<int:bookshelf_id>    | Handle form to search for books on user bookshelf and display results |
| GET\/bookshelf/add-book/<int:bookshelf_id>    | Display list of user books to add to bookshelf. Display search form for user's books |
| POST\/bookshelf/add-book/<int:bookshelf_id>    | Handle search form submission for user's books and display search results |
| GET\/bookshelf/update-bookshelf/<int:bookshelf_id>/<int:book_id>  | Query database for book |
| POST\/bookshelf/update-bookshelf/<int:bookshelf_id>/<int:book_id>  | Add book to bookshelf |
| GET\/bookshelf/my-bookshelves | Display form to create new bookshelf and display list of user's current bookshelves |
| POST\/bookshelf/my-bookshelves  | Handle form to create new bookshelf |
| GET\/bookshelf/delete-bookshelf/<int:id>  | Query database for bookshelf |
| DELETE\/bookshelf/delete-bookshelf/<int:id>  | Delete bookshelf |
| GET\/bookshelf/delete-book/<int:id>  | Query database for bookshelf book |
| DELETE\/bookshelf/delete-book/<int:id>  | Delete bookshelf book |

### Favorites End Points

| EndPoint      | Functionality |
| ----------- | ----------- |
| GET\/favorite/my-favorites | Render favorites page. |
| GET\/favorite/favorite-subject | Generate favorite subject form |
| POST\/favorite/favorite-subject | Handle favorite subject form submission and add subject to database. |
| GET\/favorite/favorite-author | Generate favorite author form |
| POST\/favorite/favorite-author | Handle favorite author form submission and add author to database. |
| DELETE\/favorite/delete-subject | Delete user favorite subject |
| DELETE\/favorite/delete-author | Delete user favorite author |

## Prerequisites

1. HTML/CSS
2. Python/Flask
3. PostgreSQL
4. Git and Version Control

## Technologies

- Python 3.7.8
- Flask

## Requirements

- Install [Python](https://www.python.org/downloads/)
- Download [PostgreSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads?gclid=CjwKCAiArNOeBhAHEiwAze_nKP-iOLHK_JbdU0WcIg-GYNorum7ajI6ApZ5ZYO8K1OJNTiWcxu5gkhoCn30QAvD_BwE)
- Code editor such as [VS Code](https://code.visualstudio.com/download)
- An SMTP email account, such as with [SendInBlue](https://account-app.sendinblue.com/account/register/)

## Setup

- Run `psql` on command prompt
- Run `CREATE DATABASE test_db` on command prompt
- Run `\q` on command prompt
- Run `git clone` this repository and `cd` into the project root.
- Open the project app.py file in your code editor.
    - On line 18 of the app.py file, replace 'myreads' with 'test_db'. Do the same for line 10 of account.py, line 14 of book.py, line 12 of bookshelf.py, line 11 of favorite.py, line 14 of password.py and line 12 of register.py 
    - On line 20 of the app.py file, change 'app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')' to 'app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secretkey')' or set whatever secret key you like. Follow this same step for line 12 of account.py, line 16 of book.py, line 14 of bookshelf.py, line 13 of favorite.py, line 16 of password.py and line 14 of register.py
    - On line 17 of register.py, change the mail server to your smtp email server
    - On line 19 of register.py, add a default mail username as your smtp email address
    - On line 20 of register.py, add a default mail password as your smtp email password
    - Save all changes and return to command prompt
- Run `python3 -m venv venv` on command prompt
- Run `source venv/bin/activate` on command prompt
- Run `pip install -r requirements.txt` on command prompt
- Run `set FLASK_CONFIG=development` on command prompt
- Run `flask run` on command prompt
- View the app on `http://127.0.0.1:5000/`

## Unittests

- Run `python -m unittest` on command prompt 

## Heroku

View this website at [myreads.herokuapp.com](myreads.herokuapp.com)
