from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages



# Create your views here.

def home(request):
    return render(request, 'authtest/home.html', {})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'アカウントが作成されました！ログインしてください。')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'authtest/register.html', {'form': form})