import matplotlib
import matplotlib.pyplot as plt
import logging
import plotly.graph_objects as go
import plotly.io as pio
from django.forms import formset_factory
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import PalletForm, CargoForm, BoxTypeForm, BoxTypeFormSet
from .models import BoxData, TruckData
from .pallet_algocorrugation import Pallet, Box, fill_pallet, plot_pallet_plotly
from .container_algo import BoxType,Container,render_plotly_plot
from plotly.offline import plot
# Create your views here

logger = logging.getLogger(__name__)

def index(request):

    if request.method == 'POST':
        return "hi"


    return render(request, 'container/index.html')

def pallet_view(request):
    plot_div = None
    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            box_data = form.cleaned_data['box']
            box_length = box_data.length
            box_width = box_data.breadth
            box_height = box_data.height
            pallet_length = form.cleaned_data['pallet_length']
            pallet_width = form.cleaned_data['pallet_breadth']
            pallet_height = form.cleaned_data['pallet_height']

            # Create Box and Pallet objects
            box = Box(box_length, box_width, box_height)
            pallet = Pallet(pallet_length, pallet_width, pallet_height)

            # Fill pallet and get the optimized pallet
            optimized_pallet = fill_pallet(pallet, box, True, Pallet(pallet_length, pallet_width, pallet_height))
            print(optimized_pallet)

            # Generate Plotly figure using the function
            fig = plot_pallet_plotly(optimized_pallet, box)
            plot_div = fig.to_html(full_html=False)  # Convert the figure to HTML for embedding in the template
    else:
        form = PalletForm()

    return render(request, 'container/pallet.html', {'form': form, 'plot_div': plot_div})

def cargo_view(request):
    plot_div = None

    if request.method == 'POST':
        form = BoxTypeFormSet(request.POST)
        truck_form = CargoForm(request.POST)  
        
        if form.is_valid() and truck_form.is_valid():
            truck_data = truck_form.cleaned_data['truck_type']
            truck_length = truck_data.length
            truck_breadth = truck_data.breadth
            truck_height = truck_data.height

            # Process formset data
            box_data = form.cleaned_data
            quantities_dict = {}

            for form_data in box_data:
                box_type = form_data['box_type']
                number = form_data['number']
                if box_type and number > 0:
                    quantities_dict[box_type] = number

            # Create the container with the selected box types and quantities
            container = Container([truck_length, truck_breadth, truck_height], quantities_dict)
            container.fill_all()

            # Render the plot
            fig = render_plotly_plot(container)
            plot_div = pio.to_html(fig, full_html=False)

    else:
        form = BoxTypeFormSet()
        truck_form = CargoForm()  # Assuming you have a form for truck details

    return render(request, 'container/cargo.html', {
        'form': form,
        'truck_form': truck_form,
        'plot_div': plot_div
    })


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




    


