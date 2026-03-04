from rest_framework import serializers

from challenges.models import Challenge

from .models import Survey, UserSurvey


class SurveySubmissionSerializer(serializers.Serializer):
    """
    Dedicated serializer for handling incoming survey submissions.
    """

    challenge = serializers.PrimaryKeyRelatedField(queryset=Challenge.objects.all())
    physical_done = serializers.BooleanField(default=False)
    mental_done = serializers.BooleanField(default=False)
    social_done = serializers.BooleanField(default=False)
    video_link = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        # Ensure at least one challenge section was marked as done
        if not any(
            [
                attrs.get("physical_done"),
                attrs.get("mental_done"),
                attrs.get("social_done"),
            ]
        ):
            raise serializers.ValidationError(
                "You must complete at least one part of the challenge."
            )
        return attrs


class UserSurveySerializer(serializers.ModelSerializer):
    """
    Serializer for outgoing UserSurvey data.
    """

    class Meta:
        model = UserSurvey
        fields = "__all__"
