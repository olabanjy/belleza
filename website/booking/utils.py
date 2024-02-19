import json
from .models import *
from booking.models import Room, Order, OrderItem, Package

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from ums.models import Profile
from datetime import datetime


def cookieCart(request):
    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}
        print("CART:", cart)

    items = []
    order = {"get_total": 0, "get_cart_items": 0}
    cartItems = order["get_cart_items"]

    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:

            cartItems += cart[i]["quantity"]
            if cart[i]["productType"] == "room":
                product = Room.objects.get(id=i)
                total = product.price * cart[i]["quantity"]
                product_price = product.price
            elif cart[i]["productType"] == "package":
                product = Package.objects.get(id=i)

                if cart[i]["options"] == "day_weekday":
                    total = product.day_weekday_price * cart[i]["quantity"]
                    product_price = product.day_weekday_price
                elif cart[i]["options"] == "day_weekend":
                    total = product.day_weekend_price * cart[i]["quantity"]
                    product_price = product.day_weekend_price
                elif cart[i]["options"] == "overnight_weekday":
                    total = product.overnight_weekday_price * cart[i]["quantity"]
                    product_price = product.overnight_weekday_price
                elif cart[i]["options"] == "overnight_weekend":
                    total = product.overnight_weekend_price * cart[i]["quantity"]
                    product_price = product.overnight_weekend_price

            order["get_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            bookedDates = cart[i]["dateBooked"]
            check_in_date, check_out_date = bookedDates.split("-")

            item = {
                "id": product.id,
                "type": cart[i]["productType"],
                "item": {
                    "id": product.id,
                    "name": product.title,
                    "price": product_price,  # product.price,
                    "displayImagePath": (
                        product.thumbnail
                        if cart[i]["productType"] == "room"
                        else product.banner
                    ),
                    "type": cart[i]["productType"],
                    "check_in": datetime.strptime(check_in_date.strip(), "%d/%m/%Y"),
                    "check_out": datetime.strptime(check_out_date.strip(), "%d/%m/%Y"),
                },
                "quantity": cart[i]["quantity"],
                "get_final_price": total,
            }
            items.append(item)

        except Exception as e:
            print(e)
            raise e

    return {"cartItems": cartItems, "order": order, "items": items}


def cartData(request):
    cookieData = cookieCart(request)
    cartItems = cookieData["cartItems"]
    order = cookieData["order"]
    items = cookieData["items"]

    return {"cartItems": cartItems, "order": order, "items": items}


def guestOrder(request, data):
    first_name = data["userInfo"]["first_name"]
    last_name = data["userInfo"]["last_name"]
    phone = data["userInfo"]["phone"]
    user_email = data["userInfo"]["email"]

    # billing_address = data["billingInfo"]["billing_address"]

    # billing_city = data["billingInfo"]["billing_city"]
    # billing_state = data["billingInfo"]["billing_state"]

    cookieData = cookieCart(request)
    items = cookieData["items"]

    user_password = f"{user_email.split('@', 1)[0]}{1234}"
    # User = get_user_model
    try:
        the_user = User.objects.get(email=user_email)

    except User.DoesNotExist:
        the_user, created = User.objects.get_or_create(
            username=str(user_email.split("@", 1)[0]),
            defaults={"email": user_email, "password": make_password(user_password)},
        )
        # send an email to the user here!

    the_profile, created = Profile.objects.get_or_create(user=the_user)

    # send welcome email to user

    # guest_billing_address = Address.objects.create(
    #     user=the_profile,
    #     street_address=billing_address,
    #     # apartment_address=billing_address2,
    #     city=billing_city,
    #     state=billing_state,
    #     address_type="B",
    # )

    order = Order.objects.create(
        user=the_profile,
        ordered=False,
    )
    order.save()

    for product in items:
        if product["type"] == "room":
            the_product = Room.objects.get(id=product["id"])
        elif product["type"] == "package":
            the_product = Package.objects.get(id=product["id"])
        order_item, created = OrderItem.objects.get_or_create(
            content_object=the_product,
            item_type=(
                choices.ProductType.Room.value
                if product["type"] == "room"
                else choices.ProductType.Package.value
            ),
            user=the_profile,
            quantity=product["quantity"],
            ordered=False,
            check_in=product["check_in"],
            check_out=product["check_out"],
        )
        order.items.add(order_item)
    return the_profile, order


def wee_day(date):
    import pandas as pd

    dte = pd.to_datetime(date, dayfirst=True)
    print(dte.isoweekday())
    if dte.isoweekday() < 6:
        return True
    else:
        return False
