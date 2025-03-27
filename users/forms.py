from django.contrib.auth import get_user_model
from django import forms 
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name","last_name","email","password","is_active","is_staff","is_superuser","role"]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(
            email=email
        ).exists():
            raise forms.ValidationError("This email is already token")
        else:
            return email
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["first_name","last_name","email","password","is_active","is_staff","is_superuser","role"]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(
            email=email
        ).exists():
            raise forms.ValidationError("This email is already token")
        else:
            return email