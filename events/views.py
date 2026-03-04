from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event, UserEvent
from .serializers import EventSerializer, UserEventSerializer


class EventsByDateView(generics.ListAPIView):
    """
    Returns a list of events occurring on a specific date.
    """

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        date_param = self.kwargs.get("date")
        return Event.objects.filter(date=date_param)


class FutureEventsView(generics.ListAPIView):
    """
    Returns events within a specific time gap (default 14 days).
    """

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            gap = int(self.request.query_params.get("gap", 14))
        except ValueError:
            gap = 14

        today = timezone.now().date()
        end_date = today + timedelta(days=gap)
        return Event.objects.filter(date__gte=today, date__lte=end_date).order_by(
            "date", "start_time"
        )


class UserEventListView(generics.ListAPIView):
    """
    Lists all events the authenticated user is subscribed to.
    """

    serializer_class = UserEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserEvent.objects.filter(user=self.request.user)


class UserEventCreateView(generics.CreateAPIView):
    """
    Subscribes the authenticated user to an event.
    """

    serializer_class = UserEventSerializer
    permission_classes = [IsAuthenticated]


class UserEventDestroyView(generics.DestroyAPIView):
    """
    Unsubscribes the authenticated user from an event.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserEvent.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        event_id = request.data.get("event")
        try:
            subscription = self.get_queryset().get(event_id=event_id)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserEvent.DoesNotExist:
            return Response(
                {"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND
            )
