from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import DailyPrize, UserBadge, UserMedal, UserTrophy
from .serializers import (
    DailyPrizeSerializer,
    UserBadgeSerializer,
    UserMedalSerializer,
    UserTrophySerializer,
)


class DailyPrizeListView(generics.ListAPIView):
    """List all daily prizes."""

    queryset = DailyPrize.objects.all()
    serializer_class = DailyPrizeSerializer
    permission_classes = [permissions.IsAuthenticated]


class DailyPrizesListView(generics.ListAPIView):
    """List daily prizes filtered by the requested day."""

    serializer_class = DailyPrizeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        day = self.request.query_params.get("day", None)
        if not day:
            return DailyPrize.objects.none()
        return DailyPrize.objects.filter(day=str(day))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"detail": "No prizes found for the specified day."},
                status=status.HTTP_404_NOT_FOUND,
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserMedalListView(generics.ListAPIView):
    """List medals acquired by the authenticated user."""

    serializer_class = UserMedalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserMedal.objects.filter(user=self.request.user)


class UserBadgeListView(generics.ListAPIView):
    """List badges acquired by the authenticated user."""

    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)


class UserTrophyListView(generics.ListAPIView):
    """List trophies acquired by the authenticated user."""

    serializer_class = UserTrophySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserTrophy.objects.filter(user=self.request.user)
