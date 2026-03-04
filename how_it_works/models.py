from django.db import models


class HIWCommonFields(models.Model):
    """
    Abstract base model containing fields common to all 'How It Works' sections.
    """

    title = models.CharField(max_length=100)
    video_link = models.URLField()
    description = models.TextField()
    # Organized media storage
    thumbnail = models.ImageField(
        upload_to="how_it_works/thumbnails/", blank=True, null=True
    )

    class Meta:
        abstract = True
        ordering = ["-id"]


class GetStarted(HIWCommonFields):
    class Meta:
        verbose_name = "Get Started"
        verbose_name_plural = "Get Started"

    def __str__(self) -> str:
        return self.title


class PhysicalHIW(HIWCommonFields):
    class Meta:
        verbose_name = "Physical HIW"
        verbose_name_plural = "Physical HIWs"

    def __str__(self) -> str:
        return self.title


class MentalHIW(HIWCommonFields):
    class Meta:
        verbose_name = "Mental HIW"
        verbose_name_plural = "Mental HIWs"

    def __str__(self) -> str:
        return self.title


class SocialHIW(HIWCommonFields):
    class Meta:
        verbose_name = "Social HIW"
        verbose_name_plural = "Social HIWs"

    def __str__(self) -> str:
        return self.title


class PrizesHIW(HIWCommonFields):
    class Meta:
        verbose_name = "Prizes HIW"
        verbose_name_plural = "Prizes HIWs"

    def __str__(self) -> str:
        return self.title


class BadgesHIW(HIWCommonFields):
    class Meta:
        verbose_name = "Badges HIW"
        verbose_name_plural = "Badges HIWs"

    def __str__(self) -> str:
        return self.title


class FAQ(models.Model):
    """
    Model representing Frequently Asked Questions.
    """

    question = models.CharField(max_length=100)
    answer = models.TextField()

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.question
