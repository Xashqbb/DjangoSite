from django.db import models
from django.conf import settings
from furniturestore.models import FurnitureProduct

class GeneratedDescription(models.Model):
    STATUS_CHOICES = [
        ("draft", "Чернетка"),
        ("published", "Опубліковано"),
        ("failed", "Помилка"),
    ]

    SOURCE_CHOICES = [
        ("OpenAI", "OpenAI"),
        ("OpenRouter", "OpenRouter"),
        ("Fallback", "Заглушка"),
        ("None", "Невідомо"),
    ]

    product = models.ForeignKey(FurnitureProduct, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="gen_images/", blank=True, null=True)
    detected_category = models.CharField(max_length=255, blank=True)
    features_json = models.JSONField(default=dict, blank=True)
    seo_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="None")  # 🔹 нове поле
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} ({self.get_status_display()})"
