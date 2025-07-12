import unittest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import patch

from backend.models import UserDB, UsageDB
from backend.tests.test_db_setup import TestingSessionLocal, init_test_db
from backend.services import usage_service
from backend.routers.auth import get_password_hash

class TestUsageService(unittest.TestCase):

    def setUp(self):
        init_test_db()
        self.db: Session = next(TestingSessionLocal())

        # Create a test user
        self.user = UserDB(email="usageuser@example.com", hashed_password=get_password_hash("pw"), plan="free")
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()

    def test_get_or_create_usage_record_creates_new(self):
        # Should not have a record initially
        self.assertIsNone(self.user.usage)

        usage = usage_service.get_or_create_usage_record(self.db, self.user)

        self.assertIsNotNone(usage)
        self.assertEqual(usage.user_id, self.user.id)
        self.assertEqual(usage.words_scanned, 0)
        self.assertEqual(usage.humanizer_uses, 0)

        # Verify it was added to the user object as well
        self.assertIsNotNone(self.user.usage)
        self.assertEqual(self.user.usage.id, usage.id)

    def test_usage_reset_for_new_month(self):
        # Create an old usage record
        one_month_ago = datetime.now() - timedelta(days=35)
        old_usage = UsageDB(user_id=self.user.id, words_scanned=1000, humanizer_uses=100, last_reset=one_month_ago)
        self.db.add(old_usage)
        self.db.commit()

        # Call the service function, which should detect the old date and reset
        usage = usage_service.get_or_create_usage_record(self.db, self.user)

        self.assertEqual(usage.words_scanned, 0)
        self.assertEqual(usage.humanizer_uses, 0)
        self.assertTrue(usage.last_reset.day == datetime.now().day)
        self.assertTrue(usage.last_reset.month == datetime.now().month)

    def test_check_word_limit(self):
        usage = usage_service.get_or_create_usage_record(self.db, self.user)
        self.user.plan = "free" # 5000 word limit

        # Within limit
        self.assertTrue(usage_service.check_word_limit(self.user, usage, 4000))
        # Exactly at limit
        self.assertTrue(usage_service.check_word_limit(self.user, usage, 5000))
        # Exceeds limit
        self.assertFalse(usage_service.check_word_limit(self.user, usage, 5001))

        # Test with updated usage
        usage.words_scanned = 2000
        self.assertTrue(usage_service.check_word_limit(self.user, usage, 3000))
        self.assertFalse(usage_service.check_word_limit(self.user, usage, 3001))

    def test_check_humanizer_limit(self):
        usage = usage_service.get_or_create_usage_record(self.db, self.user)
        self.user.plan = "pro_basic" # 100k word limit, 50% humanizer = 50k allowance

        # Within limit
        self.assertTrue(usage_service.check_humanizer_limit(self.user, usage, 40000))
        # Exactly at limit
        self.assertTrue(usage_service.check_humanizer_limit(self.user, usage, 50000))
        # Exceeds limit
        self.assertFalse(usage_service.check_humanizer_limit(self.user, usage, 50001))

        # Test with updated usage
        usage.humanizer_uses = 10000
        self.assertTrue(usage_service.check_humanizer_limit(self.user, usage, 40000))
        self.assertFalse(usage_service.check_humanizer_limit(self.user, usage, 40001))

    def test_update_usage(self):
        usage = usage_service.get_or_create_usage_record(self.db, self.user)

        initial_words = usage.words_scanned
        initial_humanizer = usage.humanizer_uses

        usage_service.update_usage(self.db, usage, words_scanned=123, humanizer_uses=45)

        self.assertEqual(usage.words_scanned, initial_words + 123)
        self.assertEqual(usage.humanizer_uses, initial_humanizer + 45)

if __name__ == '__main__':
    unittest.main()
