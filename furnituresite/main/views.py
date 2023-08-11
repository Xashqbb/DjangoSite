from django.shortcuts import render
from cart.models import *
from .models import *

def home_page(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    products = FurnitureProduct.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request,'main/main.html',context)
