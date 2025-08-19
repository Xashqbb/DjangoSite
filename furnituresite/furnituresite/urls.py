from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from crm.admin import crm_admin_site


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('main.urls')),
    path('furniturestore/',include('furniturestore.urls')),
    path('cart/',include('cart.urls')),
    path("crm-admin/", crm_admin_site.urls, name="crm_admin"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)