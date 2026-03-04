from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DailyPrize(models.Model):
    """
    Model representing a daily prize from a sponsor/company.
    """

    day = models.CharField(
        max_length=100, verbose_name="Challenge day", blank=True, null=True
    )
    company_name = models.CharField(max_length=100)
    content = models.CharField(max_length=100)
    prize_name = models.CharField(max_length=100)
    description = models.TextField()

    # Media mapping
    logo = models.ImageField(upload_to="prizes/logos/")
    thumbnail_video = models.ImageField(
        upload_to="prizes/thumbnails/", blank=True, null=True
    )
    video_link = models.URLField()

    # Socials and links
    ig_link = models.URLField(blank=True, null=True)
    tiktok_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    yt_link = models.URLField(blank=True, null=True, verbose_name="Youtube link")
    app_store_link = models.URLField(
        blank=True, null=True, verbose_name="App store link"
    )
    play_store_link = models.URLField(
        blank=True, null=True, verbose_name="Play store link"
    )

    class Meta:
        verbose_name = "Daily Prize"
        verbose_name_plural = "Daily Prizes"
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.company_name


class UserPrize(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_prizes")
    prize = models.ForeignKey(
        DailyPrize, on_delete=models.CASCADE, related_name="prizes_won"
    )
    access_code = models.CharField(max_length=100)
    date_awarded = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Prize"
        verbose_name_plural = "User Prizes"
        ordering = ["-date_awarded"]

    def __str__(self) -> str:
        identifier = getattr(self.user, "email", self.user.id)
        return f"{identifier} - {self.prize.prize_name}"


class AwardBase(models.Model):
    """
    Abstract base class for all achievement types (Medals, Badges, Trophies).
    """

    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to="prizes/awards/images/", blank=True, null=True)
    file = models.FileField(upload_to="prizes/awards/files/", blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name or "Unnamed Award"


# --- MEDALS ---
class Medal(AwardBase):
    class Meta:
        verbose_name = "Medal"
        verbose_name_plural = "Medals"
        ordering = ["id"]


class UserMedal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_medals")
    medal = models.ForeignKey(
        Medal, on_delete=models.CASCADE, related_name="prizes_won"
    )
    date_awarded = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Medal"
        verbose_name_plural = "User Medals"
        ordering = ["-date_awarded"]

    def __str__(self) -> str:
        identifier = getattr(self.user, "email", self.user.id)
        return f"{identifier} - {self.medal.name}"


# --- BADGES ---
class Badge(AwardBase):
    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["id"]


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE, related_name="prizes_won"
    )
    date_awarded = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Badge"
        verbose_name_plural = "User Badges"
        ordering = ["-date_awarded"]

    def __str__(self) -> str:
        identifier = getattr(self.user, "email", self.user.id)
        return f"{identifier} - {self.badge.name}"


# --- TROPHIES ---
class Trophy(AwardBase):
    class Meta:
        verbose_name = "Trophy"
        verbose_name_plural = "Trophies"
        ordering = ["id"]


class UserTrophy(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_trophies"
    )
    trophy = models.ForeignKey(
        Trophy, on_delete=models.CASCADE, related_name="prizes_won"
    )
    date_awarded = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Trophy"
        verbose_name_plural = "User Trophies"
        ordering = ["-date_awarded"]

    def __str__(self) -> str:
        identifier = getattr(self.user, "email", self.user.id)
        return f"{identifier} - {self.trophy.name}"
