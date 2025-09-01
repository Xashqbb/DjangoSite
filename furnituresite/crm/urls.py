from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.orders_view, name="crm_orders"),
    path("customers/", views.customers_view, name="crm_customers"),
    path("customers/<int:customer_id>/", views.customer_detail_view, name="crm_customer_detail"),
    path("logs/", views.logs_view, name="crm_logs"),
    path("analytics/", views.crm_analytics_view, name="crm_analytics"),
]
