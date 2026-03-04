from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserModelTests(APITestCase):
    """
    Test suite for the custom MyUser model and MyUserManager.
    """

    def test_create_user_successful(self):
        user = User.objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.check_password("foo"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.slug)

    def test_create_user_no_email_fails(self):
        with self.assertRaisesMessage(ValueError, "Users must have an email address"):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser_successful(self):
        admin_user = User.objects.create_superuser(
            email="super@user.com", password="foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class AuthenticationTests(APITestCase):
    """
    Test suite for JWT cookie-based authentication and token endpoints.
    """

    def setUp(self):
        self.login_url = reverse("accounts:login")
        self.logout_url = reverse("accounts:logout")
        self.user_password = "SecurePassword123!"
        self.user = User.objects.create_user(
            email="auth@example.com", password=self.user_password, is_active=True
        )

    def test_login_sets_httponly_cookies(self):
        response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.user_password}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_login_inactive_user_fails(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.user_password}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)

    def test_logout_clears_cookies_and_blacklists_token(self):
        # Authenticate first to set cookies
        login_response = self.client.post(
            self.login_url, {"email": self.user.email, "password": self.user_password}
        )

        refresh_token = login_response.cookies["refresh_token"].value
        self.client.cookies["refresh_token"] = refresh_token

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")


class RegistrationAndActivationTests(APITestCase):
    """
    Test suite for user registration, token generation, and account activation.
    """

    def setUp(self):
        self.register_url = reverse("accounts:register")
        self.user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(email=self.user_data["email"])
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.activation_token)

        # Verify activation email was dispatched
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.activation_token, mail.outbox[0].body)

    def test_user_activation_success(self):
        # Create an inactive user manually
        user = User.objects.create_user(
            email="inactive@example.com", password="foo", is_active=False
        )
        user.activation_token = "valid_test_token_123"
        user.save()

        activation_url = reverse(
            "accounts:activate", kwargs={"token": user.activation_token}
        )
        response = self.client.get(activation_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNone(user.activation_token)


class PasswordManagementTests(APITestCase):
    """
    Test suite for the password reset workflow.
    """

    def setUp(self):
        self.forgot_url = reverse("accounts:password-forgot")
        self.confirm_url = reverse("accounts:password-forgot-confirm")
        self.user = User.objects.create_user(
            email="reset@example.com", password="OldPassword123!", is_active=True
        )

    def test_password_forgot_sends_email(self):
        response = self.client.post(self.forgot_url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_code)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.reset_code, mail.outbox[0].body)

    def test_password_forgot_confirm_success(self):
        self.user.reset_code = "valid_reset_token"
        self.user.save()

        new_password = "NewSecurePassword123!"
        response = self.client.post(
            self.confirm_url,
            {
                "reset_code": self.user.reset_code,
                "new_password": new_password,
                "new_password2": new_password,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertIsNone(self.user.reset_code)
        self.assertTrue(self.user.check_password(new_password))
