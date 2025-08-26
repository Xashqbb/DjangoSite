from django.urls import path,include
from .views import *



urlpatterns = [
    path('',cart,name='cart'),
    path('checkout/',checkout,name='checkout'),
    path('update_item/',updateItem,name='update_item'),
    path('checkout/processOrder/',processOrder,name='process_order')

]