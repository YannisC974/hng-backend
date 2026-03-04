from django.urls import path

from .views import (
    RandomUserSurveyChooseView,
    UpdateUserSurveyValidationView,
    UserSurveyCreateView,
)

app_name = "surveys"

urlpatterns = [
    # Changed from ViewSet to standard view mapping
    path("create/", UserSurveyCreateView.as_view(), name="create"),
    path(
        "choose-user-survey/<str:day>/",
        RandomUserSurveyChooseView.as_view(),
        name="choose-user-survey",
    ),
    path(
        "update-user-survey-validation/<int:pk>/",
        UpdateUserSurveyValidationView.as_view(),
        name="update-user-survey-validation",
    ),
]
