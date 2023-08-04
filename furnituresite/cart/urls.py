from django.urls import path,include
from .views import *


urlpatterns = [
    path('',cart,name='cart'),
    path('checkout/',checkout,name='checkout'),
]