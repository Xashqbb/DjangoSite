from django.urls import path
from django.contrib.auth import views as auth_views

from forms import CustomPasswordResetCompleteView
from .views import home_page, user_login, user_signup, user_logout, cabinet, CustomPasswordResetView, \
    CustomPasswordResetConfirmView

urlpatterns = [
    path('', home_page, name='home'),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
    path('cabinet/', cabinet, name='cabinet'),

    # Password reset paths
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'),
         name='password_reset_complete'),
]
