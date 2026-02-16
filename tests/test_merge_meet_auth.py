from django.test import TestCase

from trackapp.models import Meet, Season, Team, User


class TestMergeMeetAuth(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team")
        self.season = Season.objects.create(name="Test Season")
        self.meet = Meet.objects.create(
            date="2024-01-01",
            description="Test Meet",
            team=self.team,
            season=self.season,
        )
        self.user = User.objects.create_user(
            "testuser", "test@example.com", "testpass123"
        )

    def test_anonymous_redirected_to_login(self):
        """Anonymous users should be redirected to login when accessing merge_meet."""
        response = self.client.get(f"/merge_meet/{self.meet.id}")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_authenticated_can_access(self):
        """Authenticated users should be able to access merge_meet."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(f"/merge_meet/{self.meet.id}")
        self.assertEqual(response.status_code, 200)
