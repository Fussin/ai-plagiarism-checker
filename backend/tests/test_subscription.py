import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models import UserDB
from backend.dependencies import get_current_active_user
from backend.tests.test_db_setup import TestingSessionLocal, init_test_db
from backend.routers.auth import get_password_hash
from backend.config import settings

# Mock the get_db dependency if needed, or use the test_db_setup
# For these tests, we need a real DB session to manipulate the user object.

class TestSubscriptionAPI(unittest.TestCase):

    def setUp(self):
        init_test_db()
        self.db: Session = next(TestingSessionLocal())

        # Create a test user without a stripe_customer_id
        self.test_user = UserDB(email="subtest@example.com", hashed_password=get_password_hash("pw"), plan="free")
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

        # Override the dependency to use our test user
        app.dependency_overrides[get_current_active_user] = lambda: self.test_user

        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()
        # Clear the dependency override
        app.dependency_overrides = {}

    @patch('stripe.Customer.create')
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_new_customer(self, mock_session_create, mock_customer_create):
        # --- Mocking Stripe API responses ---
        mock_customer_create.return_value = {'id': 'cus_test12345'}
        mock_session_create.return_value = {'url': 'https://checkout.stripe.com/test_session_url'}

        # --- Setting required config values for the test ---
        settings.STRIPE_API_KEY = "sk_test_fakekey"
        settings.STRIPE_PRICE_ID_PRO_BASIC = "price_test_pro_basic"

        # --- Making the API call ---
        response = self.client.post("/api/subscribe", json={"plan": "pro_basic"})

        # --- Assertions ---
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"checkout_url": "https://checkout.stripe.com/test_session_url"})

        # Verify Stripe Customer.create was called because user didn't have a stripe_id
        mock_customer_create.assert_called_once()
        self.assertEqual(mock_customer_create.call_args.kwargs['email'], self.test_user.email)

        # Verify user in DB was updated with the new stripe_customer_id
        self.db.refresh(self.test_user)
        self.assertEqual(self.test_user.stripe_customer_id, 'cus_test12345')

        # Verify Stripe Session.create was called with the correct parameters
        mock_session_create.assert_called_once()
        self.assertEqual(mock_session_create.call_args.kwargs['customer'], 'cus_test12345')
        self.assertEqual(mock_session_create.call_args.kwargs['line_items'][0]['price'], 'price_test_pro_basic')
        self.assertEqual(mock_session_create.call_args.kwargs['metadata']['user_id'], self.test_user.id)


    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_existing_customer(self, mock_session_create):
        # --- Setup for existing customer ---
        self.test_user.stripe_customer_id = 'cus_existing123'
        self.db.commit()

        # --- Mocking Stripe API responses ---
        mock_session_create.return_value = {'url': 'https://checkout.stripe.com/another_url'}

        # --- Setting required config values ---
        settings.STRIPE_API_KEY = "sk_test_fakekey"
        settings.STRIPE_PRICE_ID_PRO_ADVANCED = "price_test_pro_advanced"

        # --- Making the API call ---
        with patch('stripe.Customer.create') as mock_customer_create:
            response = self.client.post("/api/subscribe", json={"plan": "pro_advanced"})

            # Verify Stripe Customer.create was NOT called
            mock_customer_create.assert_not_called()

        # --- Assertions ---
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"checkout_url": "https://checkout.stripe.com/another_url"})

        # Verify Stripe Session.create was called with the existing customer ID
        mock_session_create.assert_called_once()
        self.assertEqual(mock_session_create.call_args.kwargs['customer'], 'cus_existing123')
        self.assertEqual(mock_session_create.call_args.kwargs['line_items'][0]['price'], 'price_test_pro_advanced')

    def test_subscribe_invalid_plan(self):
        settings.STRIPE_API_KEY = "sk_test_fakekey"
        response = self.client.post("/api/subscribe", json={"plan": "non_existent_plan"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid plan specified", response.json()["detail"])


if __name__ == '__main__':
    unittest.main()
