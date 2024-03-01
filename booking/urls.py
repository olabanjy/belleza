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
    path(
        "render_available_room_count/",
        render_available_room_count,
        name="render-available-room-count",
    ),
    path("check_availabilty/", check_availabilty, name="check_availabilty"),
    path("cart/", cart, name="cart"),
    path("remove_item/", remove_item, name="remove-item"),
    path("test_api/", test_api, name="test-api"),
    path("checkout/", checkout, name="checkout"),
    path("process_checkout/", process_checkout, name="process-checkout"),
    path("payment_view/<profile_id>/<order_id>/", payment_view, name="payment-view"),
    path(
        "process_paystack_payment/",
        process_paystack_payment,
        name="process-paystack-payment",
    ),
    path(
        "process_flutterwave_payment/",
        process_flutterwave_payment,
        name="process-flutterwave-payment",
    ),
]
