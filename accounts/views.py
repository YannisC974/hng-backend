import json
import logging
import os

from django.conf import settings
from django.utils.crypto import get_random_string
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import MyUser
from .serializers import (
    CustomTokenObtainPairSerializer,
    MyUserRegistrationSerializer,
    MyUserSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegionSerializer,
)
from .utils import send_activation_email

logger = logging.getLogger(__name__)

# Pre-load geographical data into memory on startup
REGIONS_FILE_PATH = os.path.join(settings.BASE_DIR, "regions.json")
REGIONS_DATA = []
try:
    with open(REGIONS_FILE_PATH, "r", encoding="utf-8") as file:
        REGIONS_DATA = json.load(file)
except FileNotFoundError:
    logger.warning("Geographical data file 'regions.json' not found.")


class RegisterView(generics.CreateAPIView):
    """
    Handles new user registration and triggers the activation email dispatch.
    """

    queryset = MyUser.objects.all()
    serializer_class = MyUserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token = get_random_string(length=32)
        user.activation_token = token
        user.save(update_fields=["activation_token"])

        url_path = f"{request.scheme}://{request.get_host()}"
        send_activation_email(user.email, token, url_path, email_type="register")

        return Response(
            {
                "message": "User registered successfully. Please check your email to activate your account.",
            },
            status=status.HTTP_201_CREATED,
        )


class ActivationView(APIView):
    """
    Activates a user account based on the provided token.
    """

    permission_classes = [AllowAny]

    def get(self, request, token, *args, **kwargs):
        try:
            user = MyUser.objects.get(activation_token=token)
            user.is_active = True
            user.activation_token = None
            user.save()
            return Response(
                {"message": "Account activated successfully."},
                status=status.HTTP_200_OK,
            )
        except MyUser.DoesNotExist:
            return Response(
                {"message": "Invalid activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Validates user credentials and sets HttpOnly cookies for JWT tokens.
    """

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            is_production = not settings.DEBUG

            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=is_production,
                samesite="None" if is_production else "Lax",
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                path="/",
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=is_production,
                samesite="None" if is_production else "Lax",
                max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
                path="/",
            )

            response.data.pop("access", None)
            response.data.pop("refresh", None)
            response.data["message"] = "Login successful"

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Refreshes the access token using the HttpOnly refresh token cookie.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get("access")
            is_production = not settings.DEBUG

            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=is_production,
                samesite="None" if is_production else "Lax",
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                path="/",
            )
            response.data.pop("access", None)
            response.data.pop("refresh", None)
            response.data["message"] = "Token refreshed successfully"

        return response


class VerifyTokenView(APIView):
    """
    Verifies the validity of the current access token.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return Response(
                {"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            AccessToken(access_token)
            return Response({"valid": True}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"valid": False}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Blacklists the refresh token and clears authentication cookies.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(
                {"message": "Successfully logged out."}, status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response
        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserInfoView(APIView):
    """
    Retrieves the authenticated user's profile information.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MyUserSerializer(instance=request.user)
        return Response(serializer.data)


class UsersListView(generics.ListAPIView):
    """
    Lists all users, ordered by birth year.
    """

    queryset = MyUser.objects.all().order_by("born_year")
    serializer_class = MyUserSerializer
    permission_classes = [IsAuthenticated]


class PasswordForgotView(generics.CreateAPIView):
    """
    Initiates the password reset process by generating a token and sending an email.
    """

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = MyUser.objects.filter(email=email).first()
        if user:
            refresh = RefreshToken.for_user(user)
            reset_token = str(refresh.access_token)
            user.reset_code = reset_token
            user.save(update_fields=["reset_code"])

            url_path = f"{request.scheme}://{request.get_host()}"
            send_activation_email(
                user.email, reset_token, domain=url_path, email_type="forgot_pass"
            )

        return Response(
            {"detail": "If an account exists, a reset token has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordForgotConfirmView(generics.CreateAPIView):
    """
    Confirms the password reset using the token provided via email.
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_code = serializer.validated_data["reset_code"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = MyUser.objects.get(reset_code=reset_code)
        except MyUser.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired reset code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.reset_code = None
        user.save()

        return Response(
            {"detail": "Password reset successfully."}, status=status.HTTP_200_OK
        )


class GetCountryListView(generics.ListAPIView):
    """
    Retrieves the list of all countries.
    """

    serializer_class = RegionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=REGIONS_DATA, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class GetStateListView(generics.ListAPIView):
    """
    Retrieves the list of states for a specific country.
    """

    serializer_class = RegionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        country_name = kwargs.get("country_name")

        country_data = next(
            (item for item in REGIONS_DATA if item.get("name") == country_name), None
        )

        if not country_data or not country_data.get("states"):
            states = [{"name": country_name}]
        else:
            states = country_data["states"]

        serializer = self.serializer_class(data=states, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class GetCityListView(generics.ListAPIView):
    """
    Retrieves the list of cities for a specific state and country.
    """

    serializer_class = RegionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        country_name = kwargs.get("country_name")
        state_name = kwargs.get("state_name")

        country_data = next(
            (item for item in REGIONS_DATA if item.get("name") == country_name), None
        )

        cities = []
        if country_data and country_data.get("states"):
            state_data = next(
                (
                    item
                    for item in country_data["states"]
                    if item.get("name") == state_name
                ),
                None,
            )
            if state_data and state_data.get("cities"):
                cities = state_data["cities"]

        if not cities:
            cities = [{"name": state_name if state_name else country_name}]

        serializer = self.serializer_class(data=cities, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
