from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat, name='chat'),  # チャットエンドポイント
    path('review/<str:place_id>/', views.review, name='review'),

]
