from django.urls import path,include
from .views import *


urlpatterns = [
    path('',furniture_store,name='furniture_store'),
    path('<slug:product_slug>/',product_detail,name='product_detail'),
]
