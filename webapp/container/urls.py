from django.urls import path
from . import views

app_name="container"

urlpatterns=[
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("addbox",views.add_box,name="add_box")
]