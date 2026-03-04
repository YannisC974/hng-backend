from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Badge,
    DailyPrize,
    Medal,
    Trophy,
    UserBadge,
    UserMedal,
    UserPrize,
    UserTrophy,
)

User = get_user_model()


class MinimalUserSerializer(serializers.ModelSerializer):
    """Safe serializer for User avoiding non-existent fields."""

    class Meta:
        model = User
        fields = ["id", "email"]


class DailyPrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrize
        fields = "__all__"


class UserPrizeSerializer(serializers.ModelSerializer):
    user = MinimalUserSerializer(read_only=True)
    prize = DailyPrizeSerializer(read_only=True)

    class Meta:
        model = UserPrize
        fields = "__all__"


class MedalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medal
        fields = "__all__"


class UserMedalSerializer(serializers.ModelSerializer):
    user = MinimalUserSerializer(read_only=True)
    medal = MedalSerializer(read_only=True)

    class Meta:
        model = UserMedal
        fields = "__all__"


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = "__all__"


class UserBadgeSerializer(serializers.ModelSerializer):
    user = MinimalUserSerializer(read_only=True)
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = "__all__"


class TrophySerializer(serializers.ModelSerializer):
    class Meta:
        model = Trophy
        fields = "__all__"


class UserTrophySerializer(serializers.ModelSerializer):
    user = MinimalUserSerializer(read_only=True)
    trophy = TrophySerializer(read_only=True)

    class Meta:
        model = UserTrophy
        fields = "__all__"
