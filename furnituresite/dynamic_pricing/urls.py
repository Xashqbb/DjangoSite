from django.urls import path
from . import views

urlpatterns = [
    path('analyze/<int:product_id>/', views.analyze_price_api, name='analyze_price'),
]