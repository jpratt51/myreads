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

## Getting Started

### Dependencies

This app is a Python app that uses Flask web framework, Flask-SQLAlchemy, and Flask-WTF. Postgresql is used for the database server. For password encryption, this app utilizes Bcrypt. For email verification, myreads. uses Flask mail. All dependency specifics are listed in the requirements.txt file.

## Author

Joel Pratt
contact: joel.a.pratt@gmail.com