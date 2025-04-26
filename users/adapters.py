# users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for django-allauth to support additional fields during registration.
    """

    def save_user(self, request, user, form, commit=True):
        """
        Saves user instance with custom fields.
        """
        user = super().save_user(request, user, form, commit=False)
        user.email = form.cleaned_data.get('email')
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.set_password(form.cleaned_data.get('password1'))
        if commit:
            user.save()
        return user
