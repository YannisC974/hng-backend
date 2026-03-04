from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Challenge
from .serializers import ChallengeSerializer


class ChallengeListView(generics.ListAPIView):
    """
    API endpoint that allows authenticated users to list all challenges,
    ordered by the most recently created.
    """

    queryset = Challenge.objects.all().order_by("-id")
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]


class ChallengeDetailView(generics.RetrieveAPIView):
    """
    API endpoint that allows authenticated users to retrieve a specific
    challenge details using its 'day' identifier.
    """

    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "day"
