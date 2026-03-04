from django.urls import path

from .views import ChallengeDetailView, ChallengeListView

app_name = "challenges"

urlpatterns = [
    # Retrieve a list of all challenges
    path("list/", ChallengeListView.as_view(), name="list"),
    # Retrieve a specific challenge by its 'day' attribute
    path("detail/<str:day>/", ChallengeDetailView.as_view(), name="detail"),
]
