
from django.core.management.base import BaseCommand
from cart.models import UserActionLog

class Command(BaseCommand):
    help = "Оновлює старі значення action_type у UserActionLog відповідно до нових choices"

    def handle(self, *args, **options):
        mapping = {
            "status_change": "order_status_change",  # старе -> нове
        }

        total_updated = 0
        for old_value, new_value in mapping.items():
            updated = UserActionLog.objects.filter(action_type=old_value).update(action_type=new_value)
            total_updated += updated
            if updated:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Оновлено {updated} записів: {old_value} → {new_value}"
                ))

        if total_updated == 0:
            self.stdout.write(self.style.WARNING("ℹ️ Не знайдено записів для оновлення."))
        else:
            self.stdout.write(self.style.SUCCESS(f"🎉 Всього оновлено {total_updated} записів."))
