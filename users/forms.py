from django.contrib.auth import get_user_model
from django import forms 
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating new users from the admin interface.
    """

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "password",
            "is_active", "is_staff", "is_superuser", "role"
        ]

    def clean_email(self):
        """
        Validates that the email is unique.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already token")
        return email


class CustomUserChangeForm(UserChangeForm):
    """
    Custom form for updating users from the admin interface.
    """

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "password",
            "is_active", "is_staff", "is_superuser", "role"
        ]

    def clean_email(self):
        """
        Validates that the email is unique.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already token")
        return email
