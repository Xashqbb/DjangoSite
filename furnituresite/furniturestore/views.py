from django.shortcuts import render, redirect, get_object_or_404
from cart.models import *
from .models import *
from utils import cookieCart,cartData

def furniture_store(request, category_slug=None):
    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    if category_slug:
        if category_slug == 'all':
            products = FurnitureProduct.objects.all()
        else:
            products = FurnitureProduct.objects.filter(category__slug=category_slug)
    else:
        products = FurnitureProduct.objects.all()

    context = {
        'products': products,
        'cartItems': cartItems,
        'categories': categories,
        'current_category_slug': category_slug,
    }
    return render(request, 'furniturestore/furniture_store.html', context)


def product_detail(request, product_slug):
    data = cartData(request)
    cartItems = data['cartItems']
    product = get_object_or_404(FurnitureProduct, slug=product_slug)
    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'furniturestore/product_detail.html', context)
