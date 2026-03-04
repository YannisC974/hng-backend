from django.contrib.auth import get_user_model
from django.db import models

from challenges.models import Challenge

User = get_user_model()


class Survey(models.Model):
    """
    Model representing the actual answers of a challenge survey.
    """

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, null=True)
    physical_done = models.BooleanField(default=False)
    mental_done = models.BooleanField(default=False)
    social_done = models.BooleanField(default=False)
    video_link = models.URLField(blank=True, null=True)

    # Automatically calculated based on the boolean fields above
    number_of_completed = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        verbose_name = "Survey"
        verbose_name_plural = "Surveys"
        ordering = ["-id"]

    def __str__(self) -> str:
        # Fixed: Removed reference to 'self.user' because it doesn't exist here
        day = getattr(self.challenge, "day", "Unknown Day")
        return f"Survey Answers - Challenge {day}"


class UserSurvey(models.Model):
    """
    Model linking a User to their Survey submission.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_surveys"
    )
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="survey_users"
    )

    # Validation flags
    is_choosed = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Survey"
        verbose_name_plural = "User Surveys"
        ordering = ["-id"]

    def __str__(self) -> str:
        email = getattr(self.user, "email", self.user.id)
        day = getattr(self.survey.challenge, "day", "Unknown")
        return f"{email} - Day {day}"
