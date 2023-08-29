from django.contrib import admin
from .models import *
from cart.models import *

class FurnitureProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'photo','article','model_3d','color']
    list_display_links = ['id', 'name']
    search_fields = ['name','article']
    prepopulated_fields =   {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    prepopulated_fields =   {'slug': ('name',)}



admin.site.register(FurnitureProduct)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddres)
admin.site.register(Category)
admin.site.register(AdditionalImage)

