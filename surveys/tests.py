from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Absolute imports for clean resolution
from challenges.models import Challenge
from prizes.models import Medal, UserMedal
from surveys.models import Survey, UserSurvey

User = get_user_model()


class SurveyAPITests(APITestCase):
    """
    Professional test suite for Survey submission and validation logic.
    """

    def setUp(self):
        # Create standard user
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123", is_active=True
        )
        # Create admin user
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )

        # Base challenge required for the survey
        self.challenge = Challenge.objects.create(day="Day 1", quote="Keep pushing")
        self.create_url = reverse("surveys:create")

    def test_create_survey_success(self):
        """
        Verify that an authenticated user can submit a survey and data is accurately stored.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "challenge": self.challenge.id,
            "physical_done": True,
            "mental_done": False,
            "social_done": True,
            "video_link": "http://example.com/video",
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)

        # Verify completion count logic (True + False + True = 2)
        survey = Survey.objects.first()
        self.assertEqual(survey.number_of_completed, 2)

    def test_medal_awarded_on_threshold(self):
        """
        Verify that a medal is dynamically awarded when a threshold (e.g., 37) is reached.
        """
        self.client.force_authenticate(user=self.user)

        # Simulate previous surveys giving the user 36 points
        survey = Survey.objects.create(challenge=self.challenge, number_of_completed=36)
        UserSurvey.objects.create(user=self.user, survey=survey)

        # Submitting this new survey adds +2 points (total: 38)
        data = {
            "challenge": self.challenge.id,
            "physical_done": True,
            "mental_done": True,
            "social_done": False,
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the Bronze medal was safely created and awarded (threshold is 37)
        self.assertTrue(
            UserMedal.objects.filter(user=self.user, medal__name="Bronze").exists()
        )

    def test_random_choose_survey_admin_only(self):
        """
        Ensure only admins can randomly select a user survey.
        """
        survey = Survey.objects.create(challenge=self.challenge, number_of_completed=1)
        user_survey = UserSurvey.objects.create(user=self.user, survey=survey)

        url = reverse("surveys:choose-user-survey", kwargs={"day": self.challenge.day})

        # 1. Unauthenticated -> 401
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Regular user -> 403 Forbidden
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Admin -> 200 OK
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the boolean changed
        user_survey.refresh_from_db()
        self.assertTrue(user_survey.is_choosed)

    def test_update_survey_validation_admin(self):
        """
        Ensure admins can successfully validate a user's survey via PATCH.
        """
        survey = Survey.objects.create(challenge=self.challenge, number_of_completed=1)
        user_survey = UserSurvey.objects.create(user=self.user, survey=survey)
        url = reverse(
            "surveys:update-user-survey-validation", kwargs={"pk": user_survey.id}
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, {"is_validated": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_survey.refresh_from_db()
        self.assertTrue(user_survey.is_validated)
