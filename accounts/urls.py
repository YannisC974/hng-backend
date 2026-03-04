from django.urls import path

from .views import (
    ActivationView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    GetCityListView,
    GetCountryListView,
    GetStateListView,
    LogoutView,
    PasswordForgotConfirmView,
    PasswordForgotView,
    RegisterView,
    UserInfoView,
    UsersListView,
    VerifyTokenView,
)

app_name = "accounts"

urlpatterns = [
    # ==========================================
    # AUTHENTICATION & TOKENS
    # ==========================================
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("verify-token/", VerifyTokenView.as_view(), name="verify-token"),
    # ==========================================
    # REGISTRATION & ACTIVATION
    # ==========================================
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<str:token>/", ActivationView.as_view(), name="activate"),
    # ==========================================
    # PASSWORD MANAGEMENT
    # ==========================================
    path("password-forgot/", PasswordForgotView.as_view(), name="password-forgot"),
    # Token is expected in the POST body, so we remove it from the URL path
    path(
        "password-forgot-confirm/",
        PasswordForgotConfirmView.as_view(),
        name="password-forgot-confirm",
    ),
    # ==========================================
    # USER PROFILE
    # ==========================================
    path("user-info/", UserInfoView.as_view(), name="user-info"),
    path("list/", UsersListView.as_view(), name="list"),
    # ==========================================
    # GEOGRAPHICAL DATA
    # ==========================================
    path("get-countries/", GetCountryListView.as_view(), name="get-countries"),
    # Added 'str:' path converters for better route matching and security
    path(
        "get-states/<str:country_name>/", GetStateListView.as_view(), name="get-states"
    ),
    path(
        "get-cities/<str:country_name>/<str:state_name>/",
        GetCityListView.as_view(),
        name="get-cities",
    ),
]
