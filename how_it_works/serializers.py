from rest_framework import serializers

from .models import (
    FAQ,
    BadgesHIW,
    GetStarted,
    MentalHIW,
    PhysicalHIW,
    PrizesHIW,
    SocialHIW,
)


class GetStartedSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(default="get_started_hiw")

    class Meta:
        model = GetStarted
        exclude = ["id"]


class PhysicalHIWSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(default="physical_hiw")

    class Meta:
        model = PhysicalHIW
        exclude = ["id"]


class MentalHIWSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(default="mental_hiw")

    class Meta:
        model = MentalHIW
        exclude = ["id"]


class SocialHIWSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(default="social_hiw")

    class Meta:
        model = SocialHIW
        exclude = ["id"]


class PrizesHIWSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(default="prizes_hiw")

    class Meta:
        model = PrizesHIW
        exclude = ["id"]


class BadgesHIWSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(default="badge_hiw")

    class Meta:
        model = BadgesHIW
        exclude = ["id"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"


class HowItWorksSerializer(serializers.Serializer):
    """
    Main serializer aggregating all 'How It Works' sections.
    """

    get_started = GetStartedSerializer(required=False)
    physical_hiw = PhysicalHIWSerializer(required=False)
    mental_hiw = MentalHIWSerializer(required=False)
    social_hiw = SocialHIWSerializer(required=False)
    prizes_hiw = PrizesHIWSerializer(
        required=False
    )  # BUG FIXED: Was PhysicalHIWSerializer
    badges_hiw = BadgesHIWSerializer(required=False)
