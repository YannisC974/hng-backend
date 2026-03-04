import random

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from prizes.models import Medal, UserMedal

from .models import Survey, UserSurvey
from .serializers import SurveySubmissionSerializer, UserSurveySerializer


class UserSurveyCreateView(generics.CreateAPIView):
    """
    Endpoint for users to submit a daily survey.
    Automatically calculates rewards and assigns medals if thresholds are met.
    """

    serializer_class = SurveySubmissionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user

        # 1. Calculate how many parts were completed in this survey
        completed_count = sum(
            [data["physical_done"], data["mental_done"], data["social_done"]]
        )

        # 2. Create the Survey answers
        survey = Survey.objects.create(
            challenge=data["challenge"],
            physical_done=data["physical_done"],
            mental_done=data["mental_done"],
            social_done=data["social_done"],
            video_link=data.get("video_link", ""),
            number_of_completed=completed_count,
        )

        # 3. Link it to the user
        user_survey = UserSurvey.objects.create(user=user, survey=survey)

        # 4. MEDAL CALCULATION LOGIC
        # Count all tasks completed by this user across all their surveys
        all_user_surveys = UserSurvey.objects.filter(user=user).select_related("survey")
        total_completed = sum(
            us.survey.number_of_completed
            for us in all_user_surveys
            if us.survey.number_of_completed
        )

        medal_name = None
        if total_completed >= 57:
            medal_name = "Gold"
        elif total_completed >= 47:
            medal_name = "Silver"
        elif total_completed >= 37:
            medal_name = "Bronze"

        # Award the medal safely if a threshold is reached
        if medal_name:
            medal, _ = Medal.objects.get_or_create(name=medal_name)
            # Assign medal only if the user doesn't already have it
            if not UserMedal.objects.filter(user=user, medal=medal).exists():
                UserMedal.objects.create(user=user, medal=medal)

        # Return the created resource
        response_serializer = UserSurveySerializer(user_survey)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class RandomUserSurveyChooseView(APIView):
    """
    Admin endpoint to randomly select an un-chosen UserSurvey for a given day.
    """

    permission_classes = [IsAdminUser]

    def get(self, request, day):
        # Find un-chosen surveys for the specified day
        surveys = UserSurvey.objects.filter(
            survey__challenge__day=day, is_choosed=False
        )

        if not surveys.exists():
            return Response(
                {"detail": "No un-chosen UserSurvey found for the given day."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Pick one randomly and update its status
        random_user_survey = random.choice(surveys)
        random_user_survey.is_choosed = True
        random_user_survey.save()

        return Response(
            {
                "detail": "UserSurvey successfully chosen.",
                "user_survey_id": random_user_survey.id,
            },
            status=status.HTTP_200_OK,
        )


class UpdateUserSurveyValidationView(APIView):
    """
    Admin endpoint to manually validate a specific UserSurvey.
    """

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            user_survey = UserSurvey.objects.get(pk=pk)
        except UserSurvey.DoesNotExist:
            raise NotFound(detail="UserSurvey not found.")

        is_validated = request.data.get("is_validated")

        if is_validated is not None:
            user_survey.is_validated = is_validated
            user_survey.save()
            return Response(
                {
                    "detail": "UserSurvey updated successfully.",
                    "user_survey_id": user_survey.id,
                    "is_validated": user_survey.is_validated,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Please provide the 'is_validated' field in the request data."},
            status=status.HTTP_400_BAD_REQUEST,
        )
