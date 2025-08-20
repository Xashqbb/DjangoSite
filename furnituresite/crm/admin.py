from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.http import JsonResponse
from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from decimal import Decimal
import json

from cart.models import Customer, Order, OrderItem, ShippingAddres
from furniturestore.models import FurnitureProduct


class CRMAdminSite(admin.AdminSite):
    site_header = "CRM Панель"
    site_title = "CRM Управління"
    index_title = "CRM Дашборд"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.orders_view), name="crm-orders"),
            path('analytics/', self.admin_view(self.analytics_view), name="crm-analytics"),
            path('create-order/', self.admin_view(self.create_order_view), name="crm-create-order"),
            path('create-order-ajax/', self.admin_view(self.create_order_ajax), name="crm-create-order-ajax"),
            path('filter-orders/', self.admin_view(self.filter_orders), name="crm-filter-orders"),
        ]
        return custom_urls + urls

    # 📌 View: список замовлень
    def orders_view(self, request):
        orders = Order.objects.all().select_related("customer").order_by("-date_ordered")[:50]
        context = dict(
            self.each_context(request),
            orders=orders,
        )
        return TemplateResponse(request, "admin/crm_orders.html", context)

    # 📌 AJAX-фільтрація замовлень
    def filter_orders(self, request):
        status = request.GET.get("status")
        customer_name = request.GET.get("customer")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        orders = Order.objects.all().select_related("customer")

        if status:
            orders = orders.filter(status=status)
        if customer_name:
            orders = orders.filter(
                models.Q(customer__name__icontains=customer_name) |
                models.Q(customer__surname__icontains=customer_name) |
                models.Q(customer__email__icontains=customer_name)
            )
        if date_from:
            orders = orders.filter(date_ordered__gte=date_from)
        if date_to:
            orders = orders.filter(date_ordered__lte=date_to)

        data = []
        for order in orders:
            data.append({
                "id": order.id,
                "customer": str(order.customer),
                "date": order.date_ordered.strftime("%Y-%m-%d %H:%M"),
                "status": order.get_status_display(),
            })
        return JsonResponse({"orders": data})

    # 📌 View: сторінка створення замовлення
    def create_order_view(self, request):
        customers = Customer.objects.all()
        products = FurnitureProduct.objects.all()

        context = dict(
            self.each_context(request),
            customers=customers,
            products=products,
        )
        return TemplateResponse(request, "admin/crm_order_create.html", context)

    # 📌 AJAX: створення замовлення
    def create_order_ajax(self, request):
        if request.method == "POST":
            data = json.loads(request.body.decode("utf-8"))
            customer_id = data.get("customer")
            items = data.get("items", [])

            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({"success": False, "error": "Клієнт не знайдений"})

            order = Order.objects.create(customer=customer, status="new", complete=False)

            for item in items:
                product_id = item.get("product")
                quantity = int(item.get("quantity", 1))
                try:
                    product = FurnitureProduct.objects.get(id=product_id)
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)
                except FurnitureProduct.DoesNotExist:
                    continue

            return JsonResponse({"success": True, "order_id": order.id})

        return JsonResponse({"success": False, "error": "Неправильний метод"})

    # 📌 View: аналітика
    def analytics_view(self, request):
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        completed_orders = Order.objects.filter(complete=True).count()
        total_revenue = OrderItem.objects.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        total_bonus = Customer.objects.aggregate(
            bonus=Sum('bonus')
        )['bonus'] or Decimal('0.00')

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
        return TemplateResponse(request, "admin/crm_analytics.html", context)


# ✅ Реєструємо окремий CRM admin site
crm_admin_site = CRMAdminSite(name='crm_admin')
crm_admin_site.register(Customer)
crm_admin_site.register(Order)
crm_admin_site.register(OrderItem)
crm_admin_site.register(ShippingAddres)
