from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="profile.gender")
    city = serializers.CharField(source="profile.city")
    phone_number = PhoneNumberField(source="profile.phone_number")
    photo = serializers.ReadOnlyField(source="profile.photo.url")

    class Meta:
        model = User
        fields = ["id","email","first_name","last_name","gender","phone_number","city","photo","country"]
    
    def to_representation(self, instance):
        representation = super(UserSerializer,self).to_representation(instance=instance)
        if instance.is_superuser:
            representation["admin"]=True
        return representation
    
    
class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Remove the username field
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        # Call the parent class's get_cleaned_data method
        data = super().get_cleaned_data()
        # Add custom fields
        data.update({
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        })
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)  # Don't save yet

        # Set custom fields
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        user.set_password(self.cleaned_data.get("password1"))  # Properly hash the password

        user.save()  # Save the user to the database
        setup_user_email(request, user, [])  # Set up the user's email

        return user


