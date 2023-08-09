from django.shortcuts import render,redirect
from .models import *
from furniturestore.models import FurnitureProduct

def cart(request):
    context = {}
    return render(request,'cart/cart.html',context)

def checkout(request):
    context = {}
    return render(request,'cart/checkout.html',context)

