# conftest.py
import pytest
from pytest_factoryboy import register
from .factories import UserFactory

register(UserFactory)