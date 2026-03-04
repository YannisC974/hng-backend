from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Use absolute imports for reliability
from challenges.models import (
    Challenge,
    Instructor,
    IntensePhysicalChallenge,
    MentalChallenge,
    ModeratePhysicalChallenge,
    SocialChallenge,
)

User = get_user_model()


class ChallengeAPITests(APITestCase):
    """
    Professional test suite for Challenge API endpoints.
    """

    def setUp(self):
        """
        Initialize test database with required objects for each test.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123", is_active=True
        )
        self.client.force_authenticate(user=self.user)

        self.instructor = Instructor.objects.create(
            name="John Doe", description="Expert fitness coach"
        )

        # Create sub-challenges
        self.moderate = ModeratePhysicalChallenge.objects.create(
            title="Moderate Walk",
            description="30-minute walk",
            instructor=self.instructor,
        )

        self.intense = IntensePhysicalChallenge.objects.create(
            title="HIIT", description="Intense workout", instructor=self.instructor
        )

        self.mental = MentalChallenge.objects.create(
            title="Focus", description="Mental focus task"
        )

        self.social = SocialChallenge.objects.create(
            title="Connect", description="Social task"
        )

        # Create the main daily challenge object
        self.daily_challenge = Challenge.objects.create(
            day="Day-1",
            quote="Stay strong",
            moderate_physical=self.moderate,
            intense_physical=self.intense,
            mental=self.mental,
            social=self.social,
        )

        self.list_url = reverse("challenges:list")
        self.detail_url = reverse(
            "challenges:detail", kwargs={"day": self.daily_challenge.day}
        )

    def test_get_challenge_list_authenticated(self):
        """
        Verify that the challenge list is correctly populated and handles pagination.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # logic to handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and "results" in response.data:
            results = response.data["results"]
        else:
            results = response.data

        # Verify the list is not empty
        self.assertGreater(len(results), 0, "The API returned an empty list.")

        # Verify the content of the first element
        self.assertEqual(results[0]["day"], "Day-1")

    def test_get_challenge_detail_authenticated(self):
        """
        Verify detailed view of a specific daily challenge.
        """
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["day"], "Day-1")
        # Check nested instructor data visibility
        self.assertEqual(
            response.data["moderate_physical"]["instructor"]["name"], "John Doe"
        )

    def test_challenge_access_unauthenticated(self):
        """
        Ensure security: unauthenticated requests must be rejected.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_challenge_detail_not_found(self):
        """
        Verify 404 handling for non-existent challenge days.
        """
        url = reverse("challenges:detail", kwargs={"day": "InvalidDay"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_challenge_model_str(self):
        """
        Test the __str__ method of the Challenge model.
        """
        self.assertEqual(str(self.daily_challenge), "Day-1")
