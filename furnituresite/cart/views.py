from django.shortcuts import render,redirect
from django.template.loader import render_to_string

from .models import *
from furniturestore.models import *
from django.http import JsonResponse
import datetime
import json
from utils import cookieCart,cartData,guestOrder
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'cart/cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(request,'cart/checkout.html',context)

def updateItem(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']

        customer = request.user.customer
        product = FurnitureProduct.objects.get(id=productId)
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
        order,created = Order.objects.get_or_create(customer=customer, complete=False)

        ShippingAddres.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    else:
        customer,order = guestOrder(request,data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    send_order_confirmation_email(customer.email, order)

    return JsonResponse('Payment complete', safe=False)

def send_order_confirmation_email(email, order):
    sender_email = "mrhoriizonn@gmail.com"
    app_password = "bkcpeykqklresikw"

    subject = "Confirmation of your order"
    recipient = email

    # Підготовка повідомлення
    message = render_to_string('cart/order_confirmation.html', {'order': order})

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient, text)
    server.quit()
