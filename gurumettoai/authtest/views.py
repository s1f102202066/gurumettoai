from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login




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