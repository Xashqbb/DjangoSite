import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from utils import *
from cart.gmail_service import send_gmail


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'cart/store.html', context)


def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart/cart.html', context)


def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        # гарантуємо одне активне замовлення
        orders = Order.objects.filter(customer=customer, complete=False)
        if orders.exists():
            order = orders.latest('id')
            orders.exclude(id=order.id).update(complete=True)
        else:
            order = Order.objects.create(customer=customer, complete=False)

        ShippingAddres.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
        order.save()

        # ✅ Відправка email-підтвердження
        subject = f"Order Confirmation #{order.id}"
        body = render_to_string("cart/order_confirmation.html", {"order": order})

        send_gmail(
            to=data['form']['email'] if not request.user.is_authenticated else customer.user.email,
            subject=subject,
            body=body
        )

    return JsonResponse('Payment complete', safe=False)
