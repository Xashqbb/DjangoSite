from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import *
from furniturestore.models import *
from utils import cartData, guestOrder
import datetime, json


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart/checkout.html', context)


def updateItem(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']

        customer = request.user.customer
        product = FurnitureProduct.objects.get(id=productId)

        # Забезпечуємо єдине активне замовлення
        orders = Order.objects.filter(customer=customer, complete=False)
        if orders.exists():
            order = orders.latest('id')
            orders.exclude(id=order.id).update(complete=True)
        else:
            order = Order.objects.create(customer=customer, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        return JsonResponse('Item was updated', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer

        # Забезпечуємо єдине активне замовлення
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

    return JsonResponse('Payment complete', safe=False)
