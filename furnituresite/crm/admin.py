from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from cart.models import Customer, Order, OrderItem, ShippingAddres
from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from decimal import Decimal
import json


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ["id", "customer", "date_ordered", "complete"]
    list_filter = ["complete", "date_ordered"]


class CRMAdminSite(admin.AdminSite):
    site_header = "CRM Панель"
    site_title = "CRM Управління"
    index_title = "CRM Дашборд"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.orders_view), name="crm-orders"),
            path('analytics/', self.admin_view(self.analytics_view), name="crm-analytics"),
        ]
        return custom_urls + urls

    def orders_view(self, request):
        # 🔍 Фільтри
        status = request.GET.get("status")
        customer_name = request.GET.get("customer")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        orders = Order.objects.all().select_related("customer")

        if status == "completed":
            orders = orders.filter(complete=True)
        elif status == "pending":
            orders = orders.filter(complete=False)

        if customer_name:
            orders = orders.filter(
                models.Q(customer__name__icontains=customer_name) |
                models.Q(customer__surname__icontains=customer_name)
            )

        if date_from:
            orders = orders.filter(date_ordered__gte=date_from)
        if date_to:
            orders = orders.filter(date_ordered__lte=date_to)

        context = dict(
            self.each_context(request),
            orders=orders.order_by("-date_ordered")[:50],
        )
        return TemplateResponse(request, "admin/crm_orders.html", context)

    def analytics_view(self, request):
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

        # 🔝 Топ-5 клієнтів
        top_customers = (
            Order.objects.filter(complete=True)
            .values("customer__name", "customer__surname")
            .annotate(total_spent=Sum("orderitem__quantity"))
            .order_by("-total_spent")[:5]
        )

        # 🔝 Топ-5 товарів
        top_products = (
            OrderItem.objects.filter(order__complete=True)
            .values("product__name")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )

        context = dict(
            self.each_context(request),
            total_customers=total_customers,
            total_orders=total_orders,
            completed_orders=completed_orders,
            total_revenue=total_revenue,
            total_bonus=total_bonus,
            months=json.dumps(months),
            counts=json.dumps(counts),
            top_customers=top_customers,
            top_products=top_products,
        )
        return TemplateResponse(request, "admin/crm_analytics.html", context)


# 👉 Створюємо CRM admin site
crm_admin_site = CRMAdminSite(name='crm_admin')

# ✅ Реєстрація моделей
crm_admin_site.register(Customer)
crm_admin_site.register(Order, OrderAdmin)
crm_admin_site.register(OrderItem)
crm_admin_site.register(ShippingAddres)
