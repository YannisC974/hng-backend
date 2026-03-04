import logging
import random
import string
from typing import Type

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models

# Initialize a logger for this module
logger = logging.getLogger(__name__)


def code_slug_generator(
    size: int = 12, chars: str = string.ascii_letters + string.digits
) -> str:
    """
    Generates a cryptographically safe-ish random string of specified length.

    Args:
        size (int): The length of the generated code. Defaults to 12.
        chars (str): The pool of characters to choose from. Defaults to alphanumeric.

    Returns:
        str: A randomly generated string.
    """
    return "".join(random.choice(chars) for _ in range(size))


def create_slug_shortcode(model_: Type[models.Model], size: int = 12) -> str:
    """
    Creates a guaranteed unique slug shortcode for a given Django model.

    This function uses a while loop instead of recursion to prevent potential
    RecursionError (stack overflow) in edge cases where collisions are frequent.

    Args:
        model_ (Type[models.Model]): The Django model class to check against.
        size (int): The length of the slug to generate.

    Returns:
        str: A unique slug that does not currently exist in the database.
    """
    while True:
        new_code = code_slug_generator(size=size)
        # Assuming the model has a 'slug' field
        if not model_.objects.filter(slug=new_code).exists():
            return new_code


def generate_code(size: int = 6, chars: str = string.digits) -> str:
    """
    Generates a random numeric code, typically used for OTPs or activation codes.

    Args:
        size (int): The length of the code. Defaults to 6.
        chars (str): The pool of characters. Defaults to digits only.

    Returns:
        str: A random string of digits.
    """
    return "".join(random.choice(chars) for _ in range(size))


def create_activation_code(model_: Type[models.Model], size: int = 6) -> str:
    """
    Creates a guaranteed unique activation code for a given Django model.

    Prevents recursion limits by using a while loop. Note: ensures that the
    underlying model has an 'activation_code' field.

    Args:
        model_ (Type[models.Model]): The Django model class.
        size (int): The length of the activation code. Defaults to 6.

    Returns:
        str: A unique numeric activation code.
    """
    while True:
        code = generate_code(size=size)
        if not model_.objects.filter(activation_code=code).exists():
            return code


def send_activation_email(
    to_email: str, token: str, domain: str, email_type: str = "register"
) -> None:
    """
    Dispatches a transactional email to the user for account activation or password reset.

    Args:
        to_email (str): The recipient's email address.
        token (str): The unique JWT or activation token.
        domain (str): The base domain of the frontend application (e.g., 'https://myapp.com').
        email_type (str): The context of the email. Must be 'register' or 'forgot_pass'.

    Note:
        In a production environment with high traffic, `email.send()` should be
        offloaded to a background task queue (like Celery) to prevent blocking
        the main HTTP request thread.
    """

    # Strip trailing slashes from domain to prevent double slashes in URLs
    base_url = domain.rstrip("/")

    if email_type == "register":
        title = "Activate Your Account"
        # Points to the frontend route handling account verification
        action_link = f"{base_url}/accounts/activate/{token}/"
        content = f"Welcome! Please click the following link to activate your account:\n{action_link}"

    elif email_type == "forgot_pass":
        title = "Reset Your Password"
        # Points to the frontend route handling password resets
        action_link = f"{base_url}/accounts/password-reset/{token}/"
        content = f"You requested a password reset. Click the following link to choose a new password:\n{action_link}"

    else:
        logger.error(
            f"Invalid email_type '{email_type}' provided to send_activation_email."
        )
        raise ValueError("email_type must be either 'register' or 'forgot_pass'")

    logger.info(f"Preparing to send '{email_type}' email to {to_email}")

    email = EmailMessage(
        subject=title, body=content, from_email=settings.EMAIL_HOST_USER, to=[to_email]
    )

    try:
        email.send(fail_silently=False)
        logger.info(f"Successfully sent '{email_type}' email to {to_email}")
    except Exception as e:
        # Catch and log SMTP exceptions without crashing the calling function completely,
        # or handle it based on your strictness requirements.
        logger.error(f"Failed to send email to {to_email}. Error: {str(e)}")
        raise
