from django.shortcuts import render,redirect


def furniture_store(request):
    return render(request,'furniturestore/furniture_store.html')

