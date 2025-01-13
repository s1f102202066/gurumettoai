from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('like/', views.like_restaurant, name='like_restaurant'),
    path('mypage/', views.mypage, name='mypage'),
]

