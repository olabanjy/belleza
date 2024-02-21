from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

app_name = "core"

urlpatterns = [
    path("", homepage, name="home"),
    path("about/", about, name="about"),
    path("contact-us/", contact_us, name="contact-us"),
]