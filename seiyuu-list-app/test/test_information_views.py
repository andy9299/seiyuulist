"""Test views for informational pages"""

import os
from unittest import TestCase

from models import db, User, FavoriteSeiyuu

os.environ['DATABASE_URL'] = "postgresql:///seiyuulist-test"

TEST_NONFAVORITE_SEIYUU_ID = 34785
TEST_FAVORITE_SEIYUU_ID = 513
TEST_ANIME_ID = 50602
TEST_NONSEIYUU_ID = 52015
TEST_CHARACTER_ID = 109929

from app import app, CURR_USER_KEY

db.create_all()

class InformationViewsTestCase(TestCase):
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
          seiyuu_id = TEST_FAVORITE_SEIYUU_ID,
          user_id = u1_id,
          rank = 1
        )

        db.session.add(f1)
        db.session.commit()

        self.u1 = u1
        self.u1_id = u1_id

        self.client = app.test_client()
  
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_anon_homepage(self):
        """Test the homepage/navbar when not logged in"""
        with self.client as c:
            resp = c.get('/')
            self.assertIn("Here\\\'s a random top seasonal anime to get started:", str(resp.data))
            self.assertIn("Register", str(resp.data))

    def test_loggedin_homepage(self):
        """Test the homepage/navbar when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get('/')
            self.assertIn("Here\\\'s a random top seasonal anime to get started:", str(resp.data))
            self.assertIn("Logout", str(resp.data))

    def test_anime_info(self):
        """Test viewing anime info"""
        with self.client as c:
            resp = c.get(f'/anime/{TEST_ANIME_ID}')
            self.assertIn("Spy x Family Part 2", str(resp.data))
            self.assertIn("Main Characters:", str(resp.data))
            self.assertIn("Eguchi, Takuya as Forger, Loid", str(resp.data))


    def test_character_info(self):
        """Test viewing character info"""
        with self.client as c:
            resp = c.get(f'/character/{TEST_CHARACTER_ID}')
            self.assertIn("Shigeo Kageyama", str(resp.data))
            self.assertIn("Voiced By: Itou, Setsuo", str(resp.data))
            self.assertIn("Main Character in:", str(resp.data))
            self.assertIn("Mob Psycho 100 II", str(resp.data))

    def test_anon_seiyuu_info(self):
        """Test viewing a seiyuu's info while not logged in"""
        with self.client as c:
            resp = c.get(f'/person/{TEST_FAVORITE_SEIYUU_ID}')
            self.assertIn("Yuuichi Nakamura", str(resp.data))
            self.assertIn("Main Roles:", str(resp.data))
            self.assertIn("Gojou, Satoru", str(resp.data))
            self.assertNotIn("Favorite", str(resp.data))

    def test_loggedin_favorite_seiyuu_info(self):
        """Test viewing a favorite seiyuu's info while logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/person/{TEST_FAVORITE_SEIYUU_ID}')
            self.assertIn("Yuuichi Nakamura", str(resp.data))
            self.assertIn("Main Roles:", str(resp.data))
            self.assertIn("Gojou, Satoru", str(resp.data))
            self.assertIn("Favorite", str(resp.data))
            self.assertIn('class="mr-2"  checked  />', str(resp.data))

    def test_loggedin_nonfavorite_seiyuu_info(self):
        """Test viewing a favorite seiyuu's info while logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/person/{TEST_NONFAVORITE_SEIYUU_ID}')
            self.assertIn("Rie Takahashi", str(resp.data))
            self.assertIn("Main Roles:", str(resp.data))
            self.assertIn("Megumin", str(resp.data))
            self.assertIn("Favorite", str(resp.data))
            self.assertNotIn('class="mr-2"  checked  />', str(resp.data))

    def test_nonseiyuu_info(self):
        """Test viewing a person who is not a seiyuu"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/person/{TEST_NONSEIYUU_ID}')
            self.assertIn("No voice acting roles!", str(resp.data))