from django.db import models


class Instructor(models.Model):
    """
    Model representing an instructor for physical challenges.
    """

    name = models.CharField(max_length=100, verbose_name="Instructor name")
    description = models.TextField()
    # Added upload_to to keep the media folder organized
    image = models.ImageField(upload_to="instructors/images/", blank=True, null=True)

    ig_link = models.URLField(blank=True, null=True)
    tiktok_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    yt_link = models.URLField(blank=True, null=True, verbose_name="Youtube link")

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"

    def __str__(self) -> str:
        return self.name or "Unnamed Instructor"


class CommonChallengeFields(models.Model):
    """
    Abstract base model containing fields common to all challenge types.
    """

    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Added upload_to paths
    banner_desktop = models.ImageField(
        upload_to="challenges/banners/desktop/", blank=True, null=True
    )
    banner_mobile = models.ImageField(
        upload_to="challenges/banners/mobile/", blank=True, null=True
    )
    thumbnail_square = models.ImageField(
        upload_to="challenges/thumbnails/square/", blank=True, null=True
    )
    thumbnail_mobile = models.ImageField(
        upload_to="challenges/thumbnails/mobile/", blank=True, null=True
    )

    class Meta:
        abstract = True


class AbstractPhysicalChallenge(CommonChallengeFields):
    """
    Abstract base model for physical challenges, inheriting common fields.
    """

    workout_name = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    required_equipments = models.CharField(max_length=100, blank=True, null=True)

    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, blank=True, null=True
    )
    video = models.URLField(max_length=250, blank=True, null=True)
    thumbnail_video = models.ImageField(
        upload_to="challenges/thumbnails/video/", blank=True, null=True
    )

    # Removed the 'description' field because it's already inherited from CommonChallengeFields

    class Meta:
        abstract = True


class ModeratePhysicalChallenge(AbstractPhysicalChallenge):
    """
    Model representing a moderate intensity physical challenge.
    """

    class Meta:
        verbose_name = "Moderate Physical Challenge"
        verbose_name_plural = "Moderate Physical Challenges"

    def __str__(self) -> str:
        return self.title or f"Moderate Physical Challenge {self.id}"


class IntensePhysicalChallenge(AbstractPhysicalChallenge):
    """
    Model representing a high intensity physical challenge.
    """

    class Meta:
        verbose_name = "Intense Physical Challenge"
        verbose_name_plural = "Intense Physical Challenges"

    def __str__(self) -> str:
        return self.title or f"Intense Physical Challenge {self.id}"


class SocialChallenge(CommonChallengeFields):
    """
    Model representing a social interaction challenge.
    """

    challenge = models.CharField(max_length=100, blank=True, null=True)
    # Removed the 'description' CharField because a TextField is inherited from CommonChallengeFields

    class Meta:
        verbose_name = "Social Challenge"
        verbose_name_plural = "Social Challenges"

    def __str__(self) -> str:
        return self.title or f"Social Challenge {self.id}"


class MentalChallenge(CommonChallengeFields):
    """
    Model representing a mental/cognitive challenge.
    """

    question = models.CharField(max_length=100, blank=True, null=True)
    # Removed the 'description' CharField because a TextField is inherited from CommonChallengeFields
    voice_recording = models.FileField(
        upload_to="challenges/audio/", blank=True, null=True
    )

    class Meta:
        verbose_name = "Mental Challenge"
        verbose_name_plural = "Mental Challenges"

    def __str__(self) -> str:
        return self.title or f"Mental Challenge {self.id}"


class Challenge(models.Model):
    """
    Main model that aggregates different types of challenges for a specific day.
    """

    day = models.CharField(
        max_length=100, verbose_name="Challenge day", blank=True, null=True
    )
    quote = models.TextField(blank=True, null=True)
    author_name = models.CharField(max_length=100, blank=True, null=True)

    video_link = models.URLField(max_length=250, blank=True, null=True)
    thumbnail_video = models.ImageField(
        upload_to="challenges/thumbnails/main_video/", blank=True, null=True
    )

    # Harmonized related_names for consistency and easier reverse querying
    moderate_physical = models.ForeignKey(
        ModeratePhysicalChallenge,
        related_name="daily_challenges",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    intense_physical = models.ForeignKey(
        IntensePhysicalChallenge,
        related_name="daily_challenges",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    mental = models.ForeignKey(
        MentalChallenge,
        related_name="daily_challenges",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    social = models.ForeignKey(
        SocialChallenge,
        related_name="daily_challenges",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"

    def __str__(self) -> str:
        return str(self.day) if self.day else f"Challenge Object ({self.id})"
