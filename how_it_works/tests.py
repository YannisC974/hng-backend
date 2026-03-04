from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Absolute imports to prevent parent package resolution errors
from how_it_works.models import FAQ, GetStarted


class HowItWorksAPITests(APITestCase):
    """
    Professional test suite for How It Works and FAQ public endpoints.
    """

    def setUp(self):
        """
        Create test data. Authentication is not forced as views are public.
        """
        self.get_started = GetStarted.objects.create(
            title="Step 1: Register",
            video_link="https://youtube.com/test",
            description="Create an account to begin.",
        )

        self.faq = FAQ.objects.create(
            question="How do I reset my password?",
            answer="Click on 'Forgot Password' on the login screen.",
        )

    def _get_results(self, data):
        """
        Helper to handle paginated or non-paginated API responses.
        """
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_get_how_it_works_data(self):
        """
        Ensure the 'How It Works' endpoint returns a unified JSON object
        containing the available sections.
        """
        url = reverse("how_it_works:how-it-works")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the unified serializer correctly outputs the 'get_started' key
        self.assertIn("get_started", response.data)
        self.assertEqual(response.data["get_started"]["title"], "Step 1: Register")

    def test_get_faq_list(self):
        """
        Ensure the FAQ endpoint returns the list of questions.
        """
        url = reverse("how_it_works:faq")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._get_results(response.data)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["question"], "How do I reset my password?")
