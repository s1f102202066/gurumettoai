from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login
from .models import LikedRestaurant
from django.contrib.auth.decorators import login_required




# Create your views here.

def home(request):
    return render(request, 'authtest/home.html', {})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # 新規ユーザーを保存
            login(request, user)  # 登録後に自動的にログイン
            return redirect('/')  # ホームページにリダイレクト
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


#いいね保存関数＝＝＝＝
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LikedRestaurant

@login_required
def like_restaurant(request):
    if request.method == 'POST':
        restaurant_name = request.POST.get('restaurant_name')
        restaurant_address = request.POST.get('restaurant_address')

        # 重複チェック: 同じユーザーとレストランで既存のいいねを防ぐ
        if not LikedRestaurant.objects.filter(user=request.user, restaurant_name=restaurant_name).exists():
            LikedRestaurant.objects.create(
                user=request.user,
                restaurant_name=restaurant_name,
                restaurant_address=restaurant_address
            )
        
        return redirect('mypage')  # いいね後にマイページに遷移

@login_required
def mypage(request):
    liked_restaurants = LikedRestaurant.objects.filter(user=request.user).order_by('-liked_at')
    return render(request, 'mypage.html', {'liked_restaurants': liked_restaurants})
