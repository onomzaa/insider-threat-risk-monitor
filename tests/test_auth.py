import tempfile
import unittest
from pathlib import Path

from modules.auth import create_user, authenticate, can, hash_password, verify_password, change_password


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "users.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_create_and_authenticate_user(self):
        create_user("analyst1", "Correct-Horse-123!", "analyst", self.path)
        self.assertEqual(authenticate("analyst1", "Correct-Horse-123!", self.path)["role"], "analyst")
        self.assertIsNone(authenticate("analyst1", "wrong-password", self.path))

    def test_password_minimum_and_duplicate(self):
        with self.assertRaises(ValueError):
            hash_password("short")
        create_user("admin1", "Secure-Password-456!", "admin", self.path)
        with self.assertRaises(ValueError):
            create_user("admin1", "Another-Password-789!", "admin", self.path)

    def test_change_password_requires_current_and_updates_credentials(self):
        create_user("analyst2", "Old-Password-123!", "analyst", self.path)
        with self.assertRaises(ValueError):
            change_password("analyst2", "incorrect-current", "New-Password-456!", self.path)
        change_password("analyst2", "Old-Password-123!", "New-Password-456!", self.path)
        self.assertIsNone(authenticate("analyst2", "Old-Password-123!", self.path))
        self.assertEqual(authenticate("analyst2", "New-Password-456!", self.path)["role"], "analyst")

    def test_role_permissions(self):
        self.assertTrue(can("view", "viewer"))
        self.assertFalse(can("review", "viewer"))
        self.assertTrue(can("review", "analyst"))
        self.assertTrue(can("manage_users", "admin"))
        self.assertFalse(can("manage_users", "analyst"))


if __name__ == "__main__":
    unittest.main()
