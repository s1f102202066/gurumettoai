from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),
    path("app01/", include("authtest.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
]

