from rest_framework import serializers

from .models import (
    Challenge,
    Instructor,
    IntensePhysicalChallenge,
    MentalChallenge,
    ModeratePhysicalChallenge,
    SocialChallenge,
)


class InstructorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Instructor model.
    """

    class Meta:
        model = Instructor
        fields = "__all__"


class ModeratePhysicalChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for moderate physical challenges.
    Includes nested instructor details (read-only).
    """

    instructor = InstructorSerializer(read_only=True)

    class Meta:
        model = ModeratePhysicalChallenge
        fields = "__all__"


class IntensePhysicalChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for intense physical challenges.
    Includes nested instructor details (read-only).
    """

    instructor = InstructorSerializer(read_only=True)

    class Meta:
        model = IntensePhysicalChallenge
        fields = "__all__"


class MentalChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for mental challenges.
    """

    class Meta:
        model = MentalChallenge
        fields = "__all__"


class SocialChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for social challenges.
    """

    class Meta:
        model = SocialChallenge
        fields = "__all__"


class ChallengeSerializer(serializers.ModelSerializer):
    """
    Main serializer for daily challenges.
    Nests all sub-challenge categories as read-only objects.
    """

    moderate_physical = ModeratePhysicalChallengeSerializer(read_only=True)
    intense_physical = IntensePhysicalChallengeSerializer(read_only=True)
    mental = MentalChallengeSerializer(read_only=True)
    social = SocialChallengeSerializer(read_only=True)

    class Meta:
        model = Challenge
        fields = "__all__"
