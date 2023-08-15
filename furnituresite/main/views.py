from django.shortcuts import render
from cart.models import *
from .models import *
from utils import cookieCart,cartData

def home_page(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = FurnitureProduct.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request,'main/main.html',context)
