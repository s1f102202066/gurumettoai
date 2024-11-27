from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat, name='chat'),
    path('suggest-restaurant-with-reviews/', views.suggest_restaurant_with_reviews, name='suggest_restaurant_with_reviews'),
]