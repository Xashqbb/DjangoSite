from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.shortcuts import render,redirect
from cart.models import *
from .models import *
from utils import cookieCart,cartData
from forms import *
def home_page(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = FurnitureProduct.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request,'main/main.html',context)

# signup page
from django.contrib.auth.hashers import make_password

# ...

def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if form.is_valid() and customer_form.is_valid():
            # Создайте или получите пользователя по email
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            # Перед сохранением пароля хешируйте его с помощью make_password
            hashed_password = make_password(password)
            user, created = User.objects.get_or_create(email=email, defaults={'password': hashed_password})

            # Создайте объект Customer и свяжите его с пользователем
            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            return redirect('login')
    else:
        form = SignupForm()
        customer_form = CustomerForm()
    return render(request, 'main/signup.html', {'form': form, 'customer_form': customer_form})


# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    pass
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

# logout page
def user_logout(request):
    logout(request)
    return redirect('login')

