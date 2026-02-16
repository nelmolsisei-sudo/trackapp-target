"""Comprehensive tests for result CRUD operations (add, edit, delete).

Tests verify that:
1. edit_result view correctly passes querysets (not view functions) for
   events and meets, and renders without error.
2. add_result recalculates athlete stats after adding (personal_rank,
   milestones via calculate_result_stats).
3. delete_result recalculates athlete stats after deleting, so remaining
   results have correct rankings and milestones.
"""

import datetime

from django.test import TestCase, Client

from trackapp.models import (
    User, Team, Event, Meet, Result, Season,
    calculate_result_stats,
)


class ResultCRUDTestBase(TestCase):
    """Base class with shared test data setup."""

    def setUp(self):
        """Create a complete set of test data for result CRUD testing."""
        # Create admin user for login (required by @login_required)
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com',
        )

        # Create athlete
        self.athlete = User.objects.create_user(
            username='testathlete',
            password='testpass123',
            first_name='Test',
            last_name='Athlete',
            gender='male',
        )

        # Create supporting objects
        self.season = Season.objects.create(name='Indoor 2023-2024')
        self.team = Team.objects.create(name='Test Team')

        # Running event (lower time = better, unit='seconds')
        self.event_800m = Event.objects.create(name='800 Meters', unit='seconds')

        # Create meets
        self.meet1 = Meet.objects.create(
            date=datetime.date(2024, 1, 10),
            description='Meet 1',
            team=self.team,
            season=self.season,
        )
        self.meet2 = Meet.objects.create(
            date=datetime.date(2024, 1, 20),
            description='Meet 2',
            team=self.team,
            season=self.season,
        )
        self.meet3 = Meet.objects.create(
            date=datetime.date(2024, 2, 1),
            description='Meet 3',
            team=self.team,
            season=self.season,
        )

        # Log in as admin
        self.client = Client()
        self.client.login(username='admin', password='adminpass123')


class TestEditResult(ResultCRUDTestBase):
    """Tests for the edit_result view.

    The edit_result view template context should include Event and Meet
    querysets (not the view functions that happen to share those names).
    The view should also render the edit form successfully on GET.
    """

    def setUp(self):
        super().setUp()
        # Create a result to edit
        self.result = Result.objects.create(
            athlete=self.athlete,
            event=self.event_800m,
            meet=self.meet1,
            result=130.0,  # 2:10
            method='FAT',
        )
        calculate_result_stats(self.athlete)

    def test_edit_result_get_returns_200(self):
        """GET /edit_result/<id> should render the form successfully."""
        response = self.client.get(f'/edit_result/{self.result.id}')
        self.assertEqual(response.status_code, 200)

    def test_edit_result_context_has_querysets(self):
        """The template context 'events' and 'meets' should be querysets."""
        response = self.client.get(f'/edit_result/{self.result.id}')
        # events should be a queryset of Event objects, not a function
        self.assertTrue(
            hasattr(response.context['events'], 'model'),
            "'events' in context should be a queryset, not a view function",
        )
        self.assertEqual(response.context['events'].model, Event)
        self.assertTrue(
            hasattr(response.context['meets'], 'model'),
            "'meets' in context should be a queryset, not a view function",
        )
        self.assertEqual(response.context['meets'].model, Meet)

    def test_edit_result_post_updates_and_redirects(self):
        """POST to edit_result should save changes and redirect."""
        response = self.client.post(
            f'/edit_result/{self.result.id}',
            {
                'event': self.event_800m.id,
                'meet': self.meet1.id,
                'result': '125.0',
                'method': 'FAT',
            },
        )
        # Should redirect to profile on success
        self.assertEqual(response.status_code, 302)

        # Verify the result was updated in the database
        self.result.refresh_from_db()
        self.assertEqual(self.result.result, 125.0)

    def test_edit_result_post_recalculates_stats(self):
        """After editing a result, personal_rank should be recalculated."""
        # Create a second result so rankings matter
        result2 = Result.objects.create(
            athlete=self.athlete,
            event=self.event_800m,
            meet=self.meet2,
            result=135.0,  # 2:15 (slower)
            method='FAT',
        )
        calculate_result_stats(self.athlete)

        # Verify initial rankings: 130.0 is rank 1 (faster), 135.0 is rank 2
        self.result.refresh_from_db()
        result2.refresh_from_db()
        self.assertEqual(self.result.personal_rank, 1)
        self.assertEqual(result2.personal_rank, 2)

        # Edit result to be slower than result2
        self.client.post(
            f'/edit_result/{self.result.id}',
            {
                'event': self.event_800m.id,
                'meet': self.meet1.id,
                'result': '140.0',
                'method': 'FAT',
            },
        )

        # Rankings should swap: result2 (135.0) = rank 1, result (140.0) = rank 2
        self.result.refresh_from_db()
        result2.refresh_from_db()
        self.assertEqual(result2.personal_rank, 1)
        self.assertEqual(self.result.personal_rank, 2)


class TestAddResult(ResultCRUDTestBase):
    """Tests for the add_result view (missing calculate_result_stats call).

    After adding a result, the view should call calculate_result_stats()
    so personal_rank and milestones are updated. Without this call,
    personal_rank stays at the default of -1 and milestones remain None.

    NOTE: The add_result view always renders the template after POST
    (no redirect on success). The template has a pre-existing URL reverse
    issue unrelated to our target bugs. We suppress template rendering
    exceptions and verify the database state directly.
    """

    def _post_add_result(self, user_id, event_id, meet_id, result_val, method='FAT'):
        """POST to add_result, suppressing template rendering exceptions.

        The add_result view saves the result and (when fixed) recalculates
        stats BEFORE rendering the response template. We test the database
        effects, not the template output.
        """
        old_setting = self.client.raise_request_exception
        self.client.raise_request_exception = False
        try:
            self.client.post(
                f'/add_result/{user_id}',
                {
                    'event': event_id,
                    'meet': meet_id,
                    'result': str(result_val),
                    'method': method,
                },
            )
        finally:
            self.client.raise_request_exception = old_setting

    def test_add_result_sets_personal_rank(self):
        """After adding a result, personal_rank should be set (not default -1)."""
        self._post_add_result(
            self.athlete.id, self.event_800m.id, self.meet1.id, 130.0,
        )

        result = Result.objects.get(athlete=self.athlete, event=self.event_800m)
        self.assertNotEqual(
            result.personal_rank, -1,
            "personal_rank should be calculated after adding a result, not left at default -1",
        )
        self.assertEqual(result.personal_rank, 1, "Only result should be rank 1")

    def test_add_result_recalculates_rankings_with_multiple_results(self):
        """Adding a faster result should make it rank 1 and demote the old one."""
        # Create a slower result directly
        Result.objects.create(
            athlete=self.athlete,
            event=self.event_800m,
            meet=self.meet1,
            result=135.0,
            method='FAT',
        )
        calculate_result_stats(self.athlete)

        # Add a faster result via the view
        self._post_add_result(
            self.athlete.id, self.event_800m.id, self.meet2.id, 128.0,
        )

        # The new faster result should be rank 1
        fast_result = Result.objects.get(
            athlete=self.athlete, event=self.event_800m, meet=self.meet2,
        )
        slow_result = Result.objects.get(
            athlete=self.athlete, event=self.event_800m, meet=self.meet1,
        )
        self.assertEqual(
            fast_result.personal_rank, 1, "Faster result should be ranked 1",
        )
        self.assertEqual(
            slow_result.personal_rank, 2, "Slower result should be demoted to rank 2",
        )

    def test_add_result_sets_milestones(self):
        """Adding a result should trigger milestone calculation."""
        self._post_add_result(
            self.athlete.id, self.event_800m.id, self.meet1.id, 130.0,
        )

        result = Result.objects.get(athlete=self.athlete, event=self.event_800m)
        self.assertIsNotNone(
            result.milestones,
            "Milestones should be set after adding a result",
        )
        self.assertIn(
            'First time in the 800 Meters',
            result.milestones,
            "First result in an event should have 'First time' milestone",
        )

    def test_add_result_new_pr_gets_milestone(self):
        """Adding a PR result should include 'New Personal Best!' milestone."""
        # Create initial slower result
        Result.objects.create(
            athlete=self.athlete,
            event=self.event_800m,
            meet=self.meet1,
            result=135.0,
            method='FAT',
        )
        calculate_result_stats(self.athlete)

        # Add a faster (better) result via the view
        self._post_add_result(
            self.athlete.id, self.event_800m.id, self.meet2.id, 128.0,
        )

        new_pr = Result.objects.get(
            athlete=self.athlete, event=self.event_800m, meet=self.meet2,
        )
        self.assertIn(
            'New Personal Best!',
            new_pr.milestones or '',
            "New PR should have 'New Personal Best!' milestone",
        )


class TestDeleteResult(ResultCRUDTestBase):
    """Tests for the delete_result view (missing calculate_result_stats call).

    After deleting a result, the view should call calculate_result_stats()
    so that the remaining results have correct personal_rank and milestones.
    Without this call, the old rankings persist (stale data).
    """

    def setUp(self):
        super().setUp()
        # Create two results: a PR and a non-PR
        self.pr_result = Result.objects.create(
            athlete=self.athlete,
            event=self.event_800m,
            meet=self.meet1,
            result=128.0,  # faster = better for running
            method='FAT',
        )
        self.other_result = Result.objects.create(
            athlete=self.athlete,
            event=self.event_800m,
            meet=self.meet2,
            result=135.0,  # slower
            method='FAT',
        )
        calculate_result_stats(self.athlete)

        # Confirm initial state: 128.0 is rank 1, 135.0 is rank 2
        self.pr_result.refresh_from_db()
        self.other_result.refresh_from_db()
        assert self.pr_result.personal_rank == 1
        assert self.other_result.personal_rank == 2

    def test_delete_pr_promotes_next_best(self):
        """After deleting the PR, the next-best result should become rank 1."""
        self.client.post(
            f'/delete_result/{self.pr_result.id}',
            {
                'event': self.event_800m.id,
                'meet': self.meet1.id,
                'result': '128.0',
                'method': 'FAT',
            },
        )

        # The remaining result should now be rank 1
        self.other_result.refresh_from_db()
        self.assertEqual(
            self.other_result.personal_rank, 1,
            "After deleting the PR, the remaining result should be promoted to rank 1",
        )

    def test_delete_result_updates_milestones(self):
        """After deleting the PR, milestones should be recalculated."""
        self.client.post(
            f'/delete_result/{self.pr_result.id}',
            {
                'event': self.event_800m.id,
                'meet': self.meet1.id,
                'result': '128.0',
                'method': 'FAT',
            },
        )

        # The remaining result should now have 'New Personal Best!' milestone
        self.other_result.refresh_from_db()
        self.assertIsNotNone(
            self.other_result.milestones,
            "Remaining result should have milestones after PR deletion",
        )
        self.assertIn(
            'New Personal Best!',
            self.other_result.milestones,
            "Remaining result should become the new PR with milestone",
        )

    def test_delete_nonpr_preserves_rankings(self):
        """Deleting a non-PR result should keep the PR at rank 1."""
        self.client.post(
            f'/delete_result/{self.other_result.id}',
            {
                'event': self.event_800m.id,
                'meet': self.meet2.id,
                'result': '135.0',
                'method': 'FAT',
            },
        )

        # The PR should still be rank 1
        self.pr_result.refresh_from_db()
        self.assertEqual(
            self.pr_result.personal_rank, 1,
            "PR result should remain rank 1 after deleting a non-PR",
        )
