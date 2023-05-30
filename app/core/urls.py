from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from core.settings import MEDIA_ROOT, MEDIA_URL


urlpatterns = [
    path('', include('contracts.urls')),
    path('admin/', admin.site.urls),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)