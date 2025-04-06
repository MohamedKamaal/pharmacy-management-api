from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
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
        """Create a normal user (default role: Cashier)"""
        extra_fields.setdefault("role", User.Role.CASHIER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create an admin with all permissions"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(email, password,role="admin", **extra_fields)


class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField("Email", unique=True, db_index=True)
    
    
    class Role(models.TextChoices):
        ACCOUNTANT = ("accountant", "Accountant")
        PHARMACIST = ("pharmacist", "Pharmacist")
        CASHIER = ("cashier", "Cashier")
        ADMIN = ("admin", "Admin")

    role = models.CharField("Role", max_length=20, choices=Role.choices)

    USERNAME_FIELD = "email"  # Use email for authentication
    REQUIRED_FIELDS = []  # Fields required when creating users

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
