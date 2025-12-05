from django.urls import path
from .views import *


app_name = "contentgen"

urlpatterns = [
    path("upload/", upload_view, name="upload"),
    path("editor/<int:pk>/", editor_view, name="editor"),
    path("list/", list_view, name="list"),
]
