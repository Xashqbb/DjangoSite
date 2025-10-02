from django.urls import path
from .views import upload_view, editor_view

app_name = "contentgen"

urlpatterns = [
    path("upload/", upload_view, name="upload"),
    path("editor/<int:pk>/", editor_view, name="editor"),
]
