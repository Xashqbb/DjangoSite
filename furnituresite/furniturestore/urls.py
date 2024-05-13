from django.urls import path, include
from .views import *

urlpatterns = [
    path('', furniture_store, name='furniture_store'),
    path('<slug:product_slug>/', product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', furniture_store, name='furniture_store_category'),
    path('cd', furniture_store, name='furniture_store_all'),
    path('<slug:product_slug>/3d/', ThreeD_view, name='3d_view'),
]
