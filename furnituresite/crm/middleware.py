from cart.models import UserActionLog


class AdminActionLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                action_type = "update"
                if request.method == "POST":
                    action_type = "create"
                elif request.method == "DELETE":
                    action_type = "delete"

                UserActionLog.objects.create(
                    user=request.user,
                    action_type=action_type,
                    description=f"Адмін {request.user.username} виконав {request.method} на {request.path}",
                )
        return None
