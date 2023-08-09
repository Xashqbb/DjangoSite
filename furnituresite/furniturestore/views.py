from django.shortcuts import render,redirect
from .models import *

def furniture_store(request):
    products = FurnitureProduct.objects.all()
    context = {'products':products}
    return render(request,'furniturestore/furniture_store.html',context)


