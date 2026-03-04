from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import (
    FAQ,
    BadgesHIW,
    GetStarted,
    MentalHIW,
    PhysicalHIW,
    PrizesHIW,
    SocialHIW,
)
from .serializers import FAQSerializer, HowItWorksSerializer


class HowItWorksView(generics.GenericAPIView):
    """
    API endpoint that returns the latest entry for each 'How It Works' category.
    Accessible to anyone.
    """

    serializer_class = HowItWorksSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Fetch the most recent object for each category
        context_data = {
            "get_started": GetStarted.objects.last(),
            "physical_hiw": PhysicalHIW.objects.last(),
            "mental_hiw": MentalHIW.objects.last(),
            "social_hiw": SocialHIW.objects.last(),
            "prizes_hiw": PrizesHIW.objects.last(),
            "badges_hiw": BadgesHIW.objects.last(),
        }

        # Filter out None values to keep the response clean
        filtered_data = {k: v for k, v in context_data.items() if v is not None}

        serializer = self.get_serializer(filtered_data)
        return Response(serializer.data)


class FAQView(generics.ListAPIView):
    """
    API endpoint that returns the list of all FAQs.
    Accessible to anyone.
    """

    queryset = FAQ.objects.all().order_by("-id")
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
