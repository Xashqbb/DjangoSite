from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from cart.models import UserActionLog


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    if user.is_staff:
        UserActionLog.objects.create(
            user=user,
            action_type="login",
            description=f"Адмін {user.username} увійшов у систему"
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user.is_staff:
        UserActionLog.objects.create(
            user=user,
            action_type="logout",
            description=f"Адмін {user.username} вийшов із системи"
        )
