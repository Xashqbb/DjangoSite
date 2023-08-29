from django.shortcuts import render, redirect, get_object_or_404
from cart.models import *
from .models import *
from utils import cookieCart,cartData

def furniture_store(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = FurnitureProduct.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request,'furniturestore/furniture_store.html',context)


def product_detail(request, product_slug):
    data = cartData(request)
    cartItems = data['cartItems']
    product = get_object_or_404(FurnitureProduct, slug=product_slug)
    context = {'product': product,'cartItems':cartItems}
    return render(request, 'furniturestore/product_detail.html', context)