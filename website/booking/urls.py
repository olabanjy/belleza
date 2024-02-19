from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

app_name = "booking"

urlpatterns = [
    path("rooms/", all_rooms, name="rooms"),
    path("room/<room_id>/", room_details, name="room-details"),
    path("packages/", all_packages, name="packages"),
    path("package/<package_id>/", package_details, name="package-details"),
    #####
    path("check_availabilty/", check_availabilty, name="check_availabilty"),
    path("cart/", cart, name="cart"),

]