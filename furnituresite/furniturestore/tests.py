from django.test import TestCase
from furniturestore.models import FurnitureProduct

class FurnitureProductModelTest(TestCase):
    def setUp(self):
        self.product = FurnitureProduct.objects.create(
            name="Стіл",
            description="Дерев'яний стіл",
            price=1000.00
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Стіл")
        self.assertEqual(self.product.description, "Дерев'яний стіл")
        self.assertEqual(self.product.price, 1000.00)