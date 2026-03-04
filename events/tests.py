from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

# Use absolute imports to avoid parent package errors
from events.models import Event, UserEvent

User = get_user_model()


class EventAPITests(APITestCase):
    """
    Professional test suite for Event and UserEvent subscription logic.
    """

    def setUp(self):
        """
        Initialize test database with required objects for each test.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123", is_active=True
        )
        self.client.force_authenticate(user=self.user)

        self.event = Event.objects.create(
            title="Yoga Session",
            description="Morning yoga practice",
            start_time="08:00:00",
            end_time="09:00:00",
            date=timezone.now().date(),
            link="https://zoom.us/j/123",
            type_of_event="Health",
            requirements="Yoga mat",
        )

    def _get_results(self, data):
        """
        Helper to extract data from paginated or non-paginated responses.
        """
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_get_future_events(self):
        """
        Ensure users can retrieve upcoming events.
        """
        url = reverse("events:future-events")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._get_results(response.data)
        self.assertGreaterEqual(len(results), 1)

    def test_user_event_subscription_workflow(self):
        """
        Test the complete workflow: Subscribe -> List -> Unsubscribe.
        """
        # 1. Subscribe to an event
        subscribe_url = reverse("events:user-event-create")
        response = self.client.post(subscribe_url, {"event": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. List user subscriptions
        list_url = reverse("events:user-events")
        response = self.client.get(list_url)
        results = self._get_results(response.data)
        # Check the length of the results list, not the whole dictionary
        self.assertEqual(len(results), 1)

        # 3. Unsubscribe from the event
        destroy_url = reverse("events:user-event-destroy")
        response = self.client.delete(
            destroy_url, {"event": self.event.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_events_by_date(self):
        """
        Verify that events can be filtered by a specific date.
        """
        url = reverse("events:events-by-date", kwargs={"date": self.event.date})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._get_results(response.data)
        # Use results list to avoid KeyError: 0
        self.assertEqual(results[0]["title"], "Yoga Session")
