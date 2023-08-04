from django.urls import path,include
from .views import *


urlpatterns = [
    path('',furniture_store,name='furniture_store'),
]