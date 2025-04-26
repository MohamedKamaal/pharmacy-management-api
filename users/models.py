from django.db import models 
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the User model using email as the unique identifier.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.

        Args:
            email (str): The email address of the user.
            password (str): The raw password for the user.
            **extra_fields: Additional keyword arguments for the user instance.

        Returns:
            User: The newly created user instance.

        Raises:
            ValueError: If the email is not provided.
            ValidationError: If the email format is invalid.
        """
        if not email:
            raise ValueError("The email field must be set")
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("This is not a valid email format")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a normal user with default role 'Cashier'.

        Returns:
            User: A user instance with role CASHIER.
        """
        extra_fields.setdefault("role", User.Role.CASHIER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates a superuser with all permissions.

        Returns:
            User: A superuser instance.
        """
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email instead of username for authentication.
    """

    username = None  # Username field is removed
    email = models.EmailField("Email", unique=True, db_index=True)

    class Role(models.TextChoices):
        """
        Enum for user roles.
        """
        ACCOUNTANT = ("accountant", "Accountant")
        PHARMACIST = ("pharmacist", "Pharmacist")
        CASHIER = ("cashier", "Cashier")
        ADMIN = ("admin", "Admin")

    role = models.CharField("Role", max_length=20, choices=Role.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        """
        String representation of the user.
        """
        return f"{self.email} ({self.role})"
