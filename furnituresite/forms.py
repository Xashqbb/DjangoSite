from django import forms
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect

from custom_user.models import User
from cart.models import *

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'sobaka@gmail.com',
        'class': '.form input',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '@!@#sadd123',
        'class': '.form input',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'repeat password',
        'class': '.form input',
    }))


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'surname', 'email']

    name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'IVANOV',
        'class': '.form input',
    }))
    surname = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'IVANOV',
        'class': '.form input',
    }))

    def save(self, commit=True):
        customer = super(CustomerForm, self).save(commit=False)
        customer.email = self.cleaned_data['email']

        if commit:
            customer.save()

        return customer

class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your Email',
        'class': '.form input',}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your Password',
        'class': '.form input', }))

class PriceFilterForm(forms.Form):
    min_price = forms.DecimalField(label='Min price', required=False)
    max_price = forms.DecimalField(label='Max price', required=False)


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your Email', 'class': '.form input'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with the specified email address.")
        return email

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': '.form input'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': '.form input'}),
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in password):
            raise forms.ValidationError("Password must contain at least one letter.")
        return password

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def post(self, request, *args, **kwargs):
        return redirect(self.success_url)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, "Your password has been successfully updated.")
        return redirect('home')




