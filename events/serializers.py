from django.contrib.auth import get_user_model
from rest_framework import serializers

from challenges.serializers import InstructorSerializer

from .models import Event, UserEvent

User = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event objects including nested instructors.
    """

    instructor = InstructorSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        # 'day' removed as it was deleted from the model in migrations
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "date",
            "link",
            "type_of_event",
            "requirements",
            "instructor",
            "thumbnail",
        ]


class UserEventSerializer(serializers.ModelSerializer):
    """
    Serializer for UserEvent subscriptions.
    """

    event_details = EventSerializer(source="event", read_only=True)
    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), write_only=True
    )

    class Meta:
        model = UserEvent
        fields = ["id", "user", "event", "event_details"]
        read_only_fields = ["user"]

    def create(self, validated_data):
        # Automatically assign the logged-in user
        user = self.context["request"].user
        return UserEvent.objects.create(user=user, **validated_data)
