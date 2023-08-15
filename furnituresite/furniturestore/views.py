from django.shortcuts import render,redirect
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


