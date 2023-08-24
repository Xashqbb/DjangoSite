from django.contrib import admin
from .models import *
from cart.models import *

admin.site.register(FurnitureProduct)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddres)
admin.site.register(Category)
admin.site.register(AdditionalImage)

