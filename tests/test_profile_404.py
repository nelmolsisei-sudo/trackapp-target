from django.test import TestCase

from trackapp.models import User


class TestProfile404(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "testathlete", "athlete@example.com", "testpass123"
        )
        self.user.first_name = "Test"
        self.user.last_name = "Athlete"
        self.user.save()

    def test_nonexistent_user_returns_404(self):
        """Accessing a profile for a non-existent user should return 404."""
        response = self.client.get("/profile/99999")
        self.assertEqual(response.status_code, 404)

    def test_existing_user_returns_200(self):
        """Accessing a profile for an existing user should return 200."""
        response = self.client.get(f"/profile/{self.user.id}")
        self.assertEqual(response.status_code, 200)
