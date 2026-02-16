from django.test import TestCase

from trackapp.models import Team, User


class TestRemoveCoachSafety(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin", "admin@example.com", "testpass123"
        )
        self.coach = User.objects.create_user(
            "coach", "coach@example.com", "testpass123"
        )
        self.team = Team.objects.create(name="Test Team")
        self.team.coaches.add(self.coach)
        self.client.login(username="admin", password="testpass123")

    def test_get_does_not_remove_coach(self):
        """GET request to remove_coach should NOT remove the coach."""
        response = self.client.get(
            f"/remove_coach/{self.coach.id}/{self.team.id}"
        )
        self.assertNotEqual(response.status_code, 302)
        self.assertIn(self.coach, self.team.coaches.all())

    def test_post_removes_coach(self):
        """POST request to remove_coach should remove the coach."""
        response = self.client.post(
            f"/remove_coach/{self.coach.id}/{self.team.id}"
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.coach, self.team.coaches.all())


class TestRemoveAthleteSafety(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin", "admin@example.com", "testpass123"
        )
        self.athlete = User.objects.create_user(
            "athlete", "athlete@example.com", "testpass123"
        )
        self.team = Team.objects.create(name="Test Team")
        self.team.athletes.add(self.athlete)
        self.client.login(username="admin", password="testpass123")

    def test_get_does_not_remove_athlete(self):
        """GET request to remove_athlete_from_team should NOT remove the athlete."""
        response = self.client.get(
            f"/remove_athlete_from_team/{self.athlete.id}/{self.team.id}"
        )
        self.assertNotEqual(response.status_code, 302)
        self.assertIn(self.athlete, self.team.athletes.all())

    def test_post_removes_athlete(self):
        """POST request to remove_athlete_from_team should remove the athlete."""
        response = self.client.post(
            f"/remove_athlete_from_team/{self.athlete.id}/{self.team.id}"
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.athlete, self.team.athletes.all())
