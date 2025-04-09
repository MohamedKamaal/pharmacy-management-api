# conftest.py
import pytest
from pytest_factoryboy import register
from .factories import SupplierFactory, ManufacturerFactory, CategoryFactory, ActiveIngredientFactory, MedicineFactory, BatchFactory

register(SupplierFactory)
register(ManufacturerFactory)
register(CategoryFactory)
register(ActiveIngredientFactory)
register(MedicineFactory)
register(BatchFactory)