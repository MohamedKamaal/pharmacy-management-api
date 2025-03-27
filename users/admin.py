from django.contrib import admin
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

# Register your models here.
User = get_user_model()

@admin.register(User)
class UserAdmin(UserAdmin):
    model = User 
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ['first_name','last_name','email','is_active','is_staff','is_superuser',
                    'date_joined','role']
    list_filter = ['is_staff','is_active','is_superuser']
    fieldsets = (
        (
            _("Login credintials"),
            {
                "fields":(
                    "email","password"
                ),
            },
            
        ),
        (
            _("Personal Info"),
            {
                "fields":(
                    "first_name","last_name"
                ),
            },
        ),
        (
            _("Permissions and Groups"),
            {
                "fields":("role","is_active","is_staff","is_superuser","groups","user_permissions")
            },
        ),
        (
            _("Important Dates"),
            {
                "fields":("date_joined",)
            }
        ),
    )
    
    search_fields = ["email","username"]
    ordering = ["email"]