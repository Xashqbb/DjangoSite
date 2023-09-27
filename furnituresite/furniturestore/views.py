from django.shortcuts import render, redirect, get_object_or_404
from cart.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

    paginator = Paginator(products, 10)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    page_number = products.number
    num_pages = paginator.num_pages
    page_range = range(max(1, page_number - 2), min(num_pages, page_number + 2) + 1)

    context = {
        'products': products,
        'cartItems': cartItems,
        'categories': categories,
        'current_category_slug': category_slug,
        'page_range': page_range,
        'page_number': page_number,
        'num_pages': num_pages,
    }
    return render(request, 'furniturestore/furniture_store.html', context)



def product_detail(request, product_slug):
    data = cartData(request)
    cartItems = data['cartItems']
    product = get_object_or_404(FurnitureProduct, slug=product_slug)
    context = {'product': product, 'cartItems': cartItems,}
    return render(request, 'furniturestore/product_detail.html', context)
