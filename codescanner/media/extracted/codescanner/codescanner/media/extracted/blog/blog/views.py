from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    if User.is_authenticated:
        return render(request, 'blog/home.html')
    else:
        return redirect(request, 'users/login.html')

