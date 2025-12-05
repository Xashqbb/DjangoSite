from django.contrib import admin
from .models import GeneratedDescription

@admin.register(GeneratedDescription)
class GeneratedDescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "status", "source", "created_by", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("product__name", "seo_text")
