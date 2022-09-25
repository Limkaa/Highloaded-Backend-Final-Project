from django.urls import path, include

urlpatterns = [
    path('account/', include('apps.accounts.urls')),
    path('courses/', include('apps.courses.urls')),
]