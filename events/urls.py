from django.urls import path

from .views import *

app_name = "events"
urlpatterns = [
    # path("sign-up/<int:pk>/", EventSignUpView.as_view(), name="sign-up"),
    # path("list/", EventListView.as_view(), name="list"),
    # path("detail/<int:pk>/", EventDetailView.as_view(), name="detail"),
    path("events-by-date/<date>/", EventsByDateView.as_view(), name="events-by-date"),
    path("future-events/", FutureEventsView.as_view(), name="future-events"),
    path("user-events/", UserEventListView.as_view(), name="user-events"),
    path(
        "user-events/create/", UserEventCreateView.as_view(), name="user-event-create"
    ),
    path(
        "user-events/destroy/",
        UserEventDestroyView.as_view(),
        name="user-event-destroy",
    ),
]
