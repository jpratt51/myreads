import unittest

from flask import session
from app import app
from models import db, connect_db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_myreads'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

connect_db(app)

class UserViewsTestCase(unittest.TestCase):
    """Tests for views for User."""

    def setUp(self):
        """Add sample user."""
        with app.app_context():
            db.create_all()

            user = User(username='jpratt', first_name='Joel', last_name='Pratt', email='joel.a.pratt@gmail.com', password='verysecret', img_url="https://i.ibb.co/g9qb6Ss/Joel-Profile-Pic.jpg")

            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction and delete all tables."""
        with app.app_context():
            db.session.rollback()
            db.drop_all()

    def test_1_home_page(self):
        """Test status code for homepage route for logged out user. Check that it correctly displays html."""
        with app.test_client() as client:
            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to myreads!', html)

    def test_2_user_home_page(self):
        """Test root route redirects to user homepage for logged in user and correctly displays html. Also test for 200 status code."""
        with app.test_client() as client:
            client.post('/login', data=dict(
                username='jpratt',
                password='verysecret'
            ), follow_redirects=True)

            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn('username', session)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('myprofile.', html)

    def test_3_find_books(self):
        """Test status code for find-books route for logged in user. Check that it correctly displays html."""
        with app.test_client() as client:
            client.post('/login', data=dict(
                username='jpratt',
                password='verysecret'
            ), follow_redirects=True)

            resp = client.get('/book/find-books')
            html = resp.get_data(as_text=True)

            self.assertIn('username', session)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search for books by author or title (or both)', html)

    def test_4_my_books(self):
        """Test status code for my-books route for logged in user. Check that it correctly displays html."""
        with app.test_client() as client:
            client.post('/login', data=dict(
                username='jpratt',
                password='verysecret'
            ), follow_redirects=True)

            resp = client.get('/book/my-books')
            html = resp.get_data(as_text=True)

            self.assertIn('username', session)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('View and delete your books here.', html)

    def test_5_my_bookshelves(self):
        """Test status code for bookshelves route for logged in user. Check that it correctly displays html."""
        with app.test_client() as client:
            client.post('/login', data=dict(
                username='jpratt',
                password='verysecret'
            ), follow_redirects=True)

            resp = client.get('/bookshelf/my-bookshelves')
            html = resp.get_data(as_text=True)

            self.assertIn('username', session)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('View, create, and delete your bookshelves here.', html)

    def test_6_my_favorites(self):
        """Test status code for my-favorites route for logged in user. Check that it correctly displays html."""
        with app.test_client() as client:
            client.post('/login', data=dict(
                username='jpratt',
                password='verysecret'
            ), follow_redirects=True)

            resp = client.get('/favorite/my-favorites')
            html = resp.get_data(as_text=True)

            self.assertIn('username', session)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('View, update, and delete your favorite subjects and authors here.', html)

    def test_7_my_account(self):
        """Test status code for my-favorites route for logged in user. Check that it correctly displays html."""
        with app.test_client() as client:
            client.post('/login', data=dict(
                username='jpratt',
                password='verysecret'
            ), follow_redirects=True)

            resp = client.get('/account/my-account')
            html = resp.get_data(as_text=True)

            self.assertIn('username', session)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('View your account info here.', html)

    # def test_2_login(self):
    #     """Test correctly routing to login route and displays correct html."""
    #     with app.test_client() as client:
    #         resp = client.get('/', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Click here to register', html)

    # def test_3_login(self):
    #     """Test correctly logs in user with correct credentials, redirects to user homepage, and displays correct html. """
    #     resp = login(self)
    #     html = resp.get_data(as_text=True)

    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn('myprofile.', html)

    # def test_login(self):
    #     """Test login route redirects to user homepage with correct credentials entry."""
    #     rv = self.login('jpratt', 'verysecret')
    #     print(rv.data)
    #     rv = self.app.get('/',follow_redirects=True)
    #     print(rv.data)

# if __name__ == '__main__':
#     unittest.main()
        # resp = self.login('username', 'verysecret')
                
        # html = resp.get_data(as_text=True)

        # self.assertEqual(resp.status_code, 200)
        # self.assertIn('myprofile.', html)


    # def test_users_page(self):
    #     """Test redirects to users page and correctly displays html"""
    #     with app.test_client() as client:
    #         resp = client.get("/", follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('myprofile.', html)

    # def test_user_details_page(self):
    #     """Test correctly routing to user details page and displays user name"""
    #     with app.test_client() as client:
    #         resp = client.get(f"/users/{self.users_id}")
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Alan Alda', html)

    # def test_edit_user_form(self):
    #     """Test correctly routing to user edit page and displays correct html"""
    #     with app.test_client() as client:
    #         resp = client.get(f"/users/{self.users_id}/edit")
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('<h1>Edit User</h1>', html)

    # def test_add_user(self):
    #     with app.test_client() as client:

    #         d = {"first_name": "Joel", "last_name": "Burton", "img_url": "https://media.istockphoto.com/photos/portrait-smiling-african-american-businessman-in-blue-suit-sit-at-picture-id1341347262?b=1&k=20&m=1341347262&s=170667a&w=0&h=nWVSejAWgPgQi128JMemYKX0YX9xUgf18Nd3o4Ez6ic="}

    #         resp = client.post("/users/new", data=d, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Joel Burton", html)

    # def test_add_post_page(self):
    #     with app.test_client() as client:
    #         resp = client.get(f"/users/{self.users_id}/new-post")
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Add Post for Alan Alda', html)

    # def test_post_details(self):
    #     with app.test_client() as client:
    #         d = {"title": "Famouse Quote", "content": "'Fortune favors the bold.' -Virgil"}

    #         resp = client.post(f"/users/{self.users_id}/new-post", data=d, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Famouse Quote', html)