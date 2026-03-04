from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class tailored for HttpOnly cookie-based token delivery.

    This class overrides the default JWTAuthentication behavior to extract the
    access token directly from the request cookies. It implements mandatory
    CSRF validation to mitigate Cross-Site Request Forgery vulnerabilities
    inherent to cookie-based authentication schemes.
    """

    def enforce_csrf(self, request):
        """
        Enforces standard Django CSRF validation for the current request.

        This method utilizes Django REST Framework's internal CSRFCheck to
        validate the X-CSRFToken header against the CSRF cookie, ensuring
        that state-changing requests (POST, PUT, DELETE, etc.) are legitimate.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Raises:
            PermissionDenied: If the CSRF token is missing, invalid, or compromised.
        """

        def dummy_get_response(request):
            return None

        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})

        if reason:
            raise PermissionDenied(f"CSRF verification failed: {reason}")

    def authenticate(self, request):
        """
        Attempts to authenticate the request using a JWT access token extracted
        from the request cookies.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            tuple: A two-tuple of (user, validated_token) if authentication succeeds.
            None: If no authentication credentials are provided.

        Raises:
            AuthenticationFailed: If the token is invalid, expired, or malformed.
        """
        raw_token = request.COOKIES.get("access_token")

        # Fallback to standard Authorization header if cookie is absent
        # (Useful for machine-to-machine communication or server-side rendering)
        if raw_token is None:
            header = self.get_header(request)
            if header is not None:
                raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)

            if user is None:
                raise AuthenticationFailed(
                    "User matching this token does not exist or is inactive."
                )

        except Exception as e:
            # Catch underlying simplejwt exceptions and unify the error response
            raise AuthenticationFailed("Invalid or expired token.")

        # Enforce CSRF protection to secure the cookie-based session
        self.enforce_csrf(request)

        return user, validated_token
