from django.urls import path
from . import views

app_name="container"

urlpatterns=[
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("pallet",views.pallet_view, name="pallet"),
    path("cargo", views.cargo_view, name="cargo")

]