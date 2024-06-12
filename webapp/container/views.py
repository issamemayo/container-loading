from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request,"container/index.html")

def login_view(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user=authenticate(request,username=username, password=password)
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request,"container/login.html",{
                "message":"Invalid Username or Password"
            })
    return render(request,"container/login.html")

def logout_view(request):
    logout(request)
    return render(request, "container/login.html",{
        "message":"Successfully Logged Out"
    })

def signup(request):
    if request.method=="POST":
        username=request.POST["new_username"]
        password=request.POST["password"]
        
        if not username or not password:
            return render(request, 'container/signup.html', {'message': 'Please fill out all fields'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'container/signup.html', {'message': 'Username already taken'})
        
        user = User(username=username, password=make_password(password))
        user.save()

        return render(request,"container/login.html",{
            "message":"Account Created Successfully"
        })  

    return render(request, 'container/signup.html')


    


