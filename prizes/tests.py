from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from prizes.models import DailyPrize, Medal, UserMedal

User = get_user_model()


class PrizesAPITests(APITestCase):
    """
    Test suite for the Prizes application endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123", is_active=True
        )
        self.client.force_authenticate(user=self.user)

        self.daily_prize = DailyPrize.objects.create(
            day="5",
            company_name="Nike",
            content="Shoes",
            prize_name="Air Max",
            description="Awesome shoes",
            video_link="https://youtube.com",
        )

        self.medal = Medal.objects.create(name="Gold Medal")
        self.user_medal = UserMedal.objects.create(user=self.user, medal=self.medal)

    def _get_results(self, data):
        """Helper to extract paginated or raw data."""
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_get_daily_prize_list(self):
        url = reverse("prizes:daily-prize-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(self._get_results(response.data)), 1)

    def test_get_daily_prize_by_valid_day(self):
        url = reverse("prizes:daily-prize-list-by-day")
        response = self.client.get(url, {"day": "5"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._get_results(response.data)
        self.assertEqual(results[0]["company_name"], "Nike")

    def test_get_daily_prize_by_invalid_day(self):
        url = reverse("prizes:daily-prize-list-by-day")
        response = self.client.get(url, {"day": "999"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_medals(self):
        url = reverse("prizes:medal-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._get_results(response.data)
        self.assertEqual(results[0]["medal"]["name"], "Gold Medal")

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        url = reverse("prizes:daily-prize-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
