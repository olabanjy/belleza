import json
from .models import *

from booking.models import Room, Order, OrderItem, Package, BookingInfo

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from ums.models import Profile
from datetime import datetime

from . import choices

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

            check_in_dt, check_out_dt = datetime.strptime(
                check_in_date.strip(), "%d/%m/%Y"
            ), datetime.strptime(check_out_date.strip(), "%d/%m/%Y")

            if cart[i]["productType"] == "room":
                product = Room.objects.get(id=i)
                rate = (check_out_dt - check_in_dt).days
                total = product.price * cart[i]["quantity"] * rate + product.caution_fee
                product_price = product.price

                product_check_in = datetime.strptime(
                    f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
                )
                product_check_out = datetime.strptime(
                    f"{check_out_date.strip()} 10:00:00", "%d/%m/%Y %H:%M:%S"
                )

            elif cart[i]["productType"] == "package":

                product = Package.objects.get(id=i)

                fetch_rate = (check_out_dt - check_in_dt).days

                rate = fetch_rate if fetch_rate > 0 else 1

                if cart[i]["period"] == "day":

                    total = (
                        product.day_price * cart[i]["quantity"] * rate
                        + product.caution_fee
                    )
                    product_price = product.day_price
                    price_option = choices.PackagePriceOption.Day.value

                    product_check_in = datetime.strptime(
                        f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
                    )
                    product_check_out = datetime.strptime(
                        f"{check_out_date.strip()} 19:00:00", "%d/%m/%Y %H:%M:%S"
                    )

                elif cart[i]["period"] == "night":
                    price_option = choices.PackagePriceOption.Overnight.value
                    total = (
                        product.overnight_price * cart[i]["quantity"] * rate
                        + product.caution_fee
                    )
                    product_price = product.overnight_price

                    product_check_in = datetime.strptime(
                        f"{check_in_date.strip()} 12:00:00", "%d/%m/%Y %H:%M:%S"
                    )
                    product_check_out = datetime.strptime(
                        f"{check_out_date.strip()} 10:00:00", "%d/%m/%Y %H:%M:%S"
                    )
            order["get_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                "id": product.id,
                "type": cart[i]["productType"],
                "item": {
                    "id": product.id,
                    "name": product.title,
                    "price": product_price,  # product.price,
                    "caution_fee": product.caution_fee,
                    "rate": rate,
                    "displayImagePath": (
                        product.thumbnail
                        if cart[i]["productType"] == "room"
                        else product.banner
                    ),
                    "type": cart[i]["productType"],
                    "price_option": (
                        price_option if cart[i]["productType"] == "package" else None
                    ),
                    "check_in": product_check_in,
                    "check_out": product_check_out,
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

    clientType = data["clientType"]

    if clientType == "personal":
        user_email = data["bookingData"]["email"]
        first_name = data["bookingData"]["first_name"]
        last_name = data["bookingData"]["last_name"]
        phone = data["bookingData"]["phone"]
        address = data["bookingData"]["address"]
        other_phone = data["bookingData"]["other_phone"]

        user_password = f"{user_email.split('@', 1)[0]}{1234}"
        # User = get_user_model
        try:
            the_user = User.objects.get(email=user_email)

        except User.DoesNotExist:
            the_user, created = User.objects.get_or_create(
                username=str(user_email.split("@", 1)[0]),
                defaults={
                    "email": user_email,
                    "password": make_password(user_password),
                },
            )
            # send an email to the user here!

        the_profile, created = Profile.objects.get_or_create(user=the_user)

        bookingInfo = BookingInfo.objects.create(
            user=the_profile,
            phone=phone,
            full_name=f"{first_name} {last_name}",
            other_phone=other_phone,
            address=address,
            client_type=choices.ClientType.Personal.value,
        )

        order = Order.objects.create(
            user=the_profile, ordered=False, booking_info=bookingInfo
        )

    elif clientType == "corporate":
        company_name = data["bookingData"]["company_name"]
        user_email = data["bookingData"]["company_email"]
        company_phone_number = data["bookingData"]["company_phone_number"]
        company_other_phone = data["bookingData"]["company_other_phone"]
        company_address = data["bookingData"]["company_address"]
        company_nature = data["bookingData"]["company_nature"]
        number_of_guests = data["bookingData"]["number_of_guests"]
        company_representative = data["bookingData"]["company_representative"]

        user_password = f"{user_email.split('@', 1)[0]}{1234}"
        try:
            the_user = User.objects.get(email=user_email)

        except User.DoesNotExist:
            the_user, created = User.objects.get_or_create(
                username=str(user_email.split("@", 1)[0]),
                defaults={
                    "email": user_email,
                    "password": make_password(user_password),
                },
            )

        the_profile, created = Profile.objects.get_or_create(user=the_user)

        bookingInfo = BookingInfo.objects.create(
            user=the_profile,
            phone=company_phone_number,
            company_name=company_name,
            other_phone=company_other_phone,
            address=company_address,
            nature_of_business=company_nature,
            number_of_guests=int(number_of_guests),
            corporate_rep=company_representative,
            client_type=choices.ClientType.Personal.value,
        )

        order = Order.objects.create(
            user=the_profile, ordered=False, booking_info=bookingInfo
        )

    cookieData = cookieCart(request)
    items = cookieData["items"]

    # send welcome email to user

    for product in items:
        if product["type"] == "room":
            the_product = Room.objects.get(id=product["id"])
            product_type = ContentType.objects.get_for_model(Room)
        elif product["type"] == "package":
            the_product = Package.objects.get(id=product["id"])
            product_type = ContentType.objects.get_for_model(Package)
            # check for extra guests

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

        # check for extra guests
        if (
            product["type"] == "package"
            and order.booking_info.number_of_guests > the_product.nos_of_guest
        ):
            extra_guests = (
                order.booking_info.number_of_guests - the_product.nos_of_guest
            )
            order_item.extra_guest = extra_guests
            order_item.save()

    return the_profile, order


def wee_day(date):
    import pandas as pd

    dte = pd.to_datetime(date, dayfirst=True)
    print(dte.isoweekday())
    if dte.isoweekday() < 6:
        return True
    else:
        return False


def handle_complimentary_booking(user_id, check_in, check_out, package):
    the_prof = Profile.objects.get(id=user_id)
    room_product_type = ContentType.objects.get_for_model(Room)
    if package == "silver":
        deluxe_room = Room.objects.filter(slug="deluxe-room").first()
        OrderItem.objects.get_or_create(
            user=the_prof,
            content_type=room_product_type,
            object_id=deluxe_room.id,
            item_type=choices.ProductType.Room.value,
            ordered=True,
            check_in=check_in,
            check_out=check_out,
            quantity=5,
            is_complimentary=True,
        )

        # book 3 full poolview
        full_poolview_room = Room.objects.filter(slug="full-poolview").first()
        OrderItem.objects.get_or_create(
            user=the_prof,
            content_type=room_product_type,
            object_id=full_poolview_room.id,
            item_type=choices.ProductType.Room.value,
            ordered=True,
            check_in=check_in,
            check_out=check_out,
            quantity=3,
            is_complimentary=True,
        )

        # book 2 oceanview
        ocean_view = Room.objects.filter(slug="ocean-view").first()
        OrderItem.objects.get_or_create(
            user=the_prof,
            content_type=room_product_type,
            object_id=ocean_view.id,
            item_type=choices.ProductType.Room.value,
            ordered=True,
            check_in=check_in,
            check_out=check_out,
            quantity=2,
            is_complimentary=True,
        )
    elif package == "bronze":
        # book two fullpoolview
        full_poolview_room = Room.objects.filter(slug="full-poolview").first()
        OrderItem.objects.get_or_create(
            user=the_prof,
            content_type=room_product_type,
            object_id=full_poolview_room.id,
            item_type=choices.ProductType.Room.value,
            ordered=True,
            check_in=check_in,
            check_out=check_out,
            quantity=2,
            is_complimentary=True,
        )
    elif package == "gold":
        # book all rooms
        all_rooms = Room.objects.all()
        for room in all_rooms:
            OrderItem.objects.get_or_create(
                user=the_prof,
                content_type=room_product_type,
                object_id=room.id,
                item_type=choices.ProductType.Room.value,
                ordered=True,
                check_in=check_in,
                check_out=check_out,
                quantity=room.availability,
                is_complimentary=True,
            )
    print("done with complementary bookings")
