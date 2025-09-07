from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from cart.models import UserActionLog
from cart.models import Order


User = get_user_model()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Логін будь-якого користувача (не тільки staff)
    UserActionLog.objects.create(
        user=user,
        action_type="login",
        description=f"Користувач {user.username} увійшов у систему"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # Логаут будь-якого користувача
    UserActionLog.objects.create(
        user=user,
        action_type="logout",
        description=f"Користувач {user.username} вийшов із системи"
    )


@receiver(post_save, sender=Order)
def log_order_created(sender, instance, created, **kwargs):
    if created:
        creator = getattr(instance, "created_by", None)  # якщо у моделі є поле created_by
        if creator:
            description = f"Користувач {creator.username} створив замовлення #{instance.id}"
            user = creator
        else:
            description = f"Створено замовлення #{instance.id}"
            user = None  # якщо створює система або гостьовий

        UserActionLog.objects.create(
            user=user,
            action_type="order_created",
            description=description
        )
