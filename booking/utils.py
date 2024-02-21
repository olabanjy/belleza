import json
from .models import *
from booking.models import Room, Order, OrderItem, Package

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from ums.models import Profile
from datetime import datetime

from django.contrib.contenttypes.models import ContentType


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
            bookedDates = cart[i]["dateBooked"]
            check_in_date, check_out_date = bookedDates.split("-")

            if cart[i]["productType"] == "room":
                product = Room.objects.get(id=i)
                total = product.price * cart[i]["quantity"]
                product_price = product.price
            elif cart[i]["productType"] == "package":
                product = Package.objects.get(id=i)

                check_weekday = wee_day(check_in_date)

                if check_weekday == True and cart[i]["period"] == "day":
                    total = product.day_weekday_price * cart[i]["quantity"]
                    product_price = product.day_weekday_price
                    price_option = choices.PackagePriceOption.DayWeekday.value

                elif check_weekday == True and cart[i]["period"] == "night":
                    price_option = choices.PackagePriceOption.OvernightWeekday.value
                    total = product.overnight_weekday_price * cart[i]["quantity"]
                    product_price = product.overnight_weekday_price

                elif check_weekday == False and cart[i]["period"] == "day":
                    price_option = choices.PackagePriceOption.DayWeekend.value
                    total = product.day_weekend_price * cart[i]["quantity"]
                    product_price = product.day_weekend_price

                elif check_weekday == False and cart[i]["period"] == "night":
                    price_option = choices.PackagePriceOption.OvernightWeekend.value

                    total = product.overnight_weekend_price * cart[i]["quantity"]
                    product_price = product.overnight_weekend_price

            order["get_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

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
                    "price_option": (
                        price_option if cart[i]["productType"] == "package" else None
                    ),
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
    the_profile.first_name = first_name
    the_profile.last_name = last_name
    the_profile.phone = phone

    the_profile.save()

    # send welcome email to user

    order = Order.objects.create(
        user=the_profile,
        ordered=False,
    )
    order.save()

    for product in items:

        if product["type"] == "room":
            the_product = Room.objects.get(id=product["id"])
            product_type = ContentType.objects.get_for_model(Room)
        elif product["type"] == "package":
            the_product = Package.objects.get(id=product["id"])
            product_type = ContentType.objects.get_for_model(Package)
        order_item, created = OrderItem.objects.get_or_create(
            content_type=product_type,
            object_id=the_product.id,
            item_type=(
                choices.ProductType.Room.value
                if product["type"] == "room"
                else choices.ProductType.Package.value
            ),
            user=the_profile,
            quantity=product["quantity"],
            package_price_option=(
                product["item"]["price_option"]
                if product["type"] == "package"
                else None
            ),
            ordered=False,
            check_in=product["item"]["check_in"],
            check_out=product["item"]["check_out"],
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