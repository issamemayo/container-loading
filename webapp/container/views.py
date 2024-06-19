import matplotlib
import matplotlib.pyplot as plt
import json
import plotly.io as pio
from django.forms import formset_factory
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import BoxOrderFormSet,BoxOrderForm
from .models import BoxData
from .algorithm import Container, Box, best_fit_decreasing, visualize_containers,visualize_containers_matplot

# Create your views here.
def index(request):
    BoxOrderFormSet = formset_factory(BoxOrderForm, extra=1, can_delete=True)

    if request.method == 'POST':
        if 'add_box' in request.POST:
            extra_forms = int(request.POST.get('extra_forms', 1))
            formset = BoxOrderFormSet(request.POST, prefix='boxes')
            if formset.is_valid():
                formset.extra = extra_forms + 1
                formset = BoxOrderFormSet(initial=formset.cleaned_data, prefix='boxes')
        else:
            formset = BoxOrderFormSet(request.POST, prefix='boxes')
            if formset.is_valid():
                # Process the formset data
                box_orders = []
                for form in formset:
                    if form.cleaned_data:
                        sku_name = form.cleaned_data.get('sku_name')
                        quantity = form.cleaned_data.get('quantity')
                        if sku_name and quantity:
                            box_orders.append({'sku_name': sku_name, 'quantity': quantity})
                
                # Generate the boxes based on the form data
                boxes = []
                for order in box_orders:
                    box_data = BoxData.objects.get(sku_name=order['sku_name'])
                    for _ in range(order['quantity']):
                        boxes.append(Box(box_data.length/10, box_data.breadth/10, box_data.height/10, box_data.sku_name))
                
                # Set up the containers
                initial_container_size = (100, 100, 100)
                containers = [Container(*initial_container_size)]

                if not best_fit_decreasing(containers, boxes):
                    error_message = "Error: No valid arrangement of boxes found."
                    return render(request, 'container/index.html', {'formset': formset, 'box_orders': box_orders, 'error_message': error_message})

                # Generate Plotly JSON data for each container
                graph_json = []
                for container in containers:
                    fig = visualize_containers([container])
                    graph_json.append(fig.to_json())

                return render(request, 'container/index.html', {'formset': formset, 'box_orders': box_orders, 'graph_json': graph_json})

    else:
        formset = BoxOrderFormSet(prefix='boxes')

    return render(request, 'container/index.html', {'formset': formset})

    
def add_box(request):
    if request.method == 'POST':
        formset = BoxOrderFormSet(request.POST)
    else:
        formset = BoxOrderFormSet()
    return render(request, 'container/index.html', {'formset': formset})

def login_view(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user=authenticate(request,username=username, password=password)
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse("container:index"))
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




    


