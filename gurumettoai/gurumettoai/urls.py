from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),
    path("app01/", include("authtest.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),  # favicon.icoへのリダイレクト

]

