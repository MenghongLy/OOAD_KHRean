import unittest
from app import create_app, db
from models.user import User
from werkzeug.security import generate_password_hash


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        # In-memory DB for tests
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create test user
            user = User(username="testuser", email="test@example.com", 
                       password=generate_password_hash("testpass"), role="student")
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_login_success(self):
        response = self.client.post(
            "/login", data={"email": "test@example.com", "password": "testpass"}, follow_redirects=True)
        # Check if redirected to dashboard
        self.assertIn(b"dashboard", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            "/login", data={"email": "test@example.com", "password": "wrongpass"}, follow_redirects=True)
        self.assertIn(b"Invalid", response.data)

    def test_login_nonexistent_user(self):
        response = self.client.post(
            "/login", data={"email": "nouser@example.com", "password": "nopass"}, follow_redirects=True)
        self.assertIn(b"Invalid", response.data)


if __name__ == "__main__":
    unittest.main()
