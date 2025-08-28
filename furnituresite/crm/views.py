from django.shortcuts import render
from django.http import JsonResponse
from cart.models import Order
from django.core.serializers import serialize
from django.db.models import Q

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

    # Якщо це AJAX-запит → відправляємо JSON
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
