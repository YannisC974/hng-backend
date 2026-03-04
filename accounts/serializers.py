from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import MyUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token serializer.
    Inherits from SimpleJWT's default serializer to handle user authentication
    and token generation. You can add custom claims to the token here if needed.
    """

    def validate(self, attrs):
        # The parent class handles authentication and checks if the user is_active.
        # It raises AuthenticationFailed if credentials are wrong or user is inactive.
        data = super().validate(attrs)

        # At this point, self.user is available.
        # You can inject extra user data into the response if needed:
        # data['user_id'] = self.user.id

        return data


class MyUserSerializer(serializers.ModelSerializer):
    """
    Standard serializer for retrieving and displaying user profile data.
    """

    class Meta:
        model = MyUser
        fields = [
            "id",
            "email",
            "username",
            "auth_provider",
            "slug",
            "born_year",
            "gender",
            "is_student",
            "university_name",
            "country",
            "state",
            "city",
            "is_active",
            "current_active_days",
            "max_consecutive_active_days",
        ]
        read_only_fields = [
            "id",
            "slug",
            "is_active",
            "current_active_days",
            "max_consecutive_active_days",
        ]


class MyUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling new user registrations.
    Validates passwords and safely hashes them via the model's manager.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = MyUser
        fields = [
            "email",
            "username",
            "password",
            "password2",
            "born_year",
            "gender",
            "is_student",
            "university_name",
            "country",
            "state",
            "city",
        ]
        # Note: Uniqueness validation for 'email' and 'username' is automatically
        # handled by DRF because they have unique=True on the MyUser model.

    def validate(self, attrs):
        """
        Custom validation to ensure password confirmation matches.
        """
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        """
        Removes the confirmation password and uses the custom user manager
        to securely create the user.
        """
        validated_data.pop("password2")
        # create_user securely hashes the password
        return MyUser.objects.create_user(**validated_data)


# Note: MyUserLoginSerializer was removed because CustomTokenObtainPairSerializer
# is the standard and correct way to handle login when using SimpleJWT.


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for initiating a password reset process via email.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        # Security Note: Returning a validation error if the email doesn't exist
        # allows "Email Enumeration" attacks. For higher security apps,
        # you might want to return success even if the email doesn't exist.
        if not MyUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email address does not exist."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset using the emailed reset code.
    """

    reset_code = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password2"):
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for authenticated users wanting to change their password.
    Requires verification of the old password.
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value


class RegionSerializer(serializers.Serializer):
    """
    Simple serializer for returning region data (countries, states, cities).
    """

    name = serializers.CharField()
