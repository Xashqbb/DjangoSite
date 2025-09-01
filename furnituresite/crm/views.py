from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import Customer, Order, OrderItem, Interaction, UserActionLog




def orders_view(request):
    status = request.GET.get("status")
    customer = request.GET.get("customer")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    orders = Order.objects.all()

    if status == "pending":
        orders = orders.filter(complete=False)
    elif status == "completed":
        orders = orders.filter(complete=True)

    if customer:
        orders = orders.filter(
            Q(customer__name__icontains=customer) |
            Q(customer__surname__icontains=customer) |
            Q(customer__email__icontains=customer)
        )

    if date_from:
        orders = orders.filter(date_ordered__gte=date_from)
    if date_to:
        orders = orders.filter(date_ordered__lte=date_to)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = [
            {
                "id": o.id,
                "customer": str(o.customer),
                "date": o.date_ordered.strftime("%Y-%m-%d %H:%M"),
                "status": "✅ Завершено" if o.complete else "⏳ В обробці"
            }
            for o in orders
        ]
        return JsonResponse({"orders": data})

    return render(request, "admin/crm_orders.html", {"orders": orders})


@login_required
def customers_view(request):
    customers = Customer.objects.all()
    return render(request, "admin/crm_customers.html", {"customers": customers})


@login_required
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = Order.objects.filter(customer=customer).order_by("-date_ordered")
    interactions = customer.interactions.all().order_by("-created_at")
    return render(request, "admin/crm_customer_detail.html", {
        "customer": customer,
        "orders": orders,
        "interactions": interactions,
    })


@login_required
def logs_view(request):
    logs = UserActionLog.objects.select_related("user").order_by("-timestamp")[:200]
    return render(request, "admin/crm_logs.html", {"logs": logs})


@login_required
def crm_logs(request):
    logs = UserActionLog.objects.select_related("user").order_by("-timestamp")
    return render(request, "admin/crm_logs.html", {"logs": logs})


@login_required
def crm_analytics_view(request):
    from django.db.models import Count, Sum, F
    from django.db.models.functions import TruncMonth
    from cart.models import OrderItem

    # Загальна статистика
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(complete=True).count()

    # Кількість товарів (штуки)
    total_products = OrderItem.objects.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    # Сума товарів (кількість * ціна)
    total_products_sum = OrderItem.objects.aggregate(
        total=Sum(F("quantity") * F("product__price"))
    )["total"] or 0

    # Замовлення по місяцях
    monthly_orders = (
        Order.objects.annotate(month=TruncMonth("date_ordered"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    months = [o["month"].strftime("%Y-%m") for o in monthly_orders]
    counts = [o["count"] for o in monthly_orders]

    # Топ-5 клієнтів
    top_customers = (
        OrderItem.objects.filter(order__complete=True)
        .values("order__customer__name", "order__customer__email")
        .annotate(total_spent=Sum(F("quantity") * F("product__price")))
        .order_by("-total_spent")[:5]
    )

    # Топ-5 товарів
    top_products = (
        OrderItem.objects.values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:5]
    )

    return render(request, "admin/crm_analytics.html", {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "total_products": total_products,
        "total_products_sum": total_products_sum,
        "months": months,
        "counts": counts,
        "top_customers": top_customers,
        "top_products": top_products,
    })

