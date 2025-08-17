from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from cart.models import Customer, Order, OrderItem, ShippingAddres
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from decimal import Decimal
import json


class CRMAdminSite(admin.AdminSite):
    site_header = "CRM Панель"
    site_title = "CRM Управління"
    index_title = "Дашборд CRM"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard), name="crm-dashboard"),
        ]
        return custom_urls + urls

    def dashboard(self, request):
        # 📊 Основна статистика
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        completed_orders = Order.objects.filter(complete=True).count()
        total_revenue = OrderItem.objects.aggregate(
            total=Sum('quantity'))['total'] or 0
        total_bonus = Customer.objects.aggregate(
            bonus=Sum('bonus'))['bonus'] or Decimal('0.00')

        # 📊 Замовлення по місяцях
        orders_by_month = (
            Order.objects
            .annotate(month=TruncMonth('date_ordered'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        months = [o['month'].strftime("%Y-%m") for o in orders_by_month]
        counts = [o['count'] for o in orders_by_month]

        context = dict(
            self.each_context(request),
            total_customers=total_customers,
            total_orders=total_orders,
            completed_orders=completed_orders,
            total_revenue=total_revenue,
            total_bonus=total_bonus,
            months=json.dumps(months),
            counts=json.dumps(counts),
        )
        return TemplateResponse(request, "admin/crm_dashboard.html", context)


# Створюємо окремий CRM admin site
crm_admin_site = CRMAdminSite(name='crm_admin')

# ✅ Реєструємо тільки CRM-моделі
crm_admin_site.register(Customer)
crm_admin_site.register(Order)
crm_admin_site.register(OrderItem)
crm_admin_site.register(ShippingAddres)
