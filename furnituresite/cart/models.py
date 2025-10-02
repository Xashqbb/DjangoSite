from django.db import models
from django.conf import settings
from furniturestore.models import *
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model


def get_system_user():
    User = get_user_model()
    username_field = User.USERNAME_FIELD

    try:
        if username_field == 'email':
            user_credentials = {username_field: "system@example.com"}
        else:
            user_credentials = {username_field: "system"}

        user, created = User.objects.get_or_create(
            **user_credentials,
            defaults={
                "is_staff": True,
                "is_active": True,
            }
        )
        return user
    except Exception as e:
        print(f"Error creating system user: {e}")
        return None

def get_system_user_id():
    """
    Повертає ID системного користувача для використання у міграціях.
    """
    return get_system_user().id


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    surname = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}" if self.surname else self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новий"),
        ("processing", "В обробці"),
        ("shipped", "Відправлений"),
        ("delivered", "Доставлений"),
        ("cancelled", "Скасований"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    def __str__(self):
        return f"Order {self.id} ({self.get_status_display()})"

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
    product = models.ForeignKey(FurnitureProduct, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.order_id} - {self.product.name}'

    @property
    def get_total(self):
        if self.product.discount_price:
            total = self.product.discount_price * self.quantity
        else:
            total = self.product.price * self.quantity
        return total


class ShippingAddres(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class UserActionLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Створення"),
        ("update", "Оновлення"),
        ("delete", "Видалення"),
        ("login", "Вхід"),
        ("logout", "Вихід"),
        ("order_created", "Створення замовлення"),
        ("order_status_change", "Зміна статусу замовлення"),
        ("bulk_order_action", "Масова дія з замовленнями"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    username = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        user_display = self.user.username if hasattr(self.user, 'username') else "Система"
        return f"[{self.timestamp}] {user_display} - {self.get_action_type_display()}"


class Interaction(models.Model):
    INTERACTION_TYPES = [
        ("call", "Дзвінок"),
        ("email", "Електронний лист"),
        ("meeting", "Зустріч"),
        ("note", "Замітка"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_interaction_type_display()} з {self.customer} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

