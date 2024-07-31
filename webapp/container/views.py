import plotly.graph_objects as go
import plotly.io as pio
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import PalletForm, CargoForm, BoxTypeFormSet
from .pallet_algocorrugation import Pallet, Box, fill_pallet, plot_pallet_plotly,report,adjust_pallet_height
from .container_algo import BoxType,Container,render_plotly_plot,reportcargo

# Create your views here

def index(request):

    if request.method == 'POST':
        return "hi"


    return render(request, 'container/index.html')

def pallet_view(request):
    plot_div = None
    text=""
    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            box_data = form.cleaned_data['box']
            box_length = box_data.length
            box_width = box_data.breadth
            box_height = box_data.height
            box_weight=box_data.net_weight
            box_crushing_strength=box_data.crushing_strength
            tolerance_limit=form.cleaned_data['tolerance_limit']
            pallet_length = form.cleaned_data['pallet_length']
            pallet_width = form.cleaned_data['pallet_breadth']
            pallet_height = form.cleaned_data['pallet_height']

            # Create Box and Pallet objects
            box = Box(box_length+tolerance_limit, box_width+tolerance_limit, box_height+tolerance_limit,box_weight,box_data.sku_name,box_crushing_strength)
            pallet = Pallet(pallet_length, pallet_width, pallet_height)

            # Fill pallet and get the optimized pallet
            optimized_pallet = fill_pallet(pallet, box, True, Pallet(pallet_length, pallet_width, pallet_height))
            adjusted_pallet=adjust_pallet_height(optimized_pallet,box)


            fig = plot_pallet_plotly(adjusted_pallet, box)
            text=report(adjusted_pallet,box)
            print(text)
            plot_div = fig.to_html(full_html=False)  # Convert the figure to HTML for embedding in the template
    else:
        form = PalletForm()

    return render(request, 'container/pallet.html', {'form': form, 'plot_div': plot_div, 'text': text})

def cargo_view(request):
    plot_div = None
    text=""
    if request.method == 'POST':
        form = BoxTypeFormSet(request.POST)
        truck_form = CargoForm(request.POST)  
        
        if form.is_valid() and truck_form.is_valid(): #Clean and expand data before calculations
            truck_data = truck_form.cleaned_data['truck_type']
            truck_length = truck_data.length
            truck_breadth = truck_data.breadth
            truck_height = truck_data.height
            max_weight=truck_form.cleaned_data['max_weight']
            tolerance_limit=truck_form.cleaned_data['tolerance_limit']

          
            box_data = form.cleaned_data
            quantities_dict = {}

            for form_data in box_data:
                box_type = form_data['box_type']
                number = form_data['number']
                
                box_element=BoxType([box_type.length+tolerance_limit,box_type.breadth+tolerance_limit,box_type.height+tolerance_limit],[0,0,1],box_type.net_weight, box_type.sku_name)
                if box_type and number > 0:
                    quantities_dict[box_element] = number

            # Create the container with the selected box types and quantities
            container = Container([truck_length, truck_breadth, truck_height], quantities_dict,max_weight)
            container.fill_all()

            
            # Render the plot

            fig = render_plotly_plot(container)
            plot_div = pio.to_html(fig, full_html=False)
            text=reportcargo(container)

    else:
        form = BoxTypeFormSet()
        truck_form = CargoForm()  

    return render(request, 'container/cargo.html', {
        'form': form,
        'truck_form': truck_form,
        'plot_div': plot_div,
        'text':text
    })

#Simple login auth implementation
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

#Logout auth implementation
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




    


