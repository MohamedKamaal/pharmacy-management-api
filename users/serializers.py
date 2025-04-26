from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer to handle extra fields during registration.
    """
    username = None
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(User.Role.choices, required=True)

    def get_cleaned_data(self):
        """
        Returns cleaned data including extra fields.
        """
        data = super().get_cleaned_data()
        data.update({
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "role": self.validated_data.get("role", ""),
        })
        return data

    def save(self, request):
        """
        Saves the user after registration.
        """
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        user.role = self.cleaned_data.get("role")
        user.set_password(self.cleaned_data.get("password1"))
        user.save()
        setup_user_email(request, user, [])
        return user
