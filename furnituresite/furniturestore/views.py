from django.core.exceptions import ValidationError
from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from cart.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from utils import cookieCart,cartData
from forms import *

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

    price_filter_form = PriceFilterForm(request.GET)
    if price_filter_form.is_valid():
        min_price = price_filter_form.cleaned_data.get('min_price')
        max_price = price_filter_form.cleaned_data.get('max_price')

        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError('Invalid price range')
        else:
            if min_price is not None:
                products = products.filter(price__gte=min_price)
            if max_price is not None:
                products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 6)
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

    min_price = FurnitureProduct.objects.aggregate(min_price=Min('price'))['min_price']
    max_price = FurnitureProduct.objects.aggregate(max_price=Max('price'))['max_price']

    context = {
        'products': products,
        'cartItems': cartItems,
        'categories': categories,
        'current_category_slug': category_slug,
        'page_range': page_range,
        'page_number': page_number,
        'num_pages': num_pages,
        'price_filter_form': price_filter_form,
        'min_price': min_price,
        'max_price': max_price
    }
    return render(request, 'furniturestore/furniture_store.html', context)






def product_detail(request, product_slug):
    data = cartData(request)
    cartItems = data['cartItems']
    product = get_object_or_404(FurnitureProduct, slug=product_slug)
    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'furniturestore/product_detail.html', context)


def ThreeD_view(request, product_slug):
    data = cartData(request)
    cartItems = data['cartItems']
    product = get_object_or_404(FurnitureProduct, slug=product_slug)
    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'furniturestore/3d_view.html', context)