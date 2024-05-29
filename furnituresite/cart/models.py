from django.db import models
from django.conf import settings
from furniturestore.models import *
from decimal import Decimal

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    surname = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200,null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def bonusCount(self):
        # Обчислюємо бонуси на основі суми замовлення (5%)
        bonus_amount = self.get_cart_total * Decimal('0.05')
        if bonus_amount > 0:
            if not self.customer.bonus:
                self.customer.bonus = bonus_amount
            else:
                self.customer.bonus += bonus_amount
            self.customer.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.complete:
            self.bonusCount()

class OrderItem(models.Model):
    product = models.ForeignKey(FurnitureProduct, on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'OrderID    : {self.order_id} - {self.product.name}'

    @property
    def get_total(self):
        if self.product.discount_price:
            total = self.product.discount_price * self.quantity
        else:
            total = self.product.price * self.quantity
        return total

class ShippingAddres(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL ,null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200,null=False)
    city = models.CharField(max_length=200,null=False)
    state = models.CharField(max_length=200,null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
