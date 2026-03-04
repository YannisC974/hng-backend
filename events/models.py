from django.contrib.auth import get_user_model
from django.db import models

from challenges.models import Instructor

User = get_user_model()


class Event(models.Model):
    """
    Model representing a scheduled event.
    """

    title = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    link = models.URLField(verbose_name="Link to the event")
    type_of_event = models.CharField(max_length=100, verbose_name="Event type")
    requirements = models.CharField(max_length=100)
    instructor = models.ManyToManyField(Instructor, blank=True)
    thumbnail = models.ImageField(upload_to="events/thumbnails/", blank=True, null=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        # Explicit ordering to prevent pagination warnings
        ordering = ["-date", "-start_time"]

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"


class UserEvent(models.Model):
    """
    Model representing a user's subscription to an event.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_subscriptions"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_subscribers"
    )

    class Meta:
        verbose_name = "User Event"
        verbose_name_plural = "User Events"
        # Prevent a user from subscribing to the same event twice
        unique_together = ("user", "event")
        # Explicit ordering for consistent API results
        ordering = ["-id"]

    def __str__(self) -> str:
        # Use email for identification as defined in your custom user model
        return f"{self.user.email} subscribed to {self.event.title}"
