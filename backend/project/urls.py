from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.urls'))
] + static(settings.MEDIA_BASE_URL, document_root=settings.MEDIA_ROOT)