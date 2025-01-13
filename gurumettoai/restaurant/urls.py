from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat, name='chat'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),

]