"""Test views for user related pages"""

import os
from unittest import TestCase

from models import db, User, FavoriteSeiyuu

os.environ['DATABASE_URL'] = "postgresql:///seiyuulist-test"

TEST_RANK1_SEIYUU_ID = 11661
TEST_RANK1_SEIYUU_NAME = 'Tomoyo Kurosawa'
TEST_RANK2_SEIYUU_ID = 55082
TEST_RANK2_SEIYUU_NAME = 'Tasuku Kaito'

from app import app, CURR_USER_KEY

db.create_all()

class UserViewsTestCase(TestCase):
    """Test Views for homepage(/),  (/anime), (/person), (/character)"""

    def setUp(self):
        """Create test client and add some data"""
        db.drop_all()
        db.create_all()

        u1 = User.signup("user1", "user1@test.com", 'password1', None)
        u1_id = 11111
        u1.id = u1_id

        db.session.commit()

        f1 = FavoriteSeiyuu(
          seiyuu_id = TEST_RANK1_SEIYUU_ID,
          user_id = u1_id,
          rank = 1
        )

        f2 = FavoriteSeiyuu(
          seiyuu_id = TEST_RANK2_SEIYUU_ID,
          user_id = u1_id,
          rank = 2
        )

        db.session.add_all([f1, f2])
        db.session.commit()

        self.u1 = u1
        self.u1_id = u1_id

        self.client = app.test_client()
  
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_anon_view_user(self):
        """Test viewing a user when not logged in"""
        with self.client as c:
            resp = c.get('/users/11111', follow_redirects=True)
            self.assertIn('user1', str(resp.data))
            self.assertIn('View All Favorite Seiyuu Ranking', str(resp.data))
            self.assertIn(TEST_RANK1_SEIYUU_NAME, str(resp.data))
            self.assertNotIn('Edit Profile', str(resp.data))

    def test_view_self_user(self):
        """Test the current users page when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get('/users/11111', follow_redirects=True)
            self.assertIn('user1', str(resp.data))
            self.assertIn('View All Favorite Seiyuu Ranking', str(resp.data))
            self.assertIn(TEST_RANK1_SEIYUU_NAME, str(resp.data))
            self.assertIn('Edit Profile', str(resp.data))

    def test_anon_view_ranking(self):
        """Test viewing a user when not logged in"""
        with self.client as c:
            resp = c.get('/users/11111/rank', follow_redirects=True)
            self.assertIn("user1\\\'s Favorites Ranking", str(resp.data))
            self.assertIn(TEST_RANK1_SEIYUU_NAME, str(resp.data))
            self.assertNotIn('Edit Seiyuu Ranking', str(resp.data))

    def test_view_self_user(self):
        """Test the current users page when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get('/users/11111/rank', follow_redirects=True)
            self.assertIn("user1\\\'s Favorites Ranking", str(resp.data))
            self.assertIn(TEST_RANK1_SEIYUU_NAME, str(resp.data))
            self.assertIn('Edit seiyuu ranking', str(resp.data))