from django.urls import path,include
from .views import *


urlpatterns=[
    path('',home_page,name='home'),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
]