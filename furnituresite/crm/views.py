# crm/views.py
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from cart.models import Customer, Order, OrderItem, Interaction, UserActionLog
from furniturestore.models import FurnitureProduct as Product

# --- Універсальна функція логування ---
def log_user_action(request, action_type, description):
    user = None
    username = "Система"
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        username = request.user.get_username()
    try:
        log_entry = UserActionLog.objects.create(
            user=user,
            username=username,
            action_type=action_type,
            description=description
        )
    except Exception as e:
        print(f"!!! ERROR during UserActionLog.objects.create: {e}")

# функція для відображення фільтрації та сортування замовлень
def orders_view(request):
    # --- Сортування ---
    sort_order = request.GET.get('sort', '-date_ordered')
    if sort_order not in ['date_ordered', '-date_ordered']:
        sort_order = '-date_ordered'
    # --- Фільтрація ---
    status = request.GET.get("status")
    customer = request.GET.get("customer")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    orders = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').all()

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
        orders = orders.filter(date_ordered__date__gte=date_from)
    if date_to:
        orders = orders.filter(date_ordered__date__lte=date_to)

    orders = orders.order_by(sort_order)

    for order in orders:
        order.total_cost = order.orderitem_set.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0
        order.items_list = list(order.orderitem_set.all())

    context = {
        "orders": orders,
        "current_sort": sort_order,
    }

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

    return render(request, "admin/crm_orders.html", context)


@login_required
def update_order_status(request):
    if request.method == "POST":
        try:

            data = json.loads(request.body)
            order_id = data.get("order_id")
            status = data.get("status")

            order = Order.objects.get(id=order_id)

            if status == "completed":
                order.complete = True
                status_display = "Завершено"
            elif status == "pending":
                order.complete = False
                status_display = "В обробці"
            else:
                return JsonResponse({"success": False, "error": "Невідомий статус"})

            order.save()

            log_user_action(
                request=request,
                action_type="update",
                description=f"Зміна статусу замовлення #{order.id} на {status_display}"
            )

            return JsonResponse({"success": True, "status_display": status_display})
        except Exception as e:
            # Також додамо вивід помилки в консоль
            print(f"ERROR in update_order_status: {e}")
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Неправильний метод"})


@csrf_exempt
@require_POST
@login_required
def bulk_order_action(request):
    """Масові дії з замовленнями"""
    try:
        data = json.loads(request.body.decode("utf-8"))
        order_ids = data.get("order_ids", [])
        action = data.get("action")

        if not order_ids or not action:
            return JsonResponse({"success": False, "error": "Невірні дані"})

        orders = Order.objects.filter(id__in=order_ids)

        if action == "mark_completed":
            orders.update(complete=True)
            action_desc = "Позначено як завершені"
        elif action == "mark_pending":
            orders.update(complete=False)
            action_desc = "Позначено як в обробці"
        else:
            return JsonResponse({"success": False, "error": "Невірна дія"})

        log_user_action(
            request,
            "bulk_order_action",
            f"{action_desc}: замовлення {', '.join(map(str, order_ids))}"
        )

        return JsonResponse({
            "success": True,
            "message": f"{action_desc}: {len(order_ids)} замовлень"
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


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
    logs = UserActionLog.objects.select_related("user").all()

    user_query = request.GET.get("user")
    action_param = request.GET.get("action_type")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if user_query:
        logs = logs.filter(user__username__icontains=user_query)

    action_code = None
    if action_param:
        choices_dict = dict(UserActionLog.ACTION_CHOICES)
        reverse_dict = {label: code for code, label in choices_dict.items()}

        if action_param in choices_dict:
            action_code = action_param
        elif action_param in reverse_dict:
            action_code = reverse_dict[action_param]

    if action_code:
        logs = logs.filter(action_type=action_code)

    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)

    sort_order = request.GET.get("sort", "-timestamp")
    if sort_order not in ["timestamp", "-timestamp", "user__username", "-user__username", "action_type", "-action_type"]:
        sort_order = "-timestamp"
    logs = logs.order_by(sort_order)

    return render(request, "admin/crm_logs.html", {
        "logs": logs[:200],
        "current_sort": sort_order,
        "current_user": user_query or "",
        "current_action": action_code or "",
        "date_from": date_from or "",
        "date_to": date_to or "",
        "action_choices": UserActionLog.ACTION_CHOICES,
    })


@login_required
def crm_analytics_view(request):
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(complete=True).count()

    total_products = OrderItem.objects.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    total_products_sum = OrderItem.objects.aggregate(
        total=Sum(F("quantity") * F("product__price"))
    )["total"] or 0

    monthly_orders = (
        Order.objects.annotate(month=TruncMonth("date_ordered"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    months = [o["month"].strftime("%Y-%m") for o in monthly_orders]
    counts = [o["count"] for o in monthly_orders]

    top_customers = (
        OrderItem.objects.filter(order__complete=True)
        .values("order__customer__name", "order__customer__email")
        .annotate(total_spent=Sum(F("quantity") * F("product__price")))
        .order_by("-total_spent")[:5]
    )

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


@login_required
def create_order_view(request):
    customers = Customer.objects.all()
    products = Product.objects.all()
    return render(request, "admin/crm_order_create.html", {
        "customers": customers,
        "products": products,
    })


@csrf_exempt
@require_POST
@login_required
def create_order_ajax(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        customer_id = data.get("customer")
        items = data.get("items", [])

        if not customer_id or not items:
            return JsonResponse({"success": False, "error": "Невірні дані"})

        customer = Customer.objects.get(id=customer_id)

        order = Order(customer=customer, complete=False, date_ordered=timezone.now())
        order._created_by = request.user
        order.save()

        for item in items:
            product_id = item.get("product")
            quantity = int(item.get("quantity", 1))

            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        log_user_action(
            request,
            "order_created",
            f"Користувач створив замовлення #{order.id}"
        )

        return JsonResponse({"success": True, "order_id": order.id})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
