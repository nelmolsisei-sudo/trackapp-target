from django.test import TestCase

from trackapp.models import User


class TestRegisterValidation(TestCase):
    def test_empty_password_rejected(self):
        """Registration with an empty password should be rejected."""
        response = self.client.post("/register", {
            "email": "newuser@example.com",
            "first": "Test",
            "last": "User",
            "password": "",
            "confirmation": "",
        })
        self.assertEqual(User.objects.filter(email="newuser@example.com").count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password must be at least 8 characters")

    def test_short_password_rejected(self):
        """Registration with a password shorter than 8 characters should be rejected."""
        response = self.client.post("/register", {
            "email": "newuser@example.com",
            "first": "Test",
            "last": "User",
            "password": "short",
            "confirmation": "short",
        })
        self.assertEqual(User.objects.filter(email="newuser@example.com").count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password must be at least 8 characters")

    def test_valid_password_accepted(self):
        """Registration with a valid password (8+ chars) should succeed."""
        response = self.client.post("/register", {
            "email": "newuser@example.com",
            "first": "Test",
            "last": "User",
            "password": "validpass123",
            "confirmation": "validpass123",
        })
        self.assertEqual(User.objects.filter(email="newuser@example.com").count(), 1)

    def test_password_mismatch_still_rejected(self):
        """Registration with mismatched passwords should still be rejected."""
        response = self.client.post("/register", {
            "email": "newuser@example.com",
            "first": "Test",
            "last": "User",
            "password": "validpass123",
            "confirmation": "differentpass",
        })
        self.assertEqual(User.objects.filter(email="newuser@example.com").count(), 0)
        self.assertContains(response, "Passwords must match")
