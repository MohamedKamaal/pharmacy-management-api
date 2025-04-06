import factory
from django.contrib.auth import get_user_model
from pytest_factoryboy import register

User = get_user_model()

@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ["email"]

    email = factory.Faker("email")
    role = factory.Iterator(User.Role.values)
    password = factory.PostGenerationMethodCall("set_password", "password123")
