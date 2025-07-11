import unittest
from backend.routers.auth import get_password_hash, verify_password

class TestAuthUtils(unittest.TestCase):

    def test_password_hashing_and_verification(self):
        password = "testpassword123"
        hashed_password = get_password_hash(password)

        self.assertIsNotNone(hashed_password)
        self.assertNotEqual(password, hashed_password)

        # Verify correct password
        self.assertTrue(verify_password(password, hashed_password))

        # Verify incorrect password
        self.assertFalse(verify_password("wrongpassword", hashed_password))

    def test_password_hashing_consistency_for_same_password(self):
        # Note: bcrypt generates a new salt each time, so hashes will be different.
        # This test just ensures the process runs without error for the same input.
        # Verification is the key.
        password = "anotherTestPassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        self.assertNotEqual(hash1, hash2, "Hashes for the same password should differ due to salting.")
        self.assertTrue(verify_password(password, hash1))
        self.assertTrue(verify_password(password, hash2))

if __name__ == '__main__':
    unittest.main()
