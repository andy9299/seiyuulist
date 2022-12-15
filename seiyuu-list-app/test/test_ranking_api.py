"""Test post requests to api to edit ranking/favoriting"""

import os
from unittest import TestCase

from models import db, User, FavoriteSeiyuu

os.environ['DATABASE_URL'] = "postgresql:///seiyuulist-test"

TEST_RANK1_SEIYUU_ID = 11661
TEST_RANK2_SEIYUU_ID = 55082
TEST_RANK3_SEIYUU_ID = 23997

from app import app, CURR_USER_KEY

db.create_all()

class RankingApiTestCase(TestCase):
    """Test Views for homepage(/),  (/anime), (/person), (/character)"""

    def setUp(self):
        """Create test client and add some data"""
        db.drop_all()
        db.create_all()

        u1 = User.signup("user1", "user1@test.com", 'password1', None)
        u1_id = 11111
        u1.id = u1_id

        u2 = User.signup("user2", "user2@test.com", 'password2', None)
        u2_id = 22222
        u2.id = u2_id

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

        f3 = FavoriteSeiyuu(
          seiyuu_id = TEST_RANK3_SEIYUU_ID,
          user_id = u1_id,
          rank = 3
        )

        db.session.add_all([f1, f2, f3])
        db.session.commit()

        self.u1 = u1
        self.u1_id = u1_id

        self.u2 = u2
        self.u2_id = u2_id

        self.client = app.test_client()
  
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_add_fav_unauthorized(self):
        """Test adding a favorite when not logged in"""
        with self.client as c:
            resp = c.post("/favorite/seiyuu", data={'seiyuu_id': 123})

            self.assertEqual(resp.status_code, 401)
            self.assertIn("Unauthorized User", str(resp.data))
    
    def test_add_fav_to_0(self):
        """Test adding a favorite to a user with 0 favorites"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = c.post("/favorite/seiyuu", json={'seiyuu_id': 123})

            self.assertEqual(resp.status_code, 200)
            query = (db.session
                        .query(FavoriteSeiyuu)
                        .filter(FavoriteSeiyuu.user_id==self.u2_id)
                        .all())
            self.assertEqual(1, len(query))
            self.assertEqual(123, query[0].seiyuu_id)

    def test_add_fav_to_some(self):
        """Test adding a favorite to a user with some favorites"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/favorite/seiyuu", json={'seiyuu_id': 123})

            self.assertEqual(resp.status_code, 200)
            query = (db.session
                        .query(FavoriteSeiyuu)
                        .filter(FavoriteSeiyuu.user_id==self.u1_id)
                        .all())
            self.assertEqual(4, len(query))
            self.assertEqual(123, query[-1].seiyuu_id)

    def test_removing_favorite(self):
        """Test removing a favorite a user with some favorites"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/favorite/seiyuu", json={'seiyuu_id': TEST_RANK2_SEIYUU_ID})

            self.assertEqual(resp.status_code, 200)
            query = (db.session
                        .query(FavoriteSeiyuu)
                        .filter(FavoriteSeiyuu.user_id==self.u1_id)
                        .all())
            self.assertEqual(2, len(query))
            self.assertEqual(TEST_RANK1_SEIYUU_ID, query[0].seiyuu_id)
            self.assertEqual(TEST_RANK3_SEIYUU_ID, query[1].seiyuu_id)

    def test_update_rank_unauthorized(self):
        """Test trying to change ranking when not logged in"""
        with self.client as c:
            resp = c.post("/rank/seiyuu", json={TEST_RANK2_SEIYUU_ID: 1, TEST_RANK1_SEIYUU_ID: 2})

            self.assertEqual(resp.status_code, 401)
            self.assertIn("Unauthorized User", str(resp.data))

    def test_update_rank(self):
        """Test trying to change ranking when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.post("/rank/seiyuu", json={TEST_RANK2_SEIYUU_ID: 1, TEST_RANK1_SEIYUU_ID: 2})
            
            self.assertEqual(resp.status_code, 200)
            query = (db.session
                        .query(FavoriteSeiyuu)
                        .filter(FavoriteSeiyuu.user_id==self.u1_id)
                        .order_by(FavoriteSeiyuu.rank.asc())
                        .all())

            self.assertEqual(3, len(query))
            self.assertEqual(TEST_RANK2_SEIYUU_ID, query[0].seiyuu_id)
            self.assertEqual(TEST_RANK1_SEIYUU_ID, query[1].seiyuu_id)
            self.assertEqual(TEST_RANK3_SEIYUU_ID, query[2].seiyuu_id)
    
