from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.contrib.messages import get_messages
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
    return render(request, 'main/main.html', context)


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
    invalid_login = False
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
                invalid_login = True
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form, 'invalid_login': invalid_login})

# logout page
def user_logout(request):
    logout(request)
    return redirect('login')

def cabinet(request):
    data = cartData(request)
    cartItems = data['cartItems']
    user = request.user
    user_info = Customer.objects.get(user=user)
    if user_info.bonus is None:
        user_info.bonus = 0
        user_info.save()
    bonus_balance = user_info.bonus
    products = FurnitureProduct.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'user': user_info, 'bonus_balance': bonus_balance}
    return render(request, 'main/cabinet.html', context)

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'main/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'main/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'main/password_reset_complete.html'
    success_url = reverse_lazy('home')