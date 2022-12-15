"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///seiyuulist-test"

DEFAULT_IMAGE="/static/no-image.png"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for the User Model"""

    def setUp(self):
        """Create test client and add some data"""
        db.drop_all()
        db.create_all()

        u1 = User.signup("user1", "user1@test.com", 'password1', None)
        u1_id = 11111
        u1.id = u1_id

        db.session.commit()

        self.u1 = u1
        self.u1_id = u1_id

        self.client = app.test_client()
  
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Test if we can add the basic model"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

# Sign Up Tests
    def test_valid_signup(self):
        test_user_id = '12345'
        test_username = 'testuser1'
        test_email = 'testuser1@test.com'
        test_password = 'testpassword1'
        test_image = None

        test_user = User.signup(test_username, test_email, test_password, test_image)
        test_user.id = test_user_id

        db.session.commit()

        self.assertEqual(test_user.username, test_username)
        self.assertEqual(test_user.email, test_email)
        self.assertNotEqual(test_user.password, test_password)
        self.assertTrue(test_user.password.startswith("$2b$"))
        self.assertEqual(test_user.image_url, DEFAULT_IMAGE)

    def test_valid_custom_image_signup(self):
        test_user_id = '12345'
        test_username = 'testuser1'
        test_email = 'testuser1@test.com'
        test_password = 'testpassword1'
        test_image = 'https://image.com/image.png'

        test_user = User.signup(test_username, test_email, test_password, test_image)
        test_user.id = test_user_id

        db.session.commit()

        self.assertEqual(test_user.username, test_username)
        self.assertEqual(test_user.email, test_email)
        self.assertNotEqual(test_user.password, test_password)
        self.assertTrue(test_user.password.startswith("$2b$"))
        self.assertEqual(test_user.image_url, 'https://image.com/image.png')

    def test_nonunique_username_signup(self):
        test_user_id = '12345'
        test_username = 'user1'
        test_email = 'testuser1@test.com'
        test_password = 'testpassword1'
        test_image = None

        test_user = User.signup(test_username, test_email, test_password, test_image)
        test_user.id = test_user_id

        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()

    
    def test_no_username_signup(self):
        test_user_id = '12345'
        test_username = None
        test_email = 'testuser1@test.com'
        test_password = 'testpassword1'
        test_image = None

        test_user = User.signup(test_username, test_email, test_password, test_image)
        test_user.id = test_user_id

        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()

    def test_nonunique_email_signup(self):
        test_user_id = '12345'
        test_username = 'testuser1'
        test_email = 'user1@test.com'
        test_password = 'testpassword1'
        test_image = None

        test_user = User.signup(test_username, test_email, test_password, test_image)
        test_user.id = test_user_id

        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()
    
    def test_no_email_signup(self):
        test_user_id = '12345'
        test_username = 'testuser1'
        test_email = None
        test_password = 'testpassword1'
        test_image = None

        test_user = User.signup(test_username, test_email, test_password, test_image)
        test_user.id = test_user_id

        with self.assertRaises(exc.IntegrityError) as e:
            db.session.commit()

    def test_no_password_signup(self):
        test_user_id = '12345'
        test_username = 'testuser1'
        test_email = 'testuser1@test.com'
        test_password = None
        test_image = None

        with self.assertRaises(ValueError) as e:
            test_user = User.signup(test_username, test_email, test_password, test_image)

# Authentication Tests
    def test_valid_auth(self):
        user = User.authenticate(self.u1.username, "password1")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, self.u1.username)
        self.assertEqual(user.id, self.u1_id)

    def wrong_username_auth(self):
        self.assertFalse(User.authenticate('wrongusername', "password1"))
    
    def wrong_password_auth(self):
        self.assertFalse(User.authenticate(self.u1.username, 'wrongpassword'))