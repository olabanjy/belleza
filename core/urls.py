from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

app_name = "core"

urlpatterns = [
    path("", homepage, name="home"),
    path("about/", about, name="about"),
    path("contact-us/", contact_us, name="contact-us"),
    path("policy/", policy, name="policy"),
    path("t&c/", terms_and_condition, name="terms"),
    path("menu/", menu, name="menu"),
    path("polo-arena/", polo_arena, name="polo_arena"),
]
