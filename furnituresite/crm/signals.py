# crm/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from cart.models import UserActionLog

User = get_user_model()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    UserActionLog.objects.create(
        user=user,
        action_type="login",
        description=f"Користувач {user.get_username()} увійшов у систему"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    UserActionLog.objects.create(
        user=user,
        action_type="logout",
        description=f"Користувач {user.get_username()} вийшов із системи"
    )

