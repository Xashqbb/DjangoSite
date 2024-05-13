from django import forms
from django.contrib.auth.forms import UserCreationForm
from custom_user.models import User
from cart.models import *

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    # username = forms.CharField(widget=forms.TextInput(attrs={
    #     'placeholder': 'I.IVANOV',
    #     'class': '.form input',
    # }))
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
