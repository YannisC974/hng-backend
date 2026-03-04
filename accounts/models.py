from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from .utils import create_slug_shortcode

AUTH_PROVIDERS = {
    "facebook": "facebook",
    "google": "google",
    "apple": "apple",
    "email": "email",
}


class MyUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
        self,
        email,
        password=None,
        is_active=False,
        is_staff=False,
        is_superuser=False,
        **kwargs,
    ):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **kwargs,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        Create and save a SuperUser with the given email and password.
        """
        # On délègue la création à create_user en passant les bons flags
        # Cela évite de sauvegarder l'utilisateur deux fois (INSERT puis UPDATE)
        return self.create_user(
            email=email,  # Pas besoin de normalize ici, create_user s'en charge
            password=password,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            **kwargs,
        )


class MyUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model replacing Django's default user.
    Uses email as the primary identifier.
    """

    email = models.EmailField(unique=True, max_length=120, verbose_name="E-mail")
    username = models.CharField(max_length=100, blank=True, null=True, unique=True)

    auth_provider = models.CharField(
        max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get("email")
    )

    slug = models.SlugField(unique=True)
    activation_token = models.CharField(max_length=255, blank=True, null=True)
    reset_code = models.CharField(max_length=254, blank=True, null=True)

    # User Profile Data
    born_year = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    is_student = models.BooleanField(default=False)
    university_name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # Activity & Metrics
    timestamp = models.DateTimeField(auto_now_add=True)
    current_active_days = models.IntegerField(default=0)
    max_consecutive_active_days = models.IntegerField(default=0)

    # Permissions & Status
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # is_superuser est automatiquement géré par PermissionsMixin

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS est vide car 'email' est le USERNAME_FIELD et le password est requis par défaut.
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    # Les méthodes has_perm et has_module_perms peuvent être retirées
    # car elles sont gérées nativement et de manière plus complète par PermissionsMixin.
    # Si vous voulez forcer le fait qu'un superuser a tous les droits (ce qui est le cas par défaut),
    # PermissionsMixin s'en charge déjà.

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to generate a unique slug
        before saving the object to the database for the first time.
        """
        if not self.slug:
            self.slug = create_slug_shortcode(model_=MyUser, size=12)
        return super().save(*args, **kwargs)
